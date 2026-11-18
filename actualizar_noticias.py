#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeChronicle — Actualizador automático de noticias de anime.

Descarga noticias reales de fuentes RSS públicas (Anime News Network,
MyAnimeList, Google News y Bing News), las clasifica por sección y género,
descarga las imágenes y regenera:

  js/news-data.js        banco de noticias que consume la portada
  datos/historico.json   histórico para no perder noticias antiguas
  noticias/*.html        una página real e indexable por noticia
  sitemap.xml / robots.txt

Uso manual:  python3 actualizar_noticias.py
"""

import os
import re
import json
import html
import time
import hashlib
import random
import urllib.request
from urllib.parse import quote, urlparse, parse_qs
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from PIL import Image

# ------------------------------------------------------------------ config
BASE = Path(__file__).resolve().parent
DATOS = BASE / 'datos'
IMGS = BASE / 'imagenes'
FONDOS = BASE / 'fondos'
JS = BASE / 'js' / 'news-data.js'
HISTORICO = DATOS / 'historico.json'
MANUALES = DATOS / 'noticias-manuales.json'
PORTADAS = DATOS / 'portadas.json'   # carátulas por franquicia (caché)
LOG = BASE / 'actualizar_noticias.log'

NOMBRE = 'AnimeChronicle'
BASE_URL = 'https://mcad76.github.io/AnimeChronicle/'
CANALES = {'telegram': '', 'whatsapp': '', 'discord': ''}

ANN = 'https://www.animenewsnetwork.com/news/rss.xml'
MAL = 'https://myanimelist.net/rss/news.xml'
GOOGLE = 'https://news.google.com/rss/search?q={q}&hl=es-ES&gl=ES&ceid=ES:es'
BING = 'https://www.bing.com/news/search?q={q}&format=rss'
UA = 'Mozilla/5.0 (compatible; AnimeChronicle/2.0; +RSS)'
TIMEOUT = 10
PAUSA = 0.15

MAX_IMAGENES = 220
DIAS_HISTORICO = 45
MAX_EN_ARCHIVO = 420
MAX_POR_GENERO = 24
TOP_N = 10

# -------- secciones de la portada --------
SECCIONES = [
    {'id': 'estrenos',     'nombre': 'Estrenos',        'color': '#ff2e88', 'kanji': '新作'},
    {'id': 'series',       'nombre': 'Series TV',       'color': '#00e5ff', 'kanji': 'アニメ'},
    {'id': 'peliculas',    'nombre': 'Películas',       'color': '#ffd23f', 'kanji': '映画'},
    {'id': 'manga',        'nombre': 'Manga y Novelas', 'color': '#a855f7', 'kanji': '漫画'},
    {'id': 'videojuegos',  'nombre': 'Videojuegos',     'color': '#39ff14', 'kanji': 'ゲーム'},
    {'id': 'eventos',      'nombre': 'Eventos y Cosplay','color': '#ff6b35', 'kanji': 'イベント'},
    {'id': 'comunidad',    'nombre': 'Comunidad',       'color': '#4d9fff', 'kanji': '仲間'},
]

# -------- pestañas (géneros). La primera es "todo" --------
GENEROS = [
    {'id': 'todos',     'nombre': 'Todo el anime'},
    {'id': 'shonen',    'nombre': 'Shōnen'},
    {'id': 'shojo',     'nombre': 'Shōjo'},
    {'id': 'isekai',    'nombre': 'Isekai'},
    {'id': 'mecha',     'nombre': 'Mecha'},
    {'id': 'fantasia',  'nombre': 'Fantasía'},
    {'id': 'accion',    'nombre': 'Acción'},
    {'id': 'romance',   'nombre': 'Romance'},
    {'id': 'comedia',   'nombre': 'Comedia'},
    {'id': 'terror',    'nombre': 'Terror'},
]

CONSULTAS_GENERO = [
    'anime {g} noticias',
    'anime {g} estreno temporada',
]

IMPORTANTES = [
    'estreno', 'estrenos', 'trailer', 'avance', 'nueva temporada', 'temporada 2',
    'pelicula', 'película', 'anuncio', 'anunciado', 'confirmado', 'adaptacion',
    'adaptación', 'estudio', 'crunchyroll', 'netflix', 'disney', 'premio',
    'ganador', 'record', 'récord', 'final', 'lanzamiento', 'fecha de estreno',
    'exclusiva', 'fallece', 'muere', 'director', 'reparto', 'secuela',
]
RUIDO = ['opinion', 'opinión', 'vota', 'encuesta', 'memes', 'donde ver',
         'dónde ver', 'top 10', 'resumen', 'curiosidades']

# Orden: las secciones más específicas primero para no etiquetar mal
DETECTAR_SECCION = [
    ('manga', ['manga', 'light novel', 'novela ligera', 'volumen', 'capítulo',
               'komi', 'one piece', 'jujutsu kaisen']),
    ('videojuegos', ['videojuego', 'videojuegos', 'gaming', 'gamer', 'consola',
                     'nintendo', 'playstation', 'xbox', 'steam', 'game']),
    ('eventos', ['convencion', 'convención', 'comic con', 'cosplay', 'festival',
                 'expo', 'evento', 'anime expo', 'salon del manga', 'japan expo']),
    ('peliculas', ['pelicula', 'película', 'movie', 'film', 'cines', 'teatro',
                   'taquilla', 'estreno en cines']),
    ('comunidad', ['comunidad', 'fans', 'fanart', 'reddit', 'debate', 'polémica',
                   'controversia', 'encuesta', 'homenaje']),
    ('estrenos', ['estreno', 'nueva serie', 'nuevo anime', 'anuncio', 'anunciado',
                  'trailer', 'avance', 'adaptación', 'adaptacion', 'secuela',
                  'confirmado', 'nueva temporada']),
    ('series', ['serie', 'series', 'anime', 'episodio', 'temporada', 'tv',
                'broadcast', 'emisión', 'emision']),
]

DETECTAR_GENERO = [
    ('shonen', ['shonen', 'shounen', 'naruto', 'one piece', 'dragon ball',
                'jujutsu', 'my hero', 'boku no hero', 'shingeki', 'attack on titan',
                'bleach', 'hunter x hunter']),
    ('shojo', ['shojo', 'shoujo', 'sailor moon', 'fruits basket', 'ouran']),
    ('isekai', ['isekai', 'reencarn', 'otro mundo', 'another world', 'tensura',
                'konosuba', 'mushoku', 're:zero', 'saved by the bell']),
    ('mecha', ['mecha', 'gundam', 'evangelion', 'robot', 'mazinger']),
    ('terror', ['terror', 'horror', 'fantasma', 'suspenso', 'yandere']),
    ('romance', ['romance', 'enamor', 'pareja', 'amor', 'noviazgo']),
    ('comedia', ['comedia', 'comedy', 'gag', 'gracioso', 'chiste', 'humor']),
    ('accion', ['accion', 'acción', 'action', 'pelea', 'batalla', 'fight']),
    ('fantasia', ['fantasia', 'fantasía', 'fantasy', 'magia', 'dragones', 'dios']),
]

# ------------------------------------------------------------------ utiles
def log(msg):
    linea = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  {msg}'
    print(linea, flush=True)
    with LOG.open('a', encoding='utf-8') as f:
        f.write(linea + '\n')


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    ultimo = None
    for intento in range(2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                time.sleep(PAUSA)
                return r.read()
        except Exception as e:
            ultimo = e
            time.sleep(0.3 + intento)
    raise ultimo


def local(tag):
    return tag.split('}')[-1].lower()


def limpiar(texto, maxlen=None):
    if not texto:
        return ''
    texto = html.unescape(texto)
    texto = re.sub(r'<[^>]+>', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    if maxlen and len(texto) > maxlen:
        texto = texto[:maxlen].rsplit(' ', 1)[0] + '…'
    return texto


def hijo_texto(item, nombre):
    for c in item:
        if local(c.tag) == nombre and c.text:
            return c.text.strip()
    return ''


def fecha_de(item):
    raw = hijo_texto(item, 'pubdate') or hijo_texto(item, 'date')
    if not raw:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def normalizar(texto):
    t = html.unescape(texto or '').lower()
    t = re.sub(r'[^a-záéíóúüñ0-9 ]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def score_keywords(texto, keywords):
    return sum(1 for k in keywords
               if re.search(r'\b' + re.escape(k) + r'\b', texto, flags=re.I))


def detectar_seccion(texto):
    t = normalizar(texto)
    for sec, palabras in DETECTAR_SECCION:
        if any(re.search(r'\b' + re.escape(p) + r'\b', t) for p in palabras):
            return sec
    return ''


def detectar_genero(texto):
    t = normalizar(texto)
    for gen, palabras in DETECTAR_GENERO:
        if any(re.search(r'\b' + re.escape(p) + r'\b', t) for p in palabras):
            return gen
    return ''


def genero_equilibrado(ident):
    """Reparte las noticias sin género detectado entre todas las pestañas."""
    opciones = [g['id'] for g in GENEROS[1:]]
    return opciones[int(hashlib.md5(ident.encode('utf-8')).hexdigest(), 16) % len(opciones)]


def cuerpo_de(item, entradilla, medio):
    crudo = ''
    for c in item:
        if local(c.tag) in ('encoded', 'content') and c.text and '<' in c.text:
            crudo = c.text
            break
    parrafos = []
    if crudo:
        for p in re.findall(r'<p[^>]*>(.*?)</p>', crudo, flags=re.S | re.I):
            t = limpiar(p, 700)
            if len(t) > 60:
                parrafos.append(t)
    if not parrafos and entradilla:
        parrafos.append(entradilla)
    if not parrafos:
        parrafos.append(f'Noticia publicada por {medio}. Consulta el artículo original para más información.')
    return parrafos[:3]


def id_para(link):
    return 'n-' + hashlib.md5(link.encode('utf-8')).hexdigest()[:11]


def medio_de(link):
    m = re.match(r'https?://(?:www\.)?([^/]+)', link)
    return m.group(1) if m else 'la fuente original'


def normalizar_link(link):
    return re.sub(r'[?#].*$', '', link).rstrip('/').lower()


def imagen_de(item):
    for c in item:
        attrs = {local(k): v for k, v in c.attrib.items()}
        url = attrs.get('url') or attrs.get('src')
        if url and url.startswith('http'):
            return url
    for c in item:
        if local(c.tag) == 'thumbnail' and (c.text or '').startswith('http'):
            return c.text.strip()
    for c in item:
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', c.text or '', flags=re.I)
        if m and m.group(1).startswith('http'):
            return m.group(1)
    return ''


def og_image(url):
    try:
        pagina = fetch(url).decode('utf-8', 'ignore')
        for patron in (r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',
                       r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']'):
            m = re.search(patron, pagina, flags=re.I)
            if m:
                return html.unescape(m.group(1))
    except Exception:
        pass
    return ''


def mejorar_url_imagen(url):
    """Pide a Googleusercontent la versión grande en lugar de la miniatura."""
    if 'googleusercontent.com' in url:
        url = re.sub(r'=[sw]\d+[^/]*$', '=w1000', url)
    return url


LOGO_GOOGLE_MD5 = 'b3e93f52c4ce6741b7a2379269d075c5'
DHASH_LOGO = 0x160f0f573717330b   # huella visual del logo de Google News


def dhash_de(imagen):
    """Huella perceptual de 64 bits, resistente a cambios de tamaño/formato."""
    try:
        gris = imagen.convert('L').resize((9, 8))
        pixeles = list(gris.getdata())
        valor = 0
        for fila in range(8):
            for col in range(8):
                valor = (valor << 1) | (1 if pixeles[fila * 9 + col] > pixeles[fila * 9 + col + 1] else 0)
        return valor
    except Exception:
        return -1


def es_logo_google(imagen):
    """True si la imagen es el logo de Google News (aunque esté reescalada)."""
    huella = dhash_de(imagen)
    return huella >= 0 and bin(huella ^ DHASH_LOGO).count('1') <= 10


def descargar_imagen(url, ident):
    url = mejorar_url_imagen(url)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=8) as r:
            ctype = (r.headers.get('Content-Type') or '').lower()
            datos = r.read(12 * 1024 * 1024)
        if not ctype.startswith('image/') or len(datos) < 1500:
            return ''
        if hashlib.md5(datos).hexdigest() == LOGO_GOOGLE_MD5:
            return ''  # Google News no trae foto: se buscará otra fuente
        imagen = Image.open(BytesIO(datos)).convert('RGB')
        if es_logo_google(imagen):
            return ''  # detectado por aspecto, aunque cambie de resolución
        imagen.thumbnail((1000, 640), Image.LANCZOS)
        salida = BytesIO()
        imagen.save(salida, 'JPEG', quality=80, optimize=True)
        nombre = ident + '.jpg'
        (IMGS / nombre).write_bytes(salida.getvalue())
        return 'imagenes/' + nombre
    except Exception as e:
        log(f'  ! imagen no descargada ({ident}): {str(e)[:80]}')
        return ''


def imagen_respaldo(sec):
    """Ilustración local del tema si la fuente no trae foto."""
    return 'fondos/fallback-' + sec + '.svg'


def termino_anilist(titulo):
    """Extrae un nombre de anime/manga razonable del titular de la noticia."""
    t = re.split(r'\s*[|·—–]\s*', titulo)[0]
    t = re.sub(r'#\w+', ' ', t)
    t = re.sub(r'^(exclusivo|estreno|nuevo|anuncio|tráiler|trailer|vía|info|confirmado)\s*:?\s*',
               '', t, flags=re.I)
    t = re.sub(r'\([^)]*\)', ' ', t)
    return limpiar(t, 60)


PISTAS_ANIME = {
    'one piece': 'One Piece', 'dragon ball': 'Dragon Ball', 'naruto': 'Naruto',
    'mecha': 'Mobile Suit Gundam', 'gundam': 'Mobile Suit Gundam',
    'isekai': 'Re:Zero kara Hajimeru Isekai Seikatsu',
    're:zero': 'Re:Zero kara Hajimeru Isekai Seikatsu',
    'shingeki': 'Shingeki no Kyojin', 'attack on titan': 'Shingeki no Kyojin',
    'jujutsu': 'Jujutsu Kaisen', 'demon slayer': 'Kimetsu no Yaiba',
    'sailor moon': 'Sailor Moon', 'pokemon': 'Pokemon',
    'five star stories': 'The Five Star Stories',
    'shonen jump': 'Shingeki no Kyojin', 'netflix': 'Kimetsu no Yaiba',
    'crunchyroll': 'Kimetsu no Yaiba', 'acción real': 'Kimetsu no Yaiba',
    'accion real': 'Kimetsu no Yaiba', 'fantasía épica': 'Shingeki no Kyojin',
}


def imagen_anilist(titulo):
    """Último recurso: carátula oficial desde la API pública de AniList."""
    buscar = termino_anilist(titulo)
    candidatos = [buscar] if len(buscar) >= 4 else []
    bajo = titulo.lower()
    candidatos += [termino for pista, termino in PISTAS_ANIME.items() if pista in bajo]

    def consultar(termino):
        for tipo in ('ANIME', 'MANGA'):
            try:
                payload = json.dumps({
                    'query': f'query ($s: String) {{ Media(search: $s, type: {tipo}) '
                             '{ coverImage { large } } }',
                    'variables': {'s': termino},
                }).encode('utf-8')
                req = urllib.request.Request(
                    'https://graphql.anilist.co', data=payload,
                    headers={'User-Agent': UA, 'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as r:
                    datos = json.loads(r.read().decode('utf-8'))
                url = (datos.get('data') or {}).get('Media', {}).get('coverImage', {}).get('large', '')
                if url:
                    return url
            except Exception:
                pass
        return ''

    for termino in candidatos:
        url = consultar(termino)
        if url:
            return url
    return ''


# ------------------------------------------------------- imágenes fiables
def detectar_franquicia(texto):
    """Devuelve la franquicia de anime de la que habla el titular."""
    t = normalizar(texto)
    for nombre, alias in FRANQUICIAS:
        if any(a in t for a in alias):
            return nombre
    for pista, termino in PISTAS_ANIME.items():
        if pista in t:
            return termino
    return ''


def cargar_portadas():
    """Descarga (una sola vez) una carátula real por franquicia y la guarda en caché."""
    portadas = {}
    if PORTADAS.exists():
        try:
            portadas = json.loads(PORTADAS.read_text(encoding='utf-8'))
        except Exception:
            portadas = {}
    faltan = [nombre for nombre, _ in FRANQUICIAS if nombre not in portadas]
    for ini in range(0, len(faltan), 8):
        chunk = faltan[ini:ini + 8]
        campos = [
            f'f{i}: Media(search: {json.dumps(n)}, type: ANIME) {{ coverImage {{ large }} }}'
            for i, n in enumerate(chunk)
        ]
        try:
            req = urllib.request.Request(
                'https://graphql.anilist.co',
                data=json.dumps({'query': 'query { ' + ' '.join(campos) + ' }'}).encode('utf-8'),
                headers={'User-Agent': UA, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=20) as r:
                datos = json.loads(r.read().decode('utf-8'))['data']
            for i, nombre in enumerate(chunk):
                url = ((datos.get(f'f{i}') or {}).get('coverImage') or {}).get('large', '')
                if url:
                    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')[:36]
                    img = descargar_imagen(url, 'portada-' + slug)
                    if img:
                        portadas[nombre] = img
            time.sleep(1.2)
        except Exception as e:
            log(f'  ! caché de portadas: {str(e)[:70]}')
    if faltan:
        PORTADAS.write_text(json.dumps(portadas, ensure_ascii=False, indent=2), encoding='utf-8')
    return portadas


def imagen_es_logo(ruta):
    try:
        ruta = Path(ruta)
        if not ruta.is_absolute():
            ruta = BASE / ruta
        return es_logo_google(Image.open(ruta))
    except Exception:
        return True


def sanitizar_imagenes(noticias):
    """Sustituye el logo de Google News por una carátula acorde a la noticia."""
    portadas = cargar_portadas()
    valores = list(portadas.values())
    arregladas = 0
    for n in noticias:
        actual = n.get('image', '')
        if actual and (BASE / actual).exists() and not imagen_es_logo(actual):
            continue
        franquicia = detectar_franquicia(n['titulo'] + ' ' + n.get('entradilla', ''))
        nueva = portadas.get(franquicia, '')
        if not nueva and valores:
            idx = int(hashlib.md5(n['titulo'].encode('utf-8')).hexdigest(), 16) % len(valores)
            nueva = valores[idx]
        if nueva and not imagen_es_logo(nueva):
            n['image'] = nueva
            arregladas += 1
    if arregladas:
        log(f'Imágenes: se sustituyeron {arregladas} fotos no válidas (logo de Google/ausentes)')
    return arregladas


# ------------------------------------------------------------------ RSS
def parsear_feed(url, forzar_sec=None, forzar_gen=None, origen='generic'):
    salida = []
    try:
        texto = fetch(url).decode('utf-8', 'ignore')
        texto = ''.join(c for c in texto if ord(c) > 31 or c in '\n\r\t')
        root = ET.fromstring(texto.encode('utf-8'))
    except Exception as e:
        log(f'  ! feed {url[:70]}: {str(e)[:90]}')
        return salida

    for item in root.findall('.//item'):
        titulo = limpiar(hijo_texto(item, 'title'), 190)
        enlace = hijo_texto(item, 'link')
        if not titulo or not enlace:
            continue
        medio = limpiar(hijo_texto(item, 'source'), 60) or medio_de(enlace)

        if origen == 'bing':
            enlace = parse_qs(urlparse(enlace).query).get('url', [enlace])[0]
            if titulo.endswith(' - ' + medio):
                titulo = titulo[:-(len(medio) + 3)].strip()

        if origen == 'google' and titulo.endswith(' - ' + medio):
            titulo = titulo[:-(len(medio) + 3)].strip()

        entradilla = limpiar(hijo_texto(item, 'description'), 250) or titulo
        ident = id_para(enlace)
        sec = forzar_sec or detectar_seccion(titulo + ' ' + entradilla) or 'series'
        gen = forzar_gen or detectar_genero(titulo + ' ' + entradilla) or genero_equilibrado(ident)

        salida.append({
            'id': ident,
            'sec': sec,
            'genero': gen,
            'slot': 0,
            'titulo': titulo,
            'entradilla': entradilla,
            'cuerpo': cuerpo_de(item, entradilla, medio),
            'autor': limpiar(hijo_texto(item, 'creator'), 60) or 'Redacción AnimeChronicle',
            'fecha': fecha_de(item),
            'image': '',
            'link': enlace,
            'medio': medio,
            'viral': 0,
            '_score': 0,
            '_imgurl': imagen_de(item),
            '_fuentes': 1,
        })
    return salida


# ------------------------------------------------------------------ ranking
def peso_titulo(titulo):
    t = normalizar(titulo)
    plus = sum(1 for k in IMPORTANTES if re.search(r'\b' + re.escape(k) + r'\b', t))
    minus = sum(1 for k in RUIDO if re.search(r'\b' + re.escape(k) + r'\b', t))
    return max(-2, min(5, plus - minus))


def calcular_viral(n, menciones, ahora):
    try:
        f = datetime.fromisoformat(n['fecha'])
        if f.tzinfo is None:
            f = f.replace(tzinfo=timezone.utc)
    except Exception:
        f = ahora
    horas = max(0.0, (ahora - f).total_seconds() / 3600)
    frescura = max(0.0, 1 - horas / 72)
    fuentes = min(n.get('_fuentes', 1), 4) / 4
    mencion = min(menciones.get(normalizar(n['titulo']), 1), 3) / 3
    peso = (peso_titulo(n['titulo']) + 2) / 7
    imagen = 0.05 if n.get('image') else 0
    return round(0.28 * frescura + 0.17 * fuentes + 0.36 * peso +
                 0.14 * mencion + imagen, 4)


# ------------------------------------------------------------------ datos
def cargar_historico():
    if HISTORICO.exists():
        try:
            datos = json.loads(HISTORICO.read_text(encoding='utf-8'))
            for n in datos.get('noticias', []):
                n.setdefault('genero', 'todos')
            return datos
        except Exception as e:
            log(f'! histórico corrupto, se empieza de cero: {e}')
    return {'actualizado': '', 'noticias': [], 'top': []}


def cargar_manuales():
    if not MANUALES.exists():
        return []
    try:
        raw = json.loads(MANUALES.read_text(encoding='utf-8'))
    except Exception as e:
        log(f'! noticias-manuales.json corrupto, se ignoran: {e}')
        return []
    secs = {s['id'] for s in SECCIONES}
    gens = {g['id'] for g in GENEROS}
    salida = []
    for m in raw.get('noticias', []):
        titulo = limpiar(m.get('titulo', ''), 190)
        if not titulo:
            continue
        sec = m.get('sec', 'estrenos')
        if sec not in secs:
            sec = 'estrenos'
        gen = m.get('genero', 'todos')
        if gen not in gens:
            gen = 'todos'
        ident = m.get('id') or ('m-' + hashlib.md5(titulo.encode('utf-8')).hexdigest()[:11])
        cuerpo = [limpiar(p, 700) for p in m.get('cuerpo', [])]
        cuerpo = [p for p in cuerpo if p]
        if not cuerpo:
            cuerpo = [limpiar(m.get('entradilla', ''), 250) or titulo]
        salida.append({
            'id': ident, 'sec': sec, 'genero': gen, 'slot': 0,
            'titulo': titulo,
            'entradilla': limpiar(m.get('entradilla', ''), 250) or titulo,
            'cuerpo': cuerpo[:3],
            'autor': limpiar(m.get('autor', ''), 60) or 'Redacción AnimeChronicle',
            'fecha': m.get('fecha') or datetime.now(timezone.utc).isoformat(),
            'image': m.get('image') or imagen_respaldo(sec),
            'link': m.get('link', ''),
            'medio': limpiar(m.get('medio', ''), 60) or 'Redacción propia',
            'viral': 0,
        })
    return salida


# Franquicias usadas para el radar de "lo más visto"
FRANQUICIAS = [
    ('One Piece', ['one piece', 'luffy', 'zoro', 'nami']),
    ('Dragon Ball', ['dragon ball', 'goku', 'vegeta', 'gohan']),
    ('Naruto / Boruto', ['naruto', 'boruto', 'sasuke', 'kakashi']),
    ('Demon Slayer', ['demon slayer', 'kimetsu', 'tanjiro', 'nezuko', 'zenitsu']),
    ('Jujutsu Kaisen', ['jujutsu', 'gojo', 'yuji itadori', 'sukuna']),
    ('Attack on Titan', ['attack on titan', 'shingeki', 'eren jaeger', 'aot']),
    ('My Hero Academia', ['my hero', 'boku no hero', 'deku', 'all might', 'bakugo']),
    ('Chainsaw Man', ['chainsaw man', 'denji', 'makima', 'power']),
    ('Spy x Family', ['spy x family', 'anya', 'loid', 'yor forger']),
    ('Pokémon', ['pokemon', 'pokémon', 'pikachu', 'ash ketchum']),
    ('Gundam', ['gundam', 'mobile suit']),
    ('Neon Genesis Evangelion', ['evangelion', 'evangelion', 'shinji']),
    ('Sailor Moon', ['sailor moon', 'usagi']),
    ('Fullmetal Alchemist', ['fullmetal alchemist', 'edward elric', 'alphonse']),
    ('Bleach', ['bleach', 'ichigo', 'rukia', 'bankai']),
    ('Hunter x Hunter', ['hunter x hunter', 'gon freecss', 'killua']),
    ('Death Note', ['death note', 'light yagami', 'ryuk']),
    ('Code Geass', ['code geass', 'lelouch']),
    ('Steins;Gate', ['steins gate', 'steins;gate', 'okabe']),
    ('Fairy Tail', ['fairy tail', 'natsu', 'lucy heartfilia']),
    ('Black Clover', ['black clover', 'asta', 'yuno']),
    ('Seven Deadly Sins', ['seven deadly sins', 'meliodas']),
    ('Solo Leveling', ['solo leveling', 'sung jin woo']),
    ('That Time I Got Reincarnated as a Slime', ['tensura', 'rimuru']),
    ('Re:Zero', ['re:zero', 're zero', 'subaru']),
    ('KonoSuba', ['konosuba', 'kazuma']),
    ('Mushoku Tensei', ['mushoku', 'rudeus']),
    ('Frieren', ['frieren', 'sousou no frieren']),
    ('Oshi no Ko', ['oshi no ko', 'ai hoshino', 'aqua']),
    ('Blue Lock', ['blue lock', 'isagi']),
    ('Haikyuu', ['haikyuu', 'hinata shoyo', 'kageyama']),
    ('JoJo', ['jojo', 'bizarre adventure', 'jotaro']),
    ('One Punch Man', ['one punch man', 'saitama', 'genos']),
    ('Mob Psycho 100', ['mob psycho', 'shigeo']),
    ('Cyberpunk: Edgerunners', ['cyberpunk', 'edgerunners', 'lucy']),
    ('Berserk', ['berserk', 'guts', 'griffith']),
    ('Vinland Saga', ['vinland saga', 'thorfinn']),
    ('Your Name', ['your name', 'kimi no na wa', 'taki']),
    ('Studio Ghibli', ['ghibli', 'spirited away', 'totoro', 'princess mononoke']),
    ('Kill la Kill', ['kill la kill', 'ryuko']),
    ('Dorohedoro', ['dorohedoro']),
    ('Ranking of Kings', ['ranking of kings', 'bojji']),
    ('Komatsuna', ['komi san', 'komi-san']),
]

DOMINIOS_ES = ('.es', 'espinof', 'vidaextra', 'xataka', 'hobbyconsolas',
               '3djuegos', 'meristation', 'areajugones', 'elmundo', 'abc.',
               'rtve', 'lavanguardia', '20minutos', 'multianime', 'kudasai',
               'crunchyroll.com/es', 'animeymanga')


def generar_tendencias(noticias):
    """Radar de franquicias más mencionadas, en España y a nivel mundial."""
    def es_de_espana(n):
        medio = (n.get('medio') or '').lower()
        return any(d in medio for d in DOMINIOS_ES)

    def ranking(lista):
        conteo = {}
        for n in lista:
            texto = normalizar(n['titulo'] + ' ' + n.get('entradilla', ''))
            for nombre, alias in FRANQUICIAS:
                if any(a in texto for a in alias):
                    if nombre not in conteo:
                        conteo[nombre] = {'nombre': nombre, 'noticias': 0, 'mejor': n}
                    conteo[nombre]['noticias'] += 1
                    if (n.get('viral', 0) > conteo[nombre]['mejor'].get('viral', 0)):
                        conteo[nombre]['mejor'] = n
        items = sorted(conteo.values(),
                       key=lambda x: (x['noticias'], x['mejor'].get('viral', 0)),
                       reverse=True)[:8]
        # Si faltan entradas, se completan con las noticias más virales
        usados = {x['nombre'] for x in items}
        for n in sorted(lista, key=lambda x: x.get('viral', 0), reverse=True):
            if len(items) >= 8:
                break
            nombre = limpiar(n['titulo'], 34)
            if nombre in usados:
                continue
            items.append({'nombre': nombre, 'noticias': 1, 'mejor': n})
            usados.add(nombre)
        return [{
            'nombre': x['nombre'],
            'noticias': x['noticias'],
            'titulo': x['mejor']['titulo'],
            'image': x['mejor'].get('image', ''),
            'url': url_para(x['mejor']),
        } for x in items]

    return {
        'es': ranking([n for n in noticias if es_de_espana(n)]),
        'mundo': ranking(noticias),
    }


def escribir_si_cambia(ruta, contenido):
    """Escribe solo si el contenido cambió: evita reescribir cientos de archivos."""
    try:
        if ruta.exists() and ruta.read_text(encoding='utf-8') == contenido:
            return False
    except Exception:
        pass
    ruta.write_text(contenido, encoding='utf-8')
    return True


def guardar_historico(datos):
    DATOS.mkdir(parents=True, exist_ok=True)
    tmp = HISTORICO.with_suffix('.tmp')
    tmp.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, HISTORICO)


def jstr(s):
    return json.dumps(s or '', ensure_ascii=False)


# ------------------------------------------------------------------ salidas
def generar_js(historico):
    JS.parent.mkdir(parents=True, exist_ok=True)
    secciones_js = ',\n'.join('  ' + json.dumps(s, ensure_ascii=False) for s in SECCIONES)
    generos_js = ',\n'.join('  ' + json.dumps(g, ensure_ascii=False) for g in GENEROS)
    lineas = [
        '/* ============================================================',
        '   ANIMECHRONICLE — Banco de noticias',
        '   Generado automáticamente por actualizar_noticias.py.',
        '   NO EDITAR A MANO: tus cambios se pierden en la próxima actualización.',
        '   ============================================================ */',
        '',
        'const ACTUALIZADO = ' + jstr(historico.get('actualizado', '')) + ';',
        '',
        'const SECCIONES = [', secciones_js, '];',
        '',
        'const GENEROS = [', generos_js, '];',
        '',
        'const TENDENCIAS = ' + json.dumps(historico.get('tendencias', {'es': [], 'mundo': []}),
                                          ensure_ascii=False) + ';',
        '',
        "const A = (id, sec, genero, slot, titulo, entradilla, cuerpo,",
        "          autor = 'Redacción', fecha = '', image = '', link = '',",
        "          medio = '', viral = 0, url = '') => ({",
        '  id, sec, genero, slot, titulo, entradilla, cuerpo, autor, fecha,',
        '  image, link, medio, viral, url',
        '});',
        '',
        'const NOTICIAS = [',
    ]
    for sec in SECCIONES:
        items = [n for n in historico['noticias'] if n['sec'] == sec['id']]
        items.sort(key=lambda n: n['fecha'], reverse=True)
        lineas.append(f'  /* -------- {sec["nombre"].upper()} -------- */')
        for i, n in enumerate(items):
            cuerpo = ', '.join(jstr(p) for p in n.get('cuerpo', []))
            lineas.append(
                f"  A({jstr(n['id'])}, {jstr(n['sec'])}, {jstr(n.get('genero', 'todos'))}, {i}, "
                f"{jstr(n['titulo'])}, {jstr(n['entradilla'])}, "
                f"[{cuerpo}], {jstr(n.get('autor'))}, {jstr(n.get('fecha'))}, "
                f"{jstr(n.get('image'))}, {jstr(n.get('link'))}, "
                f"{jstr(n.get('medio'))}, {n.get('viral', 0)}, {jstr(url_para(n))}),"
            )
    lineas += ['];', '']
    escribir_si_cambia(JS, '\n'.join(lineas))


def slug_para(n):
    base = re.sub(r'[^a-z0-9]+', '-', normalizar(n['titulo'])).strip('-')[:58].rstrip('-')
    return (base + '-' + n['id']) if base else n['id']


def url_para(n):
    return BASE_URL + 'noticias/' + slug_para(n) + '.html'


def generar_paginas(historico):
    """Una página HTML real por noticia (SEO + compartir + enlazado interno)."""
    carpeta = BASE / 'noticias'
    carpeta.mkdir(exist_ok=True)
    usados = set()
    e = html.escape

    estilos = '''
<style>
*{box-sizing:border-box}
body{margin:0;background:#080616;color:#f2f0ff;font-family:'Barlow',Arial,sans-serif;line-height:1.7}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:-1;
  background:radial-gradient(circle at 15% 10%,rgba(255,46,136,.18),transparent 45%),
             radial-gradient(circle at 85% 20%,rgba(0,229,255,.15),transparent 45%),
             radial-gradient(circle at 50% 90%,rgba(168,85,247,.15),transparent 50%)}
.cabecera{background:rgba(10,8,30,.95);border-bottom:2px solid #ff2e88;padding:18px 5%;
  box-shadow:0 0 24px rgba(255,46,136,.25)}
.cabecera a{color:#00e5ff;font:800 22px 'Chakra Petch',Arial,sans-serif;text-transform:uppercase;
  text-decoration:none;text-shadow:0 0 12px rgba(0,229,255,.7)}
.articulo{max-width:940px;margin:28px auto;background:rgba(18,16,43,.92);
  border:1px solid rgba(0,229,255,.25);border-top:4px solid var(--accent,#ff2e88);
  padding:32px clamp(20px,5vw,56px) 48px;box-shadow:0 8px 40px rgba(0,0,0,.5)}
.seccion{display:inline-block;color:#fff;font:700 13px 'Chakra Petch',Arial,sans-serif;
  text-transform:uppercase;padding:4px 12px;letter-spacing:.05em;background:var(--accent,#ff2e88)}
h1{font:800 clamp(30px,5vw,52px)/1.08 'Chakra Petch',Arial,sans-serif;margin:16px 0;
  text-shadow:0 0 18px rgba(255,46,136,.45)}
.meta{color:#a9a4c8;font-size:13px;text-transform:uppercase;border-top:1px solid #33305a;
  border-bottom:1px solid #33305a;padding:10px 0;margin-bottom:24px}
img.portada{width:100%;height:auto;display:block;margin:0 0 24px;border:1px solid #33305a}
.entradilla{font-size:20px;font-weight:700;line-height:1.55;border-left:4px solid var(--accent,#ff2e88);
  padding-left:16px;color:#fff}
.cuerpo p{font-size:18px;line-height:1.9;margin:0 0 22px;color:#d9d6f0}
.fuente,.volver{display:inline-block;margin:16px 12px 0 0;color:#00e5ff;font-weight:700}
.compartir{margin:14px 0 28px;display:flex;flex-wrap:wrap;gap:8px}
.compartir a{display:inline-block;padding:9px 15px;border-radius:4px;color:#fff;
  font:700 13px 'Barlow',Arial,sans-serif;text-decoration:none;transition:transform .2s}
.compartir a:hover{transform:translateY(-3px)}
.compartir .wa{background:#25d366;color:#08120b}.compartir .tg{background:#229ed9}
.compartir .x{background:#111}.compartir .fb{background:#1877f2}
.relacionadas{margin-top:34px;border-top:2px solid var(--accent,#ff2e88);padding-top:16px}
.relacionadas h2{font:800 22px 'Chakra Petch',Arial,sans-serif;text-transform:uppercase;margin:0 0 10px}
.relacionadas a{display:block;padding:9px 0;border-bottom:1px solid #33305a;color:#00e5ff;
  font-weight:700;text-decoration:none}
.canales{margin-top:26px;padding:16px;background:rgba(255,46,136,.08);border:1px solid rgba(255,46,136,.4)}
.canales a{margin-right:14px;color:#ff2e88;font-weight:700}
.pie{max-width:940px;margin:0 auto 40px;padding:0 20px;color:#8e89b5;font-size:13px}
</style>'''

    for n in historico['noticias']:
        nombre = slug_para(n) + '.html'
        usados.add(nombre)
        url = url_para(n)
        titulo = n['titulo']
        titulo_seo = titulo if len(titulo) <= 60 else titulo[:57].rsplit(' ', 1)[0] + '…'
        descripcion = limpiar(n.get('entradilla') or titulo, 155)
        imagen = n.get('image') or ''
        img_url = BASE_URL + imagen if imagen else ''
        fecha = n.get('fecha', '')
        autor = n.get('autor') or 'Redacción AnimeChronicle'
        medio = n.get('medio') or NOMBRE
        info_sec = next((s for s in SECCIONES if s['id'] == n['sec']), None)
        nombre_sec = info_sec['nombre'] if info_sec else n['sec']
        color = info_sec['color'] if info_sec else '#ff2e88'
        info_gen = next((g for g in GENEROS if g['id'] == n.get('genero')), None)
        nombre_gen = info_gen['nombre'] if info_gen else 'Anime'

        mismos = [x for x in historico['noticias']
                  if x['id'] != n['id'] and x['sec'] == n['sec']]
        if len(mismos) < 3:
            mismos += [x for x in historico['noticias']
                       if x['id'] != n['id'] and x.get('genero') == n.get('genero')
                       and x not in mismos]
        relacionadas = mismos[:3]

        ld = {
            '@context': 'https://schema.org',
            '@type': 'NewsArticle',
            'headline': titulo,
            'description': descripcion,
            'datePublished': fecha,
            'dateModified': fecha,
            'author': {'@type': 'Person', 'name': autor},
            'publisher': {'@type': 'Organization', 'name': NOMBRE},
            'mainEntityOfPage': url,
            'url': url,
            'articleSection': nombre_sec,
            'keywords': nombre_gen + ', anime, ' + nombre_sec,
        }
        if img_url:
            ld['image'] = [img_url]
        ld_json = json.dumps(ld, ensure_ascii=False).replace('</', '<\\/')

        pagina = [
            '<!DOCTYPE html>', '<html lang="es">', '<head>',
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'  <title>{e(titulo_seo)} | {NOMBRE}</title>',
            f'  <meta name="description" content="{e(descripcion, quote=True)}">',
            f'  <link rel="canonical" href="{url}">',
            '  <meta property="og:type" content="article">',
            f'  <meta property="og:title" content="{e(titulo, quote=True)}">',
            f'  <meta property="og:description" content="{e(descripcion, quote=True)}">',
            f'  <meta property="og:url" content="{url}">',
        ]
        if img_url:
            pagina.append(f'  <meta property="og:image" content="{img_url}">')
        pagina += [
            f'  <meta property="og:site_name" content="{NOMBRE}">',
            '  <meta name="twitter:card" content="summary_large_image">',
            f'  <meta name="twitter:title" content="{e(titulo, quote=True)}">',
            f'  <meta name="twitter:description" content="{e(descripcion, quote=True)}">',
        ]
        if img_url:
            pagina.append(f'  <meta name="twitter:image" content="{img_url}">')
        pagina += [
            '  <script type="application/ld+json">' + ld_json + '</script>',
            '  <link rel="preconnect" href="https://fonts.googleapis.com">',
            '  <link href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600;700&family=Barlow:wght@400;700&display=swap" rel="stylesheet">',
            estilos,
            '</head>', '<body>',
            f'  <div class="cabecera"><a href="../index.html">◀ {NOMBRE} — Volver a la portada</a></div>',
            f'  <article class="articulo" style="--accent:{color}">',
            f'    <span class="seccion">{e(nombre_sec)} · {e(nombre_gen)}</span>',
            f'    <h1>{e(titulo)}</h1>',
            f'    <div class="meta">{e(autor)} · {e(fecha[:10])} · {e(medio)}</div>',
        ]
        if imagen:
            pagina.append(f'    <img class="portada" src="../{imagen}" alt="{e(titulo, quote=True)}">')
        pagina.append(f'    <p class="entradilla">{e(n.get("entradilla") or titulo)}</p>')
        pagina.append('    <div class="cuerpo">')
        for parrafo in n.get('cuerpo', []):
            pagina.append(f'      <p>{e(parrafo)}</p>')
        pagina.append('    </div>')
        if n.get('link'):
            pagina.append(
                f'    <a class="fuente" href="{e(n["link"], quote=True)}" target="_blank" '
                f'rel="noopener noreferrer">Leer la noticia original en {e(medio)} ↗</a>')

        u = quote(url, safe='')
        t = e(titulo, quote=True)
        pagina += [
            '    <div class="compartir">',
            f'      <a class="wa" href="https://api.whatsapp.com/send?text={t}%20%20{u}" target="_blank" rel="noopener noreferrer">WhatsApp</a>',
            f'      <a class="tg" href="https://t.me/share/url?url={u}&text={t}" target="_blank" rel="noopener noreferrer">Telegram</a>',
            f'      <a class="x" href="https://twitter.com/intent/tweet?text={t}&url={u}" target="_blank" rel="noopener noreferrer">X</a>',
            f'      <a class="fb" href="https://www.facebook.com/sharer.php?u={u}" target="_blank" rel="noopener noreferrer">Facebook</a>',
            '    </div>',
        ]

        enlaces = []
        for clave in ('telegram', 'discord', 'whatsapp'):
            if CANALES.get(clave):
                enlaces.append(
                    f'<a href="{CANALES[clave]}" target="_blank" rel="noopener noreferrer">{clave.title()}</a>')
        if enlaces:
            pagina.append('    <div class="canales">Únete a la comunidad: ' +
                          ''.join(enlaces) + '</div>')

        if relacionadas:
            pagina += [
                '    <div class="relacionadas">',
                f'      <h2>También en {e(nombre_sec)}</h2>',
            ]
            for r in relacionadas:
                pagina.append(f'      <a href="{url_para(r)}">{e(r["titulo"])}</a>')
            pagina.append('    </div>')

        pagina += [
            '    <a class="volver" href="../index.html">← Volver a la portada</a>',
            '  </article>',
            f'  <div class="pie">{NOMBRE} · Noticias de fuentes públicas RSS · ¡Comparte con tu nakama!</div>',
            '</body>', '</html>',
        ]
        escribir_si_cambia(carpeta / nombre, '\n'.join(pagina))

    borradas = 0
    for f in carpeta.glob('*.html'):
        if f.name not in usados:
            f.unlink()
            borradas += 1
    if borradas:
        log(f'Páginas estáticas: se borraron {borradas} archivos sin uso')


def generar_sitemap(historico):
    lineas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url><loc>' + BASE_URL + '</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
    ]
    for n in historico['noticias']:
        fecha = (n.get('fecha') or '')[:10]
        lineas.append('  <url><loc>' + url_para(n) + '</loc><lastmod>' + fecha +
                      '</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    lineas.append('</urlset>')
    escribir_si_cambia(BASE / 'sitemap.xml', '\n'.join(lineas))
    escribir_si_cambia(
        BASE / 'robots.txt',
        'User-agent: *\nAllow: /\n\nSitemap: ' + BASE_URL + 'sitemap.xml\n')


def limpiar_imagenes(noticias):
    usadas = {Path(n['image']).name for n in noticias if n.get('image', '').startswith('imagenes/')}
    borradas = 0
    for f in IMGS.iterdir():
        if f.is_file() and f.name not in usadas:
            f.unlink()
            borradas += 1
    if borradas:
        log(f'Imágenes: se borraron {borradas} archivos sin uso')


# ------------------------------------------------------------------ main
def main():
    IMGS.mkdir(exist_ok=True)
    FONDOS.mkdir(exist_ok=True)
    log('=== Inicio de actualización de AnimeChronicle ===')
    ahora = datetime.now(timezone.utc)

    hist = cargar_historico()
    noticias = hist.get('noticias', [])

    manuales = cargar_manuales()
    ids_manuales = {n['id'] for n in manuales}
    noticias = [n for n in noticias if n['id'] not in ids_manuales]
    noticias.extend(manuales)

    corte = (ahora - timedelta(days=DIAS_HISTORICO)).isoformat()
    noticias = [n for n in noticias if n.get('fecha', '') >= corte]
    existentes = {n['id']: n for n in noticias}

    pool = {}

    def anadir(candidatos, etiqueta):
        nuevos = 0
        for n in candidatos:
            clave = normalizar_link(n['link'])
            if clave in pool:
                prev = pool[clave]
                prev['_fuentes'] += 1
                if not prev['_imgurl'] and n['_imgurl']:
                    prev['_imgurl'] = n['_imgurl']
                continue
            n['_clave'] = clave
            pool[clave] = n
            nuevos += 1
        return nuevos

    # 1) Feeds generales especializados
    anadir(parsear_feed(ANN, origen='ann'), 'ANN')
    anadir(parsear_feed(MAL, origen='mal'), 'MAL')
    log(f'Feeds especializados -> {len(pool)} candidatos únicos')

    # 2) Búsquedas por género (Google News + Bing) y por sección
    for gen in GENEROS[1:]:
        anteriores = len(pool)
        nombre_g = gen['nombre'].replace('ō', 'o').replace('ō', 'o')
        for plantilla in CONSULTAS_GENERO:
            q = plantilla.format(g=nombre_g)
            anadir(parsear_feed(GOOGLE.format(q=quote(q)), forzar_gen=gen['id'], origen='google'), q)
            anadir(parsear_feed(BING.format(q=quote(q)), forzar_gen=gen['id'], origen='bing'), q)
        # Solo tres búsquedas por sección (las más visibles): menos peticiones
        # y la misma cobertura, porque las búsquedas generales ya traen de todo.
        for sec in SECCIONES[:3]:
            q = f'anime {nombre_g} {sec["nombre"]} noticias'
            anadir(parsear_feed(GOOGLE.format(q=quote(q)), forzar_sec=sec['id'],
                                forzar_gen=gen['id'], origen='google'), q)
        log(f'{gen["nombre"]:12} -> {len(pool) - anteriores:3} candidatos nuevos')

    # 3) Nos quedamos con los candidatos más recientes y descargamos sus fotos.
    #    Las que no traen imagen usan una ilustración SVG local del tema.
    candidatos = sorted(pool.values(), key=lambda n: n['fecha'], reverse=True)
    candidatos = candidatos[:MAX_EN_ARCHIVO + 60]
    nuevas = 0
    pendientes = []
    for n in candidatos:
        antiguo = existentes.get(n['id'])
        if antiguo and antiguo.get('image'):
            n['image'] = antiguo['image']
        else:
            if not antiguo:
                nuevas += 1
            pendientes.append(n)

    pendientes = pendientes[:MAX_IMAGENES]

    def preparar_imagen(n):
        url = n.get('_imgurl')
        n['image'] = descargar_imagen(url, n['id']) if url else ''
        if not n['image']:
            n['image'] = imagen_respaldo(n['sec'])

    with ThreadPoolExecutor(max_workers=10) as executor:
        list(executor.map(preparar_imagen, pendientes))

    for n in candidatos:
        if not n.get('image'):
            n['image'] = imagen_respaldo(n['sec'])

    # 4) Fusionar con el histórico
    for n in candidatos:
        idn = n['id']
        if idn in existentes:
            viejo = existentes[idn]
            if not viejo.get('image') and n.get('image'):
                viejo['image'] = n['image']
        else:
            noticias.append({k: v for k, v in n.items() if not k.startswith('_')})

    # 5) Viralidad y Top 10
    menciones = Counter(normalizar(n['titulo']) for n in noticias)
    for n in noticias:
        n['viral'] = calcular_viral(n, menciones, ahora)
    noticias.sort(key=lambda n: n['fecha'], reverse=True)
    if len(noticias) > MAX_EN_ARCHIVO:
        log(f'Archivo: se recortaron {len(noticias) - MAX_EN_ARCHIVO} noticias antiguas')
        noticias = noticias[:MAX_EN_ARCHIVO]

    # TODAS las noticias (incluidas las del histórico) deben llevar foto real.
    # Se busca la og:image del artículo —Google News también la expone— y, si
    # falla, la carátula oficial en AniList. El SVG queda como último recurso.
    sin_foto = [n for n in noticias if n.get('image', '').startswith('fondos/')]

    def enriquecer(n):
        enlace = n.get('link', '')
        if enlace.startswith('http'):
            url = og_image(enlace)
            if url:
                img = descargar_imagen(url, n['id'])
                if img:
                    n['image'] = img
                    return
        url = imagen_anilist(n.get('titulo', ''))
        if url:
            img = descargar_imagen(url, n['id'])
            if img:
                n['image'] = img

    if sin_foto:
        log(f'Fotos: se intentan enriquecer {len(sin_foto)} noticias sin foto real')
    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(enriquecer, sin_foto))

    de_hoy = []
    hoy = ahora.astimezone().date().isoformat()
    for n in noticias:
        try:
            fhoy = datetime.fromisoformat(n['fecha']).astimezone().date().isoformat()
        except Exception:
            fhoy = ''
        if fhoy == hoy:
            de_hoy.append(n)
    de_hoy.sort(key=lambda n: (n['viral'], n['fecha']), reverse=True)
    top_ids = [n['id'] for n in de_hoy[:TOP_N]]
    for n in noticias:
        if len(top_ids) >= TOP_N:
            break
        if n['id'] not in top_ids:
            top_ids.append(n['id'])

    # 6) Rellenar combinaciones género/sección que se hayan quedado vacías
    ids_actuales = {n['id'] for n in noticias}
    for gen in GENEROS[1:]:
        for sec in SECCIONES:
            if any(n['genero'] == gen['id'] and n['sec'] == sec['id'] for n in noticias):
                continue
            q = f'anime {gen["nombre"]} {sec["nombre"]}'
            for extra in parsear_feed(GOOGLE.format(q=quote(q)), forzar_sec=sec['id'],
                                      forzar_gen=gen['id'], origen='google'):
                if extra['id'] in ids_actuales:
                    continue
                url = extra['_imgurl']
                extra['image'] = descargar_imagen(url, extra['id']) if url else ''
                if not extra['image']:
                    url = og_image(extra['link']) or imagen_anilist(extra['titulo'])
                    extra['image'] = descargar_imagen(url, extra['id']) if url else ''
                if not extra['image']:
                    extra['image'] = imagen_respaldo(sec['id'])
                extra['viral'] = calcular_viral(extra, menciones, ahora)
                noticias.append({k: v for k, v in extra.items() if not k.startswith('_')})
                ids_actuales.add(extra['id'])
                break
    noticias.sort(key=lambda n: n['fecha'], reverse=True)

    # 7) Última pasada: ningún logo de Google News y todas con foto válida
    sanitizar_imagenes(noticias)

    # 8) Guardar y generar salidas
    hist['noticias'] = noticias
    hist['top'] = top_ids
    hist['tendencias'] = generar_tendencias(noticias)
    hist['actualizado'] = ahora.isoformat()
    guardar_historico(hist)
    generar_js(hist)
    generar_paginas(hist)
    generar_sitemap(hist)
    limpiar_imagenes(noticias)
    log(f'=== Fin: {nuevas} nuevas únicas, {len(noticias)} en archivo, '
        f'{sum(1 for n in noticias if n.get("image"))} con imagen, Top {len(top_ids)} ===')


if __name__ == '__main__':
    main()
