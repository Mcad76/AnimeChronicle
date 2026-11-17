#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeChronicle — Generador de recursos locales.

Crea los efectos de sonido (WAV sintetizados, sin copyright) y las imágenes
SVG de fondo / respaldo usadas por la web. No requiere dependencias externas.

Uso:  python3 generar_recursos.py
"""

import math
import random
import struct
import wave
from pathlib import Path

BASE = Path(__file__).resolve().parent
SONIDOS = BASE / 'sonidos'
FONDOS = BASE / 'fondos'
SR = 22050

SECCIONES = [
    ('estrenos',    'ESTRENOS',         '#ff2e88', '新作', '✦'),
    ('series',      'SERIES TV',        '#00e5ff', 'アニメ', '▤'),
    ('peliculas',   'PELÍCULAS',        '#ffd23f', '映画', '▶'),
    ('manga',       'MANGA Y NOVELAS',  '#a855f7', '漫画', '✎'),
    ('videojuegos', 'VIDEOJUEGOS',      '#39ff14', 'ゲーム', '◆'),
    ('eventos',     'EVENTOS / COSPLAY','#ff6b35', 'イベント', '★'),
    ('comunidad',   'COMUNIDAD',        '#4d9fff', '仲間', '♥'),
]

# ------------------------------------------------------------ audio
def normalizar(tracks, pico=0.88):
    if not tracks:
        return []
    n = max(len(t) for t in tracks)
    out = [0.0] * n
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    m = max((abs(v) for v in out), default=0.0)
    if m > pico:
        out = [v * pico / m for v in out]
    return out


def escribir_wav(nombre, muestras):
    SONIDOS.mkdir(parents=True, exist_ok=True)
    ruta = SONIDOS / nombre
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = b''.join(struct.pack('<h', int(max(-1, min(1, v)) * 32767))
                          for v in muestras)
        w.writeframes(frames)
    print(f'  sonido  {ruta.name:16} {len(muestras)/SR:.2f}s')


def tono(freq, dur, vol=1.0, forma='sine', ataque=0.006):
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t / ataque) * math.exp(-3.4 * t / dur)
        if forma == 'square':
            v = math.copysign(1.0, math.sin(2 * math.pi * freq * t))
            v = 0.6 * v + 0.4 * math.sin(2 * math.pi * freq * t)
        elif forma == 'tri':
            v = 2 / math.pi * math.asin(math.sin(2 * math.pi * freq * t))
        else:
            v = math.sin(2 * math.pi * freq * t)
        out.append(v * env * vol)
    return out


def desplazar(track, segundos):
    return [0.0] * int(SR * segundos) + track


def ruido(dur, vol=1.0, corte=0.12, subida=False):
    n = int(SR * dur)
    out = []
    prev = 0.0
    for i in range(n):
        t = i / SR
        blanco = random.uniform(-1, 1)
        k = corte * (0.3 + 0.7 * (t / dur)) if subida else corte
        prev = prev * (1 - k) + blanco * k
        env = math.sin(math.pi * t / dur) ** 1.4
        out.append(prev * env * vol)
    return out


def generar_sonidos():
    print('Generando sonidos...')
    random.seed(7)

    # Blip de interfaz, muy corto y agudo
    escribir_wav('click.wav', normalizar([
        desplazar(tono(1480, 0.06, 0.9, 'tri'), 0),
        desplazar(tono(2220, 0.045, 0.35), 0.004),
    ]))

    # "Power up" al seleccionar una noticia
    notas = [523.25, 659.25, 783.99, 1046.50, 1318.51]
    escribir_wav('select.wav', normalizar([
        desplazar(tono(f, 0.13, 0.75, 'square'), i * 0.048)
        for i, f in enumerate(notas)
    ] + [desplazar(tono(1567.98, 0.22, 0.45, 'tri'), 0.25)]))

    # Barrido de velocidad
    escribir_wav('whoosh.wav', normalizar([
        ruido(0.38, 1.0, corte=0.10, subida=True),
        desplazar(tono(180, 0.34, 0.22, 'tri'), 0.02),
    ]))

    # Abrir noticia: barrido + campana ascendente
    escribir_wav('open.wav', normalizar([
        ruido(0.30, 0.55, corte=0.13, subida=True),
        desplazar(tono(440, 0.18, 0.5, 'square'), 0.03),
        desplazar(tono(659.25, 0.18, 0.5, 'square'), 0.12),
        desplazar(tono(880, 0.26, 0.6, 'tri'), 0.22),
    ]))

    # Cerrar: tres tonos descendentes
    escribir_wav('close.wav', normalizar([
        desplazar(tono(660, 0.10, 0.5, 'tri'), 0),
        desplazar(tono(494, 0.10, 0.5, 'tri'), 0.08),
        desplazar(tono(330, 0.18, 0.55, 'tri'), 0.16),
    ]))

    # Cambio de pestaña: "da-dun" grave
    escribir_wav('tab.wav', normalizar([
        desplazar(tono(196, 0.11, 0.7, 'square'), 0),
        desplazar(tono(293.66, 0.17, 0.7, 'square'), 0.075),
    ]))

    # Tick muy suave para el hover
    escribir_wav('hover.wav', normalizar([
        tono(1760, 0.035, 0.30, 'sine', ataque=0.002),
    ]))

    # Bucle musical synth (8 s) — se activa solo si el usuario pulsa ♪
    acordes = [
        [220.00, 261.63, 329.63],  # Am
        [174.61, 220.00, 261.63],  # F
        [130.81, 164.81, 196.00],  # C
        [196.00, 246.94, 293.66],  # G
    ]
    bgm = []
    paso = 0.25
    for compas, acorde in enumerate(acordes):
        base = compas * 2.0
        # arpegio de corcheas con envolvente de "pluck"
        for i in range(8):
            f = acorde[i % 3] * (2 if i == 7 else 1)
            bgm.append(desplazar(tono(f, 0.20, 0.30, 'square', ataque=0.003),
                                 base + i * paso))
        # bajo
        bgm.append(desplazar(tono(acorde[0] / 2, 0.42, 0.34, 'tri'), base))
        bgm.append(desplazar(tono(acorde[0] / 2, 0.34, 0.26, 'tri'), base + 1.0))
        # bombo y hi-hat
        for golpe in (0.0, 1.0):
            bgm.append(desplazar(tono(70, 0.16, 0.5, 'sine', ataque=0.001), base + golpe))
            bgm.append(desplazar(ruido(0.045, 0.14, corte=0.35), base + golpe + 0.5))
    escribir_wav('bgm.wav', normalizar(bgm, pico=0.8))


# ------------------------------------------------------------ svg
def escribir_svg(nombre, contenido):
    FONDOS.mkdir(parents=True, exist_ok=True)
    ruta = FONDOS / nombre
    ruta.write_text(contenido.strip() + '\n', encoding='utf-8')
    print(f'  fondo   {ruta.name}')


def generar_fondos():
    print('Generando fondos SVG...')

    # Campo estrellado (tesela)
    random.seed(42)
    estrellas = []
    for _ in range(150):
        x = random.randint(0, 700)
        y = random.randint(0, 700)
        r = round(random.uniform(0.5, 2.1), 1)
        o = round(random.uniform(0.15, 0.85), 2)
        estrellas.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{o}"/>')
    escribir_svg('estrellas.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="700" viewBox="0 0 700 700">
  {''.join(estrellas)}
</svg>''')

    # Rejilla neón en perspectiva
    lineas = []
    for i in range(0, 701, 70):
        lineas.append(f'<path d="M350 380 L{i} 700" stroke="#00e5ff" stroke-width="1" opacity=".28"/>')
    for i in range(390, 701, 45):
        lineas.append(f'<path d="M0 {i} L700 {i}" stroke="#ff2e88" stroke-width="1" opacity=".16"/>')
    escribir_svg('grid.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="700" viewBox="0 0 700 700">
  {''.join(lineas)}
</svg>''')

    # Pétalos de sakura (tesela)
    petalos = []
    random.seed(9)
    for _ in range(26):
        x = random.randint(0, 700)
        y = random.randint(0, 700)
        s = round(random.uniform(6, 16), 1)
        o = round(random.uniform(0.12, 0.4), 2)
        petalos.append(
            f'<path d="M{x} {y} q{s} {-s} {s*1.6} 0 q{-s*0.6} {s} {-s*1.6} 0z" '
            f'fill="#ff9ec4" opacity="{o}"/>')
    escribir_svg('sakura.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="700" viewBox="0 0 700 700">
  {''.join(petalos)}
</svg>''')

    # Ilustraciones de respaldo por sección
    random.seed(3)
    for ident, nombre, color, kanji, simbolo in SECCIONES:
        velocidad = []
        for i in range(26):
            x = random.randint(-200, 1100)
            y = random.randint(0, 640)
            w = random.randint(40, 260)
            velocidad.append(
                f'<path d="M{x} {y} l{w} -{random.randint(20, 90)}" '
                f'stroke="{color}" stroke-width="{random.choice((1,2,3))}" '
                f'opacity="{round(random.uniform(.08,.28),2)}"/>')
        escribir_svg(f'fallback-{ident}.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640" viewBox="0 0 1000 640">
  <defs>
    <linearGradient id="f" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#080616"/><stop offset=".55" stop-color="#171037"/><stop offset="1" stop-color="#080616"/>
    </linearGradient>
    <radialGradient id="g"><stop offset="0" stop-color="{color}" stop-opacity=".55"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="1000" height="640" fill="url(#f)"/>
  <circle cx="760" cy="180" r="330" fill="url(#g)"/>
  {''.join(velocidad)}
  <text x="820" y="400" font-size="290" fill="{color}" opacity=".14" text-anchor="middle" font-family="sans-serif">{kanji}</text>
  <path d="M0 470 L1000 360 L1000 640 L0 640Z" fill="#080616" opacity=".65"/>
  <text x="56" y="520" font-size="76" font-weight="900" fill="#fff" font-family="Arial,sans-serif">{nombre}</text>
  <text x="58" y="566" font-size="24" letter-spacing="8" fill="{color}" font-family="Arial,sans-serif">ANIMECHRONICLE {simbolo}</text>
</svg>''')


if __name__ == '__main__':
    generar_sonidos()
    generar_fondos()
    print('Recursos listos.')
