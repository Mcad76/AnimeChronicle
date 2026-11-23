#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeChronicle — Supervisor diario.

Comprueba que las noticias se han actualizado hoy, que TODAS tienen foto real,
que ninguna imagen es el logotipo de Google News (detección perceptual) y que
TODOS los enlaces a las páginas de noticias responden correctamente.

Sale con código 1 si algo falla, para que el workflow quede en rojo.
"""

import json
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import actualizar_noticias as gen
from PIL import Image

BASE = Path(__file__).resolve().parent
DHASH_LOGO = 0x160f0f573717330b


def dhash(imagen):
    gris = imagen.convert('L').resize((9, 8))
    pix = list(gris.get_flattened_data() if hasattr(gris, 'get_flattened_data') else gris.getdata())
    valor = 0
    for fila in range(8):
        for col in range(8):
            valor = (valor << 1) | (1 if pix[fila * 9 + col] > pix[fila * 9 + col + 1] else 0)
    return valor


def es_logo(ruta):
    try:
        return bin(dhash(Image.open(ruta)) ^ DHASH_LOGO).count('1') <= 10
    except Exception:
        return False


def estado_enlace(url):
    """Devuelve None si responde, o un texto con el error."""
    for intento in range(2):
        try:
            req = urllib.request.Request(
                url, method='HEAD', headers={'User-Agent': 'AnimeChronicle-Supervisor/1.0'})
            with urllib.request.urlopen(req, timeout=12) as resp:
                if 200 <= resp.status < 400:
                    return None
                return f'HTTP {resp.status}'
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 'HTTP 404'
            if intento == 1:
                return f'HTTP {e.code}'
        except Exception as e:
            if intento == 1:
                return str(e)[:80]
    return None


def comprobar_enlaces(noticias):
    """Comprueba por HTTP que todas las páginas estáticas siguen vivas."""
    urls = sorted({gen.url_para(n) for n in noticias})
    if not urls:
        return [], 0
    fallos = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for url, error in zip(urls, pool.map(estado_enlace, urls)):
            if error:
                fallos.append(f'{url}: {error}')
    return fallos, len(urls)


def guardar_informe(informe):
    """Escribe datos/supervision.json para que MCad Hub pueda mostrarlo."""
    ruta = BASE / 'datos' / 'supervision.json'
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + '\n',
                    encoding='utf-8')


def main():
    errores = []
    avisos = []

    historico = BASE / 'datos' / 'historico.json'
    if not historico.exists():
        guardar_informe({
            'revisado': datetime.now(timezone.utc).isoformat(),
            'resultado': 'error',
            'errores': ['no existe datos/historico.json'],
            'avisos': [],
        })
        print('FALLO: no existe datos/historico.json')
        return 1

    datos = json.loads(historico.read_text(encoding='utf-8'))
    noticias = datos.get('noticias', [])
    actualizado = datos.get('actualizado', '')
    hoy = datetime.now(timezone.utc).date().isoformat()

    if not actualizado.startswith(hoy):
        errores.append(f'la última actualización es {actualizado!r}, no de hoy ({hoy})')
    if len(noticias) < 100:
        errores.append(f'solo hay {len(noticias)} noticias')

    sin_imagen = []
    archivos_faltan = []
    logos = []
    for n in noticias:
        img = n.get('image', '')
        ident = n.get('id', '?')
        if not img:
            sin_imagen.append(ident)
            continue
        ruta = BASE / img if not Path(img).is_absolute() else Path(img)
        if not ruta.exists():
            archivos_faltan.append(f'{ident}: {img}')
        elif es_logo(ruta):
            logos.append(f'{ident}: {img}')

    if sin_imagen:
        errores.append(f'{len(sin_imagen)} noticias sin imagen')
    if archivos_faltan:
        errores.append(f'{len(archivos_faltan)} archivos de imagen ausentes: {archivos_faltan[:3]}')
    if logos:
        errores.append(f'{len(logos)} noticias con el logo de Google News: {logos[:3]}')

    js = BASE / 'js' / 'news-data.js'
    if not js.exists():
        errores.append('falta js/news-data.js')
    else:
        texto = js.read_text(encoding='utf-8')
        if texto.count('  A("') != len(noticias):
            errores.append('news-data.js no coincide con el histórico')
        if 'const TENDENCIAS' not in texto:
            errores.append('falta TENDENCIAS en news-data.js')

    paginas = list((BASE / 'noticias').glob('*.html'))
    if len(paginas) != len(noticias):
        avisos.append(f'{len(paginas)} páginas estáticas para {len(noticias)} noticias')
    for n in noticias:
        nombre = gen.slug_para(n) + '.html'
        if not (BASE / 'noticias' / nombre).exists():
            errores.append(f'falta la página local de {n.get("id", "?")}: {nombre}')
            break

    fallos_enlaces, total_enlaces = comprobar_enlaces(noticias)
    if fallos_enlaces:
        errores.append(
            f'{len(fallos_enlaces)} de {total_enlaces} enlaces fallan: {fallos_enlaces[:3]}')

    for archivo in ('index.html', 'archivo.html', 'glosario.html', 'sitemap.xml', 'robots.txt'):
        ruta = BASE / archivo
        if not ruta.exists() or ruta.stat().st_size < 40:
            errores.append(f'{archivo} ausente o vacío')

    guardar_informe({
        'revisado': datetime.now(timezone.utc).isoformat(),
        'resultado': 'error' if errores else 'ok',
        'portal': 'AnimeChronicle',
        'actualizado': actualizado,
        'actualizacion_hoy': actualizado.startswith(hoy),
        'noticias': len(noticias),
        'con_imagen': sum(1 for n in noticias if n.get('image')),
        'sin_imagen': len(sin_imagen),
        'imagenes_ausentes': len(archivos_faltan),
        'logos_google': len(logos),
        'paginas': len(paginas),
        'enlaces': {
            'total': total_enlaces,
            'fallidos': len(fallos_enlaces),
            'ejemplos': fallos_enlaces[:5],
        },
        'errores': errores,
        'avisos': avisos,
    })

    print('=== SUPERVISOR ANIMECHRONICLE ===')
    print(f'Fecha UTC: {datetime.now(timezone.utc).isoformat()}')
    print(f'Actualizado: {actualizado}')
    print(f'Noticias: {len(noticias)}')
    print(f'Con imagen: {sum(1 for n in noticias if n.get("image"))}')
    print(f'Páginas estáticas: {len(paginas)}')
    print(f'Enlaces comprobados: {total_enlaces} ({len(fallos_enlaces)} fallidos)')
    print(f'Logos de Google News detectados: {len(logos)}')
    for aviso in avisos:
        print('AVISO:', aviso)
    if errores:
        print('RESULTADO: FALLIDO')
        for e in errores:
            print('  -', e)
        return 1
    print('RESULTADO: CORRECTO')
    return 0


if __name__ == '__main__':
    sys.exit(main())
