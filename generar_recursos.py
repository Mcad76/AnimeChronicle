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


# ------------------------------------------------------------ personajes
# Arte original: arquetipos de héroes de anime y videojuegos (sin copyright).
PERSONAJES = [
    {'id': 'guerrero',    'nombre': 'GUERRERO DE ENERGÍA', 'pelo': '#ff2e88', 'traje': '#2a1b5e', 'acento': '#ff8a3d', 'prop': 'espada', 'variante': 0},
    {'id': 'espadachina', 'nombre': 'ESPDACHINA VELOZ',    'pelo': '#00e5ff', 'traje': '#3b1d6e', 'acento': '#a855f7', 'prop': 'espada', 'variante': 1},
    {'id': 'ninja',       'nombre': 'NINJA DEL SHURIKEN',  'pelo': '#1a2b1a', 'traje': '#1f3d2b', 'acento': '#39ff14', 'prop': 'kunai', 'variante': 2},
    {'id': 'maga',        'nombre': 'MAGA ESTELAR',        'pelo': '#a855f7', 'traje': '#4a1d6b', 'acento': '#ffd23f', 'prop': 'varita', 'variante': 1},
    {'id': 'mecha',       'nombre': 'MECHA TITÁN',         'pelo': '#4d9fff', 'traje': '#1b2a4a', 'acento': '#ff2e88', 'prop': 'escudo', 'variante': 3},
    {'id': 'detective',   'nombre': 'DETECTIVE GENIO',     'pelo': '#3a2a1a', 'traje': '#2b2b45', 'acento': '#ffd23f', 'prop': 'lupa', 'variante': 1},
    {'id': 'idol',        'nombre': 'ÍDOLO DEL ESCENARIO', 'pelo': '#ff6b35', 'traje': '#5a1d5e', 'acento': '#ffffff', 'prop': 'micro', 'variante': 2},
    {'id': 'dragon',      'nombre': 'JINETE DE DRAGONES',  'pelo': '#ffd23f', 'traje': '#5e1b2e', 'acento': '#ff2e88', 'prop': 'dragon', 'variante': 0},
    {'id': 'samurai',     'nombre': 'SAMURAI ERRANTE',     'pelo': '#e11d48', 'traje': '#2a1a2a', 'acento': '#ffd23f', 'prop': 'espada', 'variante': 2},
    {'id': 'pirata',      'nombre': 'CAPITÁN PIRATA',      'pelo': '#f97316', 'traje': '#3b1d2e', 'acento': '#39ff14', 'prop': 'espada', 'variante': 3},
    {'id': 'cazador',     'nombre': 'CAZADOR DE MONSTRUOS','pelo': '#7c3aed', 'traje': '#1d2b4a', 'acento': '#f59e0b', 'prop': 'arco', 'variante': 1},
    {'id': 'bruja',       'nombre': 'BRUJA NOCTURNA',      'pelo': '#22d3ee', 'traje': '#2d1b4e', 'acento': '#a855f7', 'prop': 'varita', 'variante': 3},
    {'id': 'caballero',   'nombre': 'CABALLERO REAL',      'pelo': '#fbbf24', 'traje': '#1e3a5f', 'acento': '#e2e8f0', 'prop': 'escudo', 'variante': 3},
    {'id': 'cyborg',      'nombre': 'CYBORG REBELDE',      'pelo': '#38bdf8', 'traje': '#0f2740', 'acento': '#ff2e88', 'prop': 'pistola', 'variante': 0},
    {'id': 'astronauta',  'nombre': 'VIAJERO ESPACIAL',    'pelo': '#e2e8f0', 'traje': '#1e293b', 'acento': '#00e5ff', 'prop': 'escudo', 'variante': 3},
    {'id': 'skater',      'nombre': 'SKATER URBANO',       'pelo': '#f472b6', 'traje': '#312e81', 'acento': '#39ff14', 'prop': 'bola', 'variante': 2},
    {'id': 'gamer',       'nombre': 'GAMER LEGEND',        'pelo': '#4ade80', 'traje': '#1a2e2a', 'acento': '#ffd23f', 'prop': 'mando', 'variante': 0},
    {'id': 'boxeador',    'nombre': 'BOXEADOR TITÁN',      'pelo': '#dc2626', 'traje': '#3f1d1d', 'acento': '#fbbf24', 'prop': 'guante', 'variante': 0},
    {'id': 'bailarina',   'nombre': 'BAILARINA NEÓN',      'pelo': '#c084fc', 'traje': '#4a1d4e', 'acento': '#ff2e88', 'prop': 'cinta', 'variante': 2},
    {'id': 'vampiro',     'nombre': 'VAMPIRO ETERNO',      'pelo': '#111827', 'traje': '#3b0d1e', 'acento': '#ef4444', 'prop': 'dragon', 'variante': 1},
    {'id': 'robotito',    'nombre': 'ROBOT DE BOLSILLO',   'pelo': '#60a5fa', 'traje': '#1e3a8a', 'acento': '#22d3ee', 'prop': 'escudo', 'variante': 3},
    {'id': 'sirena',      'nombre': 'SIRENA OCEÁNICA',     'pelo': '#2dd4bf', 'traje': '#134e4a', 'acento': '#38bdf8', 'prop': 'varita', 'variante': 2},
    {'id': 'zorro',       'nombre': 'GUARDIÁN ZORRO',      'pelo': '#fb923c', 'traje': '#3b2415', 'acento': '#fde047', 'prop': 'kunai', 'variante': 0},
    {'id': 'fenix',       'nombre': 'FÉNIX INMORTAL',      'pelo': '#f43f5e', 'traje': '#4c1d1d', 'acento': '#fbbf24', 'prop': 'espada', 'variante': 1},
    {'id': 'kraken',      'nombre': 'TITAN DEL MAR',       'pelo': '#0ea5e9', 'traje': '#0c4a6e', 'acento': '#a78bfa', 'prop': 'escudo', 'variante': 3},
    {'id': 'heroina',     'nombre': 'HEROÍNA DE ACERO',    'pelo': '#facc15', 'traje': '#3f3f46', 'acento': '#f43f5e', 'prop': 'espada', 'variante': 1},
    {'id': 'músico',      'nombre': 'MÚSICO CALLEJERO',    'pelo': '#a3e635', 'traje': '#27303f', 'acento': '#f472b6', 'prop': 'guitarra', 'variante': 0},
    {'id': 'centinela',   'nombre': 'CENTINELA OMEGA',     'pelo': '#94a3b8', 'traje': '#1f2937', 'acento': '#39ff14', 'prop': 'pistola', 'variante': 3},
    {'id': 'ciberpunk',   'nombre': 'CIBERPUNK NEÓN',      'pelo': '#f0abfc', 'traje': '#1e1b4b', 'acento': '#22d3ee', 'prop': 'pistola', 'variante': 1},
    {'id': 'valkiria',    'nombre': 'VALKIRIA DEL CIELO',  'pelo': '#e2e8f0', 'traje': '#312e81', 'acento': '#fbbf24', 'prop': 'escudo', 'variante': 2},
    {'id': 'gladiador',   'nombre': 'GLADIADOR REAL',      'pelo': '#b45309', 'traje': '#3f1d1d', 'acento': '#f59e0b', 'prop': 'espada', 'variante': 0},
    {'id': 'templario',   'nombre': 'TEMPLARIO SANTO',     'pelo': '#fcd34d', 'traje': '#1e3a5f', 'acento': '#e2e8f0', 'prop': 'escudo', 'variante': 1},
    {'id': 'marinero',    'nombre': 'MARINERO VALIENTE',   'pelo': '#38bdf8', 'traje': '#0c4a6e', 'acento': '#fde047', 'prop': 'arco', 'variante': 0},
    {'id': 'piloto',      'nombre': 'PILOTO DE ASALTO',    'pelo': '#fb7185', 'traje': '#1f2937', 'acento': '#38bdf8', 'prop': 'pistola', 'variante': 3},
    {'id': 'artista',     'nombre': 'ARTISTA CALLEJERO',   'pelo': '#f472b6', 'traje': '#4c1d95', 'acento': '#a3e635', 'prop': 'cinta', 'variante': 2},
    {'id': 'alquimista',  'nombre': 'ALQUIMISTA MAESTRO',  'pelo': '#34d399', 'traje': '#064e3b', 'acento': '#fbbf24', 'prop': 'varita', 'variante': 1},
    {'id': 'ronin',       'nombre': 'RØNIN SIN AMO',       'pelo': '#1f2937', 'traje': '#3b1d2e', 'acento': '#ef4444', 'prop': 'espada', 'variante': 2},
    {'id': 'sacerdotisa', 'nombre': 'SACERDOTISA LUNA',    'pelo': '#c4b5fd', 'traje': '#2e1065', 'acento': '#fde047', 'prop': 'varita', 'variante': 1},
    {'id': 'mercenario',  'nombre': 'MERCENARIO OMEGA',    'pelo': '#f97316', 'traje': '#292524', 'acento': '#84cc16', 'prop': 'pistola', 'variante': 0},
    {'id': 'cazarrecompensas', 'nombre': 'CAZARRECOMPENSAS', 'pelo': '#22d3ee', 'traje': '#0f172a', 'acento': '#f43f5e', 'prop': 'guante', 'variante': 3},
]

SECCION_PERSONAJE = {
    'estrenos': 'guerrero', 'series': 'ninja', 'peliculas': 'espadachina',
    'manga': 'maga', 'videojuegos': 'mecha', 'eventos': 'idol', 'comunidad': 'dragon',
}


def pelo_formas(pelo, variante, ident):
    """Cuatro peinados detectallados, con mechones de brillo."""
    grad = f'url(#pelo-{ident})'
    if variante == 1:  # melena larga y lateral
        base = (f'<path d="M126 176 Q108 92 178 80 Q252 70 276 156 L292 312 L256 300 '
                f'L246 168 Q200 134 152 170 L148 302 L112 312Z" fill="{grad}" '
                f'stroke="#160e2e" stroke-width="4"/>'
                f'<path d="M140 150 Q160 104 206 100" fill="none" stroke="#fff" stroke-width="6" opacity=".35" stroke-linecap="round"/>')
    elif variante == 2:  # dos coletazos con lazos
        base = (f'<path d="M126 176 L114 102 L152 138 L160 70 L196 120 L202 46 L240 120 '
                f'L254 70 L272 138 L288 102 L274 176 Q200 128 126 176Z" fill="{grad}" '
                f'stroke="#160e2e" stroke-width="4"/>'
                f'<ellipse cx="102" cy="226" rx="24" ry="68" fill="{grad}" stroke="#160e2e" stroke-width="4"/>'
                f'<ellipse cx="298" cy="226" rx="24" ry="68" fill="{grad}" stroke="#160e2e" stroke-width="4"/>'
                f'<rect x="88" y="162" width="30" height="14" rx="6" fill="#ff2e88" stroke="#fff" stroke-width="2"/>'
                f'<rect x="282" y="162" width="30" height="14" rx="6" fill="#ff2e88" stroke="#fff" stroke-width="2"/>')
    elif variante == 3:  # casco / capucha futurista
        base = (f'<path d="M116 180 Q104 68 200 64 Q296 68 284 180 L260 174 Q254 102 200 98 '
                f'Q146 102 140 174Z" fill="{grad}" stroke="#160e2e" stroke-width="4"/>'
                f'<path d="M124 150 Q200 104 276 150" fill="none" stroke="#fff" stroke-width="5" opacity=".55"/>'
                f'<rect x="168" y="74" width="64" height="12" rx="6" fill="#00e5ff" opacity=".8"/>')
    else:  # pelo con puntas
        base = (f'<path d="M124 178 L110 104 L146 136 L150 68 L182 120 L200 46 L218 120 '
                f'L250 68 L254 136 L290 104 L276 178 Q200 126 124 178Z" fill="{grad}" '
                f'stroke="#160e2e" stroke-width="4"/>')
    brillo = (f'<path d="M138 132 Q164 92 208 88" fill="none" stroke="#fff" '
              f'stroke-width="6" opacity=".32" stroke-linecap="round"/>')
    return base + brillo


def formas_personaje(p, escala=1.0):
    """Cuerpo detallado: rostro expresivo, armadura, sombras y accesorios."""
    ident = p['id']
    pelo, traje, acento, prop = p['pelo'], p['traje'], p['acento'], p['prop']
    v = p.get('variante', 0)

    defs = f'''<defs>
      <linearGradient id="cuerpo-{ident}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{traje}"/><stop offset=".6" stop-color="{traje}"/>
        <stop offset="1" stop-color="#070512"/>
      </linearGradient>
      <linearGradient id="pelo-{ident}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#ffffff" stop-opacity=".45"/>
        <stop offset=".35" stop-color="{pelo}"/><stop offset="1" stop-color="{pelo}"/>
      </linearGradient>
      <radialGradient id="iris-{ident}"><stop offset="0" stop-color="#fff"/>
        <stop offset=".45" stop-color="{acento}"/><stop offset="1" stop-color="#111827"/>
      </radialGradient>
      <linearGradient id="metal-{ident}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#f8fafc"/><stop offset=".5" stop-color="#94a3b8"/>
        <stop offset="1" stop-color="#475569"/>
      </linearGradient>
    </defs>'''

    partes = [
        defs,
        # sombra y aura
        '<ellipse cx="200" cy="494" rx="96" ry="14" fill="#000" opacity=".5"/>',
        f'<circle cx="200" cy="250" r="150" fill="none" stroke="{acento}" stroke-width="2" opacity=".35" stroke-dasharray="14 8"/>',
        f'<circle cx="200" cy="250" r="182" fill="none" stroke="{acento}" stroke-width="1" opacity=".2"/>',
        f'<path d="M42 130 l70 -26 M30 190 l62 -14 M350 120 l-58 22" stroke="{acento}" stroke-width="3" opacity=".4" stroke-linecap="round"/>',
        # capa con pliegues
        f'<path d="M116 272 Q40 372 78 486 L322 486 Q360 372 284 272Z" fill="{pelo}" opacity=".5"/>',
        f'<path d="M120 290 Q92 388 108 470 M280 290 Q308 388 292 470" fill="none" stroke="#000" stroke-width="3" opacity=".25"/>',
        # piernas, rodilleras y botas
        '<path d="M156 378 L150 474 L184 474 L188 378Z" fill="#15122f" stroke="' + acento + '" stroke-width="3"/>',
        '<path d="M212 378 L216 474 L250 474 L244 378Z" fill="#15122f" stroke="' + acento + '" stroke-width="3"/>',
        f'<path d="M154 418 L186 418 M214 418 L246 418" stroke="{acento}" stroke-width="6" opacity=".8"/>',
        f'<rect x="140" y="456" width="60" height="28" rx="8" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        f'<rect x="200" y="456" width="60" height="28" rx="8" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        f'<path d="M140 476 H200 M200 476 H260" stroke="#111" stroke-width="5"/>',
        # torso con hombreras y cuello
        f'<path d="M136 268 Q200 236 264 268 L282 386 Q200 410 118 386Z" fill="url(#cuerpo-{ident})" stroke="{acento}" stroke-width="4"/>',
        f'<path d="M138 272 Q168 292 200 292 Q232 292 262 272 L254 300 Q200 316 146 300Z" fill="{acento}" opacity=".85"/>',
        f'<path d="M132 266 Q112 256 108 286 L122 302 L146 282Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        f'<path d="M268 266 Q288 256 292 286 L278 302 L254 282Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        f'<path d="M200 300 L200 388" stroke="{acento}" stroke-width="4" opacity=".7"/>',
        f'<rect x="122" y="344" width="156" height="18" fill="{acento}" stroke="#111" stroke-width="3"/>',
        f'<rect x="188" y="342" width="24" height="22" rx="4" fill="url(#metal-{ident})" stroke="#111" stroke-width="2"/>',
        # brazos y guantes
        f'<path d="M136 288 L92 360" stroke="url(#cuerpo-{ident})" stroke-width="27" stroke-linecap="round"/>',
        f'<path d="M264 288 L310 224" stroke="url(#cuerpo-{ident})" stroke-width="27" stroke-linecap="round"/>',
        f'<circle cx="90" cy="364" r="16" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        f'<circle cx="312" cy="221" r="16" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
        '<circle cx="84" cy="360" r="3" fill="#fff"/><circle cx="306" cy="217" r="3" fill="#fff"/>',
        # cuello y rostro
        '<rect x="186" y="244" width="28" height="30" rx="6" fill="#f0be97" stroke="#7a4a35" stroke-width="2"/>',
        '<path d="M138 170 Q140 244 200 254 Q260 244 262 170Z" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="4"/>',
        '<ellipse cx="135" cy="194" rx="11" ry="16" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="3"/>',
        '<ellipse cx="265" cy="194" rx="11" ry="16" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="3"/>',
        # ojos grandes con brillo
        '<path d="M154 190 Q174 172 194 190 Q174 208 154 190Z" fill="#fff" stroke="#2a1a3a" stroke-width="3"/>',
        '<path d="M206 190 Q226 172 246 190 Q226 208 206 190Z" fill="#fff" stroke="#2a1a3a" stroke-width="3"/>',
        f'<circle cx="175" cy="190" r="11" fill="url(#iris-{ident})"/>',
        f'<circle cx="225" cy="190" r="11" fill="url(#iris-{ident})"/>',
        '<circle cx="175" cy="190" r="5" fill="#0f172a"/><circle cx="225" cy="190" r="5" fill="#0f172a"/>',
        '<circle cx="179" cy="185" r="4" fill="#fff"/><circle cx="229" cy="185" r="4" fill="#fff"/>',
        '<circle cx="170" cy="195" r="2" fill="#fff" opacity=".8"/><circle cx="220" cy="195" r="2" fill="#fff" opacity=".8"/>',
        f'<path d="M152 174 Q174 164 194 174 M206 174 Q226 164 248 174" fill="none" stroke="{pelo}" stroke-width="6" stroke-linecap="round"/>',
        '<path d="M198 206 L194 220 L202 220" fill="none" stroke="#c98f6e" stroke-width="3" stroke-linecap="round"/>',
        '<path d="M184 232 Q200 244 216 232" fill="none" stroke="#8a3552" stroke-width="4" stroke-linecap="round"/>',
        f'<circle cx="200" cy="162" r="6" fill="{acento}" opacity=".9"/>',
        pelo_formas(pelo, v, ident),
        # accessory según peinado
        (f'<rect x="128" y="158" width="144" height="9" rx="4" fill="{acento}" stroke="#fff" stroke-width="2"/>'
         if v == 2 else
         f'<path d="M150 150 Q200 130 250 150" fill="none" stroke="{acento}" stroke-width="5" opacity=".8"/>'
         if v == 1 else ''),
    ]

    if prop == 'espada':
        partes += [
            f'<path d="M322 214 L128 34" stroke="url(#metal-{ident})" stroke-width="15" stroke-linecap="round"/>',
            '<path d="M322 214 L128 34" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".75"/>',
            f'<path d="M300 238 L340 198" stroke="{acento}" stroke-width="13" stroke-linecap="round"/>',
            '<circle cx="320" cy="218" r="6" fill="#fbbf24"/>',
        ]
    elif prop == 'kunai':
        partes += [
            '<path d="M312 224 L370 174 L356 234Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
            '<path d="M346 220 L372 250" stroke="#64748b" stroke-width="10" stroke-linecap="round"/>',
            f'<circle cx="360" cy="244" r="7" fill="{acento}"/>',
        ]
    elif prop == 'varita':
        partes += [
            '<path d="M100 384 L82 104" stroke="#fbbf24" stroke-width="10" stroke-linecap="round"/>',
            '<path d="M82 58 L96 88 L126 92 L103 111 L109 141 L82 125 L55 141 L61 111 L38 92 L68 88Z" fill="#fde047" stroke="#fff" stroke-width="4"/>',
            f'<circle cx="82" cy="100" r="7" fill="{acento}"/>',
        ]
    elif prop == 'escudo':
        partes += [
            f'<circle cx="330" cy="238" r="48" fill="{acento}" opacity=".9" stroke="#fff" stroke-width="5"/>',
            f'<circle cx="330" cy="238" r="35" fill="none" stroke="#111" stroke-width="4"/>',
            '<path d="M330 208 L330 268 M300 238 L360 238" stroke="#fff" stroke-width="5"/>',
        ]
    elif prop == 'lupa':
        partes += [
            '<circle cx="326" cy="230" r="32" fill="#bff6ff" opacity=".4" stroke="#fbbf24" stroke-width="9"/>',
            '<path d="M348 254 L376 288" stroke="#8b5a2b" stroke-width="11" stroke-linecap="round"/>',
            '<path d="M310 216 Q326 206 342 216" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>',
        ]
    elif prop == 'micro':
        partes += [
            f'<rect x="304" y="186" width="20" height="64" rx="10" fill="{acento}" stroke="#fff" stroke-width="3"/>',
            '<circle cx="314" cy="178" r="19" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
            '<path d="M304 174 Q314 168 324 174" fill="none" stroke="#fff" stroke-width="3" opacity=".7"/>',
        ]
    elif prop == 'arco':
        partes += [
            '<path d="M330 150 Q388 230 330 310" fill="none" stroke="#d9a05b" stroke-width="10"/>',
            '<path d="M330 150 L330 310" stroke="#e2e8f0" stroke-width="3"/>',
            '<path d="M316 230 L352 204 L346 246Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="2"/>',
        ]
    elif prop == 'pistola':
        partes += [
            '<path d="M300 220 L370 206 L372 236 L316 248Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
            '<path d="M312 246 L330 274 L346 270 L334 244Z" fill="#334155" stroke="#111" stroke-width="2"/>',
            f'<circle cx="366" cy="221" r="5" fill="{acento}"/>',
        ]
    elif prop == 'bola':
        partes += [
            f'<circle cx="344" cy="240" r="34" fill="{acento}" stroke="#fff" stroke-width="5"/>',
            '<path d="M312 230 Q344 214 376 230 M312 252 Q344 238 376 252" fill="none" stroke="#111" stroke-width="3"/>',
        ]
    elif prop == 'mando':
        partes += [
            f'<rect x="304" y="214" width="72" height="40" rx="18" fill="{acento}" stroke="#fff" stroke-width="3"/>',
            '<circle cx="322" cy="234" r="6" fill="#111"/><circle cx="358" cy="226" r="5" fill="#111"/>',
            '<circle cx="350" cy="242" r="5" fill="#111"/>',
        ]
    elif prop == 'guante':
        partes += [
            f'<circle cx="340" cy="232" r="32" fill="{acento}" stroke="#fff" stroke-width="4"/>',
            '<path d="M314 214 Q340 202 366 214" fill="none" stroke="#111" stroke-width="4"/>',
        ]
    elif prop == 'cinta':
        partes += [
            f'<path d="M310 236 Q356 174 384 220 Q356 208 338 244Z" fill="{acento}" stroke="#fff" stroke-width="3"/>',
            f'<path d="M306 250 Q348 302 384 258" fill="none" stroke="{acento}" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif prop == 'guitarra':
        partes += [
            f'<ellipse cx="344" cy="252" rx="30" ry="38" fill="{acento}" stroke="#fff" stroke-width="4"/>',
            '<rect x="338" y="160" width="12" height="72" fill="#d9a05b" stroke="#111" stroke-width="2"/>',
            '<circle cx="344" cy="258" r="10" fill="#111"/>',
        ]
    else:  # dragón
        partes += [
            '<path d="M304 220 Q360 166 384 210 Q360 198 348 224 Q374 246 348 266 Q330 250 304 254Z" fill="#ff2e88" stroke="#fbbf24" stroke-width="4"/>',
            '<circle cx="364" cy="214" r="4" fill="#fff"/>',
            '<path d="M348 224 L362 228 L348 234Z" fill="#111"/>',
        ]

    return '<g transform="scale(' + str(escala) + ')">' + ''.join(partes) + '</g>'

def generar_personajes():
    print('Generando personajes...')
    destino = FONDOS / 'personajes'
    destino.mkdir(parents=True, exist_ok=True)

    for p in PERSONAJES:
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="520" viewBox="0 0 400 520">
  {formas_personaje(p)}
</svg>'''
        escribir_svg('personajes/' + p['id'] + '.svg', svg)

    # Fondo principal: varios héroes en silueta neón
    random.seed(11)
    grupos = []
    posiciones = [(10, 260, 0.85), (180, 320, 1.0), (350, 240, 0.8),
                  (510, 320, 1.05), (680, 250, 0.85), (840, 330, 0.95),
                  (1000, 250, 0.9), (1170, 320, 1.0), (1320, 240, 0.8),
                  (1460, 330, 0.9)]
    for (x, y, s), p in zip(posiciones, PERSONAJES[:10]):
        grupos.append(f'<g transform="translate({x},{y}) scale({s})" opacity=".22">'
                      + formas_personaje(p) + '</g>')
    escribir_svg('personajes-fondo.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">
  <defs>
    <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#080616"/><stop offset=".5" stop-color="#1a0f3a"/><stop offset="1" stop-color="#080616"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="900" fill="url(#b)"/>
  {''.join(grupos)}
</svg>''')

    # Respaldo por sección con el personaje protagonista
    random.seed(3)
    for ident, nombre, color, kanji, simbolo in SECCIONES:
        p = next(x for x in PERSONAJES if x['id'] == SECCION_PERSONAJE[ident])
        velocidad = []
        for i in range(22):
            x = random.randint(-200, 1100)
            y = random.randint(0, 640)
            w = random.randint(40, 240)
            velocidad.append(f'<path d="M{x} {y} l{w} -{random.randint(20,90)}" stroke="{color}" stroke-width="{random.choice((1,2,3))}" opacity="{round(random.uniform(.08,.26),2)}"/>')
        escribir_svg(f'fallback-{ident}.svg', f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640" viewBox="0 0 1000 640">
  <defs>
    <linearGradient id="f" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#080616"/><stop offset=".55" stop-color="#171037"/><stop offset="1" stop-color="#080616"/>
    </linearGradient>
    <radialGradient id="g"><stop offset="0" stop-color="{color}" stop-opacity=".55"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="1000" height="640" fill="url(#f)"/>
  <circle cx="720" cy="260" r="330" fill="url(#g)"/>
  {''.join(velocidad)}
  <text x="500" y="360" font-size="230" fill="{color}" opacity=".12" text-anchor="middle" font-family="sans-serif">{kanji}</text>
  <g transform="translate(600,120) scale(1.15)">{formas_personaje(p)}</g>
  <path d="M0 470 L1000 430 L1000 640 L0 640Z" fill="#080616" opacity=".72"/>
  <text x="48" y="528" font-size="66" font-weight="900" fill="#fff" font-family="Arial,sans-serif">{nombre}</text>
  <text x="50" y="572" font-size="22" letter-spacing="7" fill="{color}" font-family="Arial,sans-serif">ANIMECHRONICLE {simbolo} · {p["nombre"]}</text>
</svg>''')


if __name__ == '__main__':
    generar_sonidos()
    generar_fondos()
    generar_personajes()
    print('Recursos listos.')
