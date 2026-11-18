#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnimeChronicle — Personajes homenaje (fan art original).

Arte vectorial propio inspirado en rasgos visuales de franquicias famosas
(ninja naranja, guerrero de ki, capitán de paja, espadachín verde...).
No son imágenes oficiales ni reproducen logotipos.

Uso: python3 generar_personajes_famosos.py
"""

from pathlib import Path
from generar_personajes_reales import personaje_svg

BASE = Path(__file__).resolve().parent
SALIDA = BASE / 'fondos' / 'personajes-famosos'

# id, pelo, ojos, traje, acento, estilo, arma
PERSONAJES = [
    ('ninja-naranja',  '#fde047', '#3b82f6', '#ea580c', '#1d4ed8', 0, 'kunai'),
    ('guerrero-ki',    '#111827', '#e11d48', '#ea580c', '#2563eb', 0, 'guante'),
    ('capitan-paja',   '#7c2d12', '#3b82f6', '#dc2626', '#facc15', 2, 'espada'),
    ('espadachin-verde','#166534', '#22c55e', '#14532d', '#84cc16', 2, 'espada'),
    ('flor-rosa',      '#f472b6', '#e11d48', '#be185d', '#fde047', 1, 'guante'),
    ('principe-saiyan', '#18181b', '#38bdf8', '#1e293b', '#e2e8f0', 0, 'guante'),
    ('detective-lupa', '#1f2937', '#64748b', '#1e3a5f', '#fbbf24', 3, 'lupa'),
    ('guerrera-lunar', '#fef08a', '#f43f5e', '#1e3a8a', '#fde047', 1, 'varita'),
    ('cazador-naranja','#f97316', '#ef4444', '#1c1917', '#f59e0b', 0, 'espada'),
    ('tigre-ki',       '#0f172a', '#facc15', '#1e3a8a', '#fbbf24', 0, 'guante'),
    ('marinero-goma',  '#7c2d12', '#60a5fa', '#dc2626', '#facc15', 2, 'escudo'),
    ('sombra-terror',  '#18181b', '#a855f7', '#27272a', '#ef4444', 3, 'kunai'),
]


def extras(ident):
    """Rasgos distintivos de cada homenaje (sin logotipos oficiales)."""
    if ident == 'ninja-naranja':
        return (
            '<rect x="136" y="122" width="128" height="14" rx="4" fill="#1d4ed8" stroke="#fff" stroke-width="2"/>'
            '<path d="M196 127 q8 -7 14 0 q-7 5 -14 0" fill="none" stroke="#e2e8f0" stroke-width="3"/>'
            '<path d="M150 180 l18 -4 M150 190 l18 -3 M232 176 l18 4 M232 186 l18 3" stroke="#b45309" stroke-width="3" stroke-linecap="round"/>'
        )
    if ident == 'guerrero-ki':
        return (
            '<path d="M120 300 Q60 250 96 190 M280 300 Q340 250 304 190" fill="none" stroke="#fbbf24" stroke-width="6" opacity=".7" stroke-linecap="round"/>'
            '<path d="M200 236 L200 270 M186 252 L214 252" stroke="#2563eb" stroke-width="6"/>'
        )
    if ident in ('capitan-paja', 'marinero-goma'):
        return (
            '<ellipse cx="200" cy="92" rx="104" ry="24" fill="#fde68a" stroke="#78350f" stroke-width="4"/>'
            '<path d="M144 78 Q200 30 256 78 Q200 56 144 78Z" fill="#fbbf24" stroke="#78350f" stroke-width="4"/>'
            '<path d="M144 84 Q200 66 256 84" fill="none" stroke="#dc2626" stroke-width="8"/>'
            '<path d="M226 186 l14 12" stroke="#9f1239" stroke-width="3"/>'
        )
    if ident == 'espadachin-verde':
        return (
            '<path d="M306 230 L384 150" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>'
            '<path d="M312 250 L390 190" stroke="#94a3b8" stroke-width="10" stroke-linecap="round"/>'
        )
    if ident == 'flor-rosa':
        return (
            '<path d="M146 130 q10 -16 20 0 M234 130 q10 -16 20 0" fill="none" stroke="#fbcfe8" stroke-width="4"/>'
            '<circle cx="200" cy="128" r="6" fill="#fbcfe8"/>'
        )
    if ident == 'principe-saiyan':
        return (
            '<path d="M130 250 Q200 224 270 250 L262 278 Q200 258 138 278Z" fill="#e2e8f0" stroke="#64748b" stroke-width="3"/>'
            '<path d="M200 84 L200 118" stroke="#111" stroke-width="6"/>'
        )
    if ident == 'detective-lupa':
        return (
            '<path d="M132 100 Q200 60 268 100 L268 116 Q200 82 132 116Z" fill="#1e293b" stroke="#fbbf24" stroke-width="4"/>'
            '<circle cx="200" cy="252" r="10" fill="#dc2626" stroke="#fff" stroke-width="2"/>'
            '<path d="M190 252 h20" stroke="#fff" stroke-width="2"/>'
        )
    if ident == 'guerrera-lunar':
        return (
            '<circle cx="132" cy="96" r="24" fill="#fef08a" stroke="#fbbf24" stroke-width="3"/>'
            '<circle cx="268" cy="96" r="24" fill="#fef08a" stroke="#fbbf24" stroke-width="3"/>'
            '<path d="M200 130 q12 -10 12 4 q-12 8 -12 -4" fill="#fde047"/>'
        )
    if ident == 'cazador-naranja':
        return (
            '<path d="M120 250 L110 150 M280 250 L290 150" stroke="#78350f" stroke-width="10" stroke-linecap="round"/>'
            '<path d="M200 224 L200 268" stroke="#f59e0b" stroke-width="7"/>'
        )
    if ident == 'tigre-ki':
        return (
            '<path d="M150 176 l-16 -18 M250 176 l16 -18" stroke="#facc15" stroke-width="6" stroke-linecap="round"/>'
            '<circle cx="200" cy="270" r="22" fill="none" stroke="#fbbf24" stroke-width="4" opacity=".8"/>'
        )
    if ident == 'sombra-terror':
        return (
            '<path d="M200 224 L188 244 L200 238 L212 244Z" fill="#ef4444"/>'
            '<path d="M152 196 q22 14 44 -4 M204 192 q22 18 44 4" fill="none" stroke="#1f2937" stroke-width="4"/>'
        )
    return ''


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    grupos = []
    posiciones = [(0, 300, .78), (170, 360, .86), (340, 290, .72),
                  (500, 370, .9), (670, 300, .78), (840, 380, .85),
                  (1010, 290, .75), (1180, 370, .9), (1350, 300, .8),
                  (1500, 370, .75)]
    for i, p in enumerate(PERSONAJES):
        svg = personaje_svg(p).replace('</svg>', extras(p[0]) + '</svg>')
        (SALIDA / (p[0] + '.svg')).write_text(svg + '\n', encoding='utf-8')
        cuerpo = svg[svg.index('>') + 1:svg.rindex('</svg>')]
        x, y, s = posiciones[i % len(posiciones)]
        grupos.append(f'<g transform="translate({x},{y}) scale({s})" opacity=".22">{cuerpo}</g>')

    fondo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="900" viewBox="0 0 1700 900">
  <defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#080616"/><stop offset=".5" stop-color="#1a0f3a"/>
    <stop offset="1" stop-color="#080616"/>
  </linearGradient></defs>
  <rect width="1700" height="900" fill="url(#b)"/>
  {''.join(grupos)}
</svg>'''
    (BASE / 'fondos' / 'personajes-fondo-famosos.svg').write_text(fondo, encoding='utf-8')
    print(f'Generados {len(PERSONAJES)} personajes homenaje')


if __name__ == '__main__':
    main()
