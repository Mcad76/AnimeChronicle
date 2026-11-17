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
]

SECCION_PERSONAJE = {
    'estrenos': 'guerrero', 'series': 'ninja', 'peliculas': 'espadachina',
    'manga': 'maga', 'videojuegos': 'mecha', 'eventos': 'idol', 'comunidad': 'dragon',
}


def pelo_formas(pelo, variante):
    """Cuatro peinados distintos para que los personajes no se repitan."""
    if variante == 1:  # melena larga y lateral
        return (f'<path d="M126 176 Q110 96 176 84 Q248 76 274 156 L286 300 L254 292 '
                f'L246 168 Q200 136 154 170 L150 296 L118 290Z" fill="{pelo}" '
                f'stroke="#160e2e" stroke-width="3"/>')
    if variante == 2:  # dos coletazos
        return (f'<path d="M126 176 L116 104 L152 138 L162 74 L196 120 L202 50 L238 120 '
                f'L254 74 L270 138 L286 104 L274 176 Q200 130 126 176Z" fill="{pelo}" '
                f'stroke="#160e2e" stroke-width="3"/>'
                f'<ellipse cx="104" cy="230" rx="22" ry="66" fill="{pelo}" stroke="#160e2e" stroke-width="3"/>'
                f'<ellipse cx="296" cy="230" rx="22" ry="66" fill="{pelo}" stroke="#160e2e" stroke-width="3"/>')
    if variante == 3:  # casco / capucha
        return (f'<path d="M118 178 Q108 72 200 68 Q292 72 282 178 L262 172 Q256 104 200 100 '
                f'Q144 104 138 172Z" fill="{pelo}" stroke="#160e2e" stroke-width="3"/>'
                f'<path d="M126 150 Q200 108 274 150" fill="none" stroke="#fff" stroke-width="4" opacity=".5"/>')
    return (f'<path d="M126 176 L112 108 L146 138 L152 72 L182 122 L200 52 L218 122 '
            f'L248 72 L254 138 L288 108 L274 176 Q200 128 126 176Z" fill="{pelo}" '
            f'stroke="#160e2e" stroke-width="3"/>')


def formas_personaje(p, escala=1.0):
    """Devuelve las formas SVG de un personaje (sin etiqueta <svg>)."""
    pelo, traje, acento, prop = p['pelo'], p['traje'], p['acento'], p['prop']
    partes = [
        f'<circle cx="200" cy="250" r="152" fill="none" stroke="{acento}" stroke-width="2" opacity=".35"/>',
        f'<circle cx="200" cy="250" r="182" fill="none" stroke="{acento}" stroke-width="1" opacity=".18"/>',
        f'<path d="M118 272 Q52 372 88 482 L312 482 Q348 372 282 272Z" fill="{pelo}" opacity=".45"/>',
        '<rect x="158" y="382" width="32" height="98" rx="10" fill="#15122f" stroke="' + acento + '" stroke-width="2"/>',
        '<rect x="210" y="382" width="32" height="98" rx="10" fill="#15122f" stroke="' + acento + '" stroke-width="2"/>',
        f'<rect x="146" y="462" width="56" height="22" rx="7" fill="{acento}"/>',
        f'<rect x="198" y="462" width="56" height="22" rx="7" fill="{acento}"/>',
        f'<path d="M140 270 Q200 238 260 270 L278 388 Q200 408 122 388Z" fill="{traje}" stroke="{acento}" stroke-width="3"/>',
        f'<rect x="126" y="344" width="148" height="15" fill="{acento}"/>',
        f'<path d="M142 286 L96 362" stroke="{traje}" stroke-width="24" stroke-linecap="round"/>',
        f'<path d="M258 286 L308 224" stroke="{traje}" stroke-width="24" stroke-linecap="round"/>',
        '<circle cx="94" cy="366" r="14" fill="#ffd9b3"/>',
        '<circle cx="311" cy="221" r="14" fill="#ffd9b3"/>',
        '<rect x="188" y="248" width="24" height="26" fill="#ffd9b3"/>',
        '<ellipse cx="200" cy="185" rx="68" ry="72" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="3"/>',
        pelo_formas(p['pelo'], p.get('variante', 0)),
        '<ellipse cx="175" cy="192" rx="13" ry="17" fill="#fff"/>',
        '<ellipse cx="225" cy="192" rx="13" ry="17" fill="#fff"/>',
        f'<circle cx="177" cy="194" r="7" fill="{acento}"/><circle cx="227" cy="194" r="7" fill="{acento}"/>',
        '<circle cx="180" cy="190" r="2.5" fill="#fff"/><circle cx="230" cy="190" r="2.5" fill="#fff"/>',
        f'<path d="M160 168 L188 164 M212 164 L240 168" stroke="{pelo}" stroke-width="5" stroke-linecap="round"/>',
        '<path d="M186 228 Q200 240 214 228" fill="none" stroke="#7a2f4a" stroke-width="4" stroke-linecap="round"/>',
        f'<circle cx="200" cy="132" r="7" fill="{acento}"/>',
    ]

    if prop == 'espada':
        partes += [
            '<path d="M322 214 L128 34" stroke="#eaf6ff" stroke-width="13" stroke-linecap="round"/>',
            '<path d="M322 214 L128 34" stroke="#9fd8ff" stroke-width="5" stroke-linecap="round"/>',
            f'<path d="M304 234 L338 200" stroke="{acento}" stroke-width="12" stroke-linecap="round"/>',
        ]
    elif prop == 'kunai':
        partes += [
            '<path d="M312 224 L370 176 L356 234Z" fill="#dbe4f0" stroke="#111" stroke-width="3"/>',
            '<path d="M346 220 L372 250" stroke="#64748b" stroke-width="9" stroke-linecap="round"/>',
            f'<circle cx="360" cy="244" r="7" fill="{acento}"/>',
        ]
    elif prop == 'varita':
        partes += [
            '<path d="M100 384 L82 104" stroke="#ffd23f" stroke-width="9" stroke-linecap="round"/>',
            '<path d="M82 62 L94 88 L122 92 L101 110 L107 138 L82 123 L57 138 L63 110 L42 92 L70 88Z" fill="#ffd23f" stroke="#fff" stroke-width="3"/>',
        ]
    elif prop == 'escudo':
        partes += [
            f'<circle cx="330" cy="238" r="46" fill="{acento}" opacity=".85" stroke="#fff" stroke-width="5"/>',
            '<path d="M330 210 L330 266 M304 238 L356 238" stroke="#fff" stroke-width="5"/>',
        ]
    elif prop == 'lupa':
        partes += [
            '<circle cx="326" cy="230" r="30" fill="#bff6ff" opacity=".35" stroke="#ffd23f" stroke-width="8"/>',
            '<path d="M348 252 L376 284" stroke="#8b5a2b" stroke-width="10" stroke-linecap="round"/>',
        ]
    elif prop == 'micro':
        partes += [
            '<rect x="304" y="186" width="20" height="64" rx="10" fill="#ff2e88" stroke="#fff" stroke-width="3"/>',
            '<circle cx="314" cy="180" r="18" fill="#e2e8f0" stroke="#111" stroke-width="3"/>',
        ]
    elif prop == 'arco':
        partes += [
            '<path d="M330 150 Q388 230 330 310" fill="none" stroke="#d9a05b" stroke-width="9"/>',
            '<path d="M330 150 L330 310" stroke="#e2e8f0" stroke-width="3"/>',
            '<path d="M318 230 L352 206 L346 244Z" fill="#94a3b8" stroke="#111" stroke-width="2"/>',
        ]
    elif prop == 'pistola':
        partes += [
            '<path d="M300 220 L370 206 L372 236 L316 248Z" fill="#64748b" stroke="#111" stroke-width="3"/>',
            '<path d="M312 246 L330 274 L346 270 L334 244Z" fill="#334155" stroke="#111" stroke-width="2"/>',
            f'<circle cx="366" cy="221" r="5" fill="{acento}"/>',
        ]
    elif prop == 'bola':
        partes += [
            f'<circle cx="344" cy="240" r="34" fill="{acento}" stroke="#fff" stroke-width="4"/>',
            '<path d="M312 230 Q344 216 376 230 M312 252 Q344 238 376 252" fill="none" stroke="#111" stroke-width="3"/>',
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
            '<path d="M316 214 Q340 204 364 214" fill="none" stroke="#111" stroke-width="4"/>',
        ]
    elif prop == 'cinta':
        partes += [
            f'<path d="M310 236 Q356 176 384 220 Q356 208 338 244Z" fill="{acento}" stroke="#fff" stroke-width="3"/>',
            f'<path d="M306 250 Q348 300 384 258" fill="none" stroke="{acento}" stroke-width="8" stroke-linecap="round"/>',
        ]
    elif prop == 'guitarra':
        partes += [
            f'<ellipse cx="344" cy="252" rx="30" ry="38" fill="{acento}" stroke="#fff" stroke-width="3"/>',
            '<rect x="338" y="164" width="12" height="70" fill="#d9a05b" stroke="#111" stroke-width="2"/>',
            '<circle cx="344" cy="258" r="10" fill="#111"/>',
        ]
    else:  # dragón
        partes += [
            '<path d="M306 220 Q360 170 382 210 Q360 200 348 224 Q372 246 348 264 Q330 250 306 254Z" fill="#ff2e88" stroke="#ffd23f" stroke-width="3"/>',
            '<circle cx="362" cy="214" r="4" fill="#fff"/>',
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
