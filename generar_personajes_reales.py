#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeChronicle — Personajes anime detallados (estilo realista).

Dibujo vectorial original con proporciones anime, rostros expresivos,
pelo por capas, sombras y ropa con detalles. Sin imágenes de terceros.

Uso: python3 generar_personajes_reales.py
"""

from pathlib import Path

BASE = Path(__file__).resolve().parent
SALIDA = BASE / 'fondos' / 'personajes-reales'

# id, pelo, ojos, traje, acento, estilo de pelo, arma
PERSONAJES = [
    ('kaito',   '#1e293b', '#38bdf8', '#1d4ed8', '#fbbf24', 0, 'espada'),
    ('sakura',  '#f472b6', '#f43f5e', '#9d174d', '#fde047', 1, 'varita'),
    ('ryu',     '#0f172a', '#ef4444', '#1e3a8a', '#f59e0b', 2, 'guante'),
    ('mei',     '#a855f7', '#a78bfa', '#4c1d95', '#22d3ee', 3, 'kunai'),
    ('taro',    '#f59e0b', '#fbbf24', '#7c2d12', '#84cc16', 0, 'espada'),
    ('yuki',    '#e2e8f0', '#60a5fa', '#1e40af', '#f472b6', 1, 'varita'),
    ('haruto',  '#111827', '#22d3ee', '#0f766e', '#fbbf24', 2, 'pistola'),
    ('aoi',     '#3b82f6', '#38bdf8', '#1e1b4b', '#f43f5e', 3, 'escudo'),
    ('ren',     '#dc2626', '#f87171', '#3f1d1d', '#fbbf24', 0, 'espada'),
    ('mika',    '#f472b6', '#f9a8d4', '#831843', '#a3e635', 1, 'micro'),
    ('shiro',   '#94a3b8', '#e2e8f0', '#334155', '#38bdf8', 2, 'arco'),
    ('kuro',    '#18181b', '#a855f7', '#27272a', '#ef4444', 3, 'kunai'),
    ('hana',    '#fb7185', '#f43f5e', '#5b21b6', '#fde047', 1, 'cinta'),
    ('gou',     '#065f46', '#34d399', '#064e3b', '#fbbf24', 0, 'espada'),
    ('luna',    '#c4b5fd', '#8b5cf6', '#312e81', '#f472b6', 3, 'varita'),
    ('alex',    '#374151', '#f59e0b', '#1f2937', '#22d3ee', 2, 'pistola'),
]


def cabello(pelo, estilo, ident):
    g = f'url(#pelo-{ident})'
    if estilo == 1:  # melena larga con flequillo
        return (
            f'<path d="M132 142 Q126 76 200 72 Q274 76 268 142 L282 322 Q266 312 252 292 '
            f'L248 168 Q200 138 152 168 L148 292 Q134 312 118 322Z" fill="{g}" stroke="#160e2e" stroke-width="4"/>'
            f'<path d="M140 132 Q168 100 200 104 Q232 100 260 132 L246 158 Q224 132 200 134 '
            f'Q176 132 154 158Z" fill="{g}" stroke="#160e2e" stroke-width="3"/>'
            f'<path d="M146 124 Q172 96 202 100" fill="none" stroke="#fff" stroke-width="5" opacity=".35"/>'
        )
    if estilo == 2:  # pelo corto con mechones afilados
        return (
            f'<path d="M128 144 L116 92 L148 116 L156 66 L184 106 L200 58 L216 106 L244 66 '
            f'L252 116 L284 92 L272 144 Q200 110 128 144Z" fill="{g}" stroke="#160e2e" stroke-width="4"/>'
            f'<path d="M150 122 L142 172 L162 148 M250 122 L258 172 L238 148" fill="{g}" stroke="#160e2e" stroke-width="3"/>'
            f'<path d="M140 116 Q168 84 200 86" fill="none" stroke="#fff" stroke-width="5" opacity=".35"/>'
        )
    if estilo == 3:  # gorro / mechón lateral largo
        return (
            f'<path d="M124 148 Q112 74 200 70 Q288 74 276 148 L254 140 Q250 100 200 98 '
            f'Q150 100 146 140Z" fill="{g}" stroke="#160e2e" stroke-width="4"/>'
            f'<path d="M254 138 Q290 180 274 288 L250 276 Q262 196 242 162Z" fill="{g}" stroke="#160e2e" stroke-width="3"/>'
            f'<path d="M136 122 Q172 92 214 94" fill="none" stroke="#fff" stroke-width="5" opacity=".4"/>'
        )
    # estilo 0: capas rectas con puntas hacia abajo
    return (
        f'<path d="M126 146 L118 96 L150 120 L160 70 L188 112 L200 60 L212 112 L240 70 '
        f'L250 120 L282 96 L274 146 Q200 112 126 146Z" fill="{g}" stroke="#160e2e" stroke-width="4"/>'
        f'<path d="M132 140 L128 206 L150 184 L154 138 M268 140 L272 206 L250 184 L246 138" '
        f'fill="{g}" stroke="#160e2e" stroke-width="3"/>'
        f'<path d="M138 120 Q170 88 204 90" fill="none" stroke="#fff" stroke-width="5" opacity=".35"/>'
    )


def arma(prop, acento, ident):
    metal = f'url(#metal-{ident})'
    if prop == 'espada':
        return (f'<path d="M322 176 L146 30" stroke="{metal}" stroke-width="14" stroke-linecap="round"/>'
                '<path d="M322 176 L146 30" stroke="#fff" stroke-width="4" opacity=".7"/>'
                f'<path d="M300 200 L340 160" stroke="{acento}" stroke-width="12" stroke-linecap="round"/>')
    if prop == 'varita':
        return ('<path d="M104 380 L86 106" stroke="#fbbf24" stroke-width="9" stroke-linecap="round"/>'
                '<path d="M86 64 L98 92 L126 96 L104 114 L110 142 L86 126 L62 142 L68 114 L46 96 L74 92Z" '
                f'fill="#fde047" stroke="#fff" stroke-width="4"/><circle cx="86" cy="104" r="7" fill="{acento}"/>')
    if prop == 'kunai':
        return ('<path d="M312 210 L372 158 L356 220Z" fill="' + metal + '" stroke="#111" stroke-width="3"/>'
                f'<path d="M346 206 L374 238" stroke="#64748b" stroke-width="9" stroke-linecap="round"/>'
                f'<circle cx="362" cy="232" r="6" fill="{acento}"/>')
    if prop == 'guante':
        return (f'<circle cx="330" cy="214" r="34" fill="{acento}" stroke="#fff" stroke-width="4"/>'
                '<path d="M304 196 Q330 184 356 196" fill="none" stroke="#111" stroke-width="4"/>')
    if prop == 'pistola':
        return ('<path d="M296 202 L368 188 L370 218 L312 230Z" fill="' + metal + '" stroke="#111" stroke-width="3"/>'
                f'<path d="M308 228 L326 256 L342 252 L330 224Z" fill="#334155" stroke="#111" stroke-width="2"/>'
                f'<circle cx="362" cy="203" r="5" fill="{acento}"/>')
    if prop == 'escudo':
        return (f'<circle cx="330" cy="222" r="46" fill="{acento}" opacity=".9" stroke="#fff" stroke-width="5"/>'
                '<circle cx="330" cy="222" r="33" fill="none" stroke="#111" stroke-width="4"/>'
                '<path d="M330 194 L330 250 M304 222 L356 222" stroke="#fff" stroke-width="5"/>')
    if prop == 'micro':
        return (f'<rect x="304" y="176" width="20" height="64" rx="10" fill="{acento}" stroke="#fff" stroke-width="3"/>'
                f'<circle cx="314" cy="168" r="18" fill="{metal}" stroke="#111" stroke-width="3"/>')
    if prop == 'arco':
        return ('<path d="M330 144 Q390 222 330 300" fill="none" stroke="#d9a05b" stroke-width="10"/>'
                '<path d="M330 144 L330 300" stroke="#e2e8f0" stroke-width="3"/>'
                f'<path d="M316 222 L354 196 L348 238Z" fill="{metal}" stroke="#111" stroke-width="2"/>')
    return (f'<path d="M308 222 Q352 170 380 210 Q352 200 340 226 Q362 246 340 264 Q322 248 308 250Z" '
            f'fill="{acento}" stroke="#fff" stroke-width="3"/>')


def personaje_svg(p):
    ident, pelo, ojos, traje, acento, estilo, prop = p
    defs = f'''<defs>
      <linearGradient id="cuerpo-{ident}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{traje}"/><stop offset=".55" stop-color="{traje}"/>
        <stop offset="1" stop-color="#070512"/>
      </linearGradient>
      <linearGradient id="pelo-{ident}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#fff" stop-opacity=".5"/>
        <stop offset=".3" stop-color="{pelo}"/><stop offset="1" stop-color="{pelo}"/>
      </linearGradient>
      <radialGradient id="iris-{ident}"><stop offset="0" stop-color="#fff"/>
        <stop offset=".4" stop-color="{ojos}"/><stop offset="1" stop-color="#0f172a"/>
      </radialGradient>
      <linearGradient id="metal-{ident}" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#fff"/><stop offset=".5" stop-color="#94a3b8"/>
        <stop offset="1" stop-color="#475569"/>
      </linearGradient>
    </defs>'''

    s = [defs,
         '<ellipse cx="200" cy="548" rx="86" ry="13" fill="#000" opacity=".5"/>',
         f'<circle cx="200" cy="270" r="172" fill="none" stroke="{acento}" stroke-width="2" opacity=".3" stroke-dasharray="16 10"/>',
         f'<circle cx="200" cy="270" r="202" fill="none" stroke="{acento}" stroke-width="1" opacity=".15"/>',
         # capa / bufanda
         f'<path d="M132 246 Q56 350 84 508 Q140 492 158 448 L164 272Z" fill="{pelo}" opacity=".55"/>',
         f'<path d="M268 246 Q344 350 316 508 Q260 492 242 448 L236 272Z" fill="{pelo}" opacity=".55"/>',
         # piernas
         '<path d="M158 400 L150 516 L184 516 L190 400Z" fill="#15122f" stroke="' + acento + '" stroke-width="3"/>',
         '<path d="M210 400 L216 516 L250 516 L242 400Z" fill="#15122f" stroke="' + acento + '" stroke-width="3"/>',
         f'<path d="M154 448 L186 448 M214 448 L246 448" stroke="{acento}" stroke-width="6" opacity=".8"/>',
         f'<path d="M146 512 L188 512 L194 540 L136 540Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
         f'<path d="M212 512 L254 512 L264 540 L206 540Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
         # torso
         f'<path d="M132 240 Q200 214 268 240 L282 402 Q200 424 118 402Z" fill="url(#cuerpo-{ident})" stroke="{acento}" stroke-width="4"/>',
         f'<path d="M160 238 L200 276 L240 238 L258 250 L200 296 L142 250Z" fill="{acento}" opacity=".85"/>',
         f'<path d="M200 292 L200 404" stroke="{acento}" stroke-width="4" opacity=".8"/>',
         f'<path d="M140 262 L118 290 L132 306 L154 282Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
         f'<path d="M260 262 L282 290 L268 306 L246 282Z" fill="url(#metal-{ident})" stroke="#111" stroke-width="3"/>',
         f'<rect x="120" y="350" width="160" height="18" fill="{acento}" stroke="#111" stroke-width="3"/>',
         f'<rect x="188" y="348" width="24" height="22" rx="4" fill="url(#metal-{ident})" stroke="#111" stroke-width="2"/>',
         f'<path d="M150 320 L176 326 M224 326 L250 320" stroke="#fff" stroke-width="2" opacity=".3"/>',
         # brazos
         f'<path d="M136 262 L92 366" stroke="url(#cuerpo-{ident})" stroke-width="26" stroke-linecap="round"/>',
         f'<path d="M264 262 L310 190" stroke="url(#cuerpo-{ident})" stroke-width="26" stroke-linecap="round"/>',
         f'<circle cx="90" cy="370" r="15" fill="#ffd9b3" stroke="#7a4a35" stroke-width="2"/>',
         f'<circle cx="312" cy="187" r="15" fill="#ffd9b3" stroke="#7a4a35" stroke-width="2"/>',
         # cuello y cara
         '<rect x="186" y="206" width="28" height="34" rx="6" fill="#f0c19c" stroke="#7a4a35" stroke-width="2"/>',
         '<path d="M140 128 Q142 202 200 218 Q258 202 260 128 Q256 90 200 86 Q144 90 140 128Z" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="4"/>',
         '<ellipse cx="138" cy="160" rx="10" ry="15" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="3"/>',
         '<ellipse cx="262" cy="160" rx="10" ry="15" fill="#ffd9b3" stroke="#2a1a3a" stroke-width="3"/>',
         # ojos anime grandes
         '<path d="M154 156 Q174 138 194 157 Q174 178 154 156Z" fill="#fff" stroke="#2a1a3a" stroke-width="3"/>',
         '<path d="M206 157 Q226 138 246 156 Q226 178 206 157Z" fill="#fff" stroke="#2a1a3a" stroke-width="3"/>',
         f'<circle cx="175" cy="157" r="11" fill="url(#iris-{ident})"/>',
         f'<circle cx="225" cy="157" r="11" fill="url(#iris-{ident})"/>',
         '<circle cx="175" cy="157" r="5" fill="#0f172a"/><circle cx="225" cy="157" r="5" fill="#0f172a"/>',
         '<circle cx="179" cy="152" r="4" fill="#fff"/><circle cx="229" cy="152" r="4" fill="#fff"/>',
         '<circle cx="170" cy="162" r="2" fill="#fff" opacity=".85"/><circle cx="220" cy="162" r="2" fill="#fff" opacity=".85"/>',
         f'<path d="M152 142 Q174 130 196 142 M204 142 Q226 130 248 142" fill="none" stroke="#2a1a3a" stroke-width="5" stroke-linecap="round"/>',
         f'<path d="M156 136 Q176 126 194 136 M206 136 Q224 126 244 136" fill="none" stroke="{pelo}" stroke-width="5" stroke-linecap="round"/>',
         '<path d="M197 176 L193 190 L201 190" fill="none" stroke="#c98f6e" stroke-width="2.5" stroke-linecap="round"/>',
         '<path d="M185 199 Q200 210 215 199" fill="none" stroke="#8a3552" stroke-width="3.5" stroke-linecap="round"/>',
         '<ellipse cx="158" cy="186" rx="9" ry="4" fill="#f87171" opacity=".25"/>',
         '<ellipse cx="242" cy="186" rx="9" ry="4" fill="#f87171" opacity=".25"/>',
         cabello(pelo, estilo, ident),
         arma(prop, acento, ident),
         ]

    return ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="560" viewBox="0 0 400 560">'
            + ''.join(s) + '</svg>')


def fondo():
    """Fondo ancho con varios héroes en silueta neón."""
    posiciones = [(0, 300, .78), (170, 360, .86), (340, 290, .72),
                  (500, 370, .9), (670, 300, .78), (840, 380, .85),
                  (1010, 290, .75), (1180, 370, .9), (1350, 300, .8),
                  (1500, 370, .75)]
    grupos = []
    for (x, y, s), p in zip(posiciones, PERSONAJES):
        cuerpo = personaje_svg(p)
        cuerpo = cuerpo[cuerpo.index('>') + 1:cuerpo.rindex('</svg>')]
        grupos.append(f'<g transform="translate({x},{y}) scale({s})" opacity=".22">{cuerpo}</g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="900" viewBox="0 0 1700 900">
  <defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#080616"/><stop offset=".5" stop-color="#1a0f3a"/>
    <stop offset="1" stop-color="#080616"/>
  </linearGradient></defs>
  <rect width="1700" height="900" fill="url(#b)"/>
  {''.join(grupos)}
</svg>'''
    (BASE / 'fondos' / 'personajes-fondo-real.svg').write_text(svg, encoding='utf-8')
    print('Fondo con personajes reales generado')


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for p in PERSONAJES:
        (SALIDA / (p[0] + '.svg')).write_text(personaje_svg(p) + '\n', encoding='utf-8')
    fondo()
    print(f'Generados {len(PERSONAJES)} personajes anime en {SALIDA}')


if __name__ == '__main__':
    main()
