/* ============================================================
   ANIMECHRONICLE — Efectos compartidos (páginas secundarias)
   Personajes flotantes + ataque al abrir noticia + scroll limpio.
   ============================================================ */

const PERSONAJES_ATAQUE = [
  'guerrero', 'espadachina', 'ninja', 'maga', 'mecha', 'detective', 'idol', 'dragon', 'samurai', 'pirata', 'cazador', 'bruja', 'caballero', 'cyborg', 'astronauta', 'skater', 'gamer', 'boxeador', 'bailarina', 'vampiro', 'robotito', 'sirena', 'zorro', 'fenix', 'kraken', 'heroina', 'músico', 'centinela',
];

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

function irArriba() {
  document.documentElement.style.scrollBehavior = 'auto';
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  document.documentElement.scrollTop = 0;
}

window.addEventListener('pageshow', (e) => { if (e.persisted) irArriba(); });

function crearPersonajesFlotantes() {
  const contenedor = document.getElementById('personajes-flotantes');
  if (!contenedor) return;
  let html = '';
  for (let i = 0; i < 11; i++) {
    const p = PERSONAJES_ATAQUE[i % PERSONAJES_ATAQUE.length];
    const anim = ['caer-personaje', 'subir-personaje', 'deriva-personaje'][i % 3];
    const izq = ((i * 37) % 96) + Math.random() * 6;
    const tam = 32 + Math.random() * 52;
    const dur = 18 + Math.random() * 18;
    const ret = i * 2.8 + Math.random() * 2;
    const der = (Math.random() * 260 - 130).toFixed(0);
    const opa = (0.14 + Math.random() * 0.38).toFixed(2);
    html += `<img class="personaje-flotante ${anim}" src="fondos/personajes/${p}.svg" alt=""
      style="left:${izq.toFixed(1)}%;--tam:${tam}px;--dur:${dur}s;--ret:${ret}s;--der:${der}px;--opa:${opa}">`;
  }
  contenedor.innerHTML = html;
}

const Ataque = {
  activo: false,
  mostrar(callback) {
    if (this.activo) return;
    this.activo = true;
    const personaje = PERSONAJES_ATAQUE[Math.floor(Math.random() * PERSONAJES_ATAQUE.length)];
    const grito = (typeof Sonido !== 'undefined') ? Sonido.frase('whoosh') : '¡ATAQUE!';
    if (typeof Sonido !== 'undefined') Sonido.decir(grito, 'ja-JP', 1);
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { setTimeout(() => { this.activo = false; if (callback) callback(); }, 400); return; }
    const capa = document.createElement('div');
    capa.className = 'ataque';
    capa.setAttribute('aria-hidden', 'true');
    capa.innerHTML = `
      <div class="ataque__rayo"></div>
      <div class="ataque__personaje"><img src="fondos/personajes/${personaje}.svg" alt=""></div>
      <div class="ataque__burbuja">${grito}</div>
      <div class="ataque__flash"></div>`;
    document.body.appendChild(capa);
    document.body.classList.add('ataque-activo');
    requestAnimationFrame(() => requestAnimationFrame(() => capa.classList.add('ataque--activo')));
    setTimeout(() => {
      capa.remove();
      document.body.classList.remove('ataque-activo');
      this.activo = false;
      if (callback) callback();
    }, 1750);
  },
};

function abrirConAtaque(url) {
  if (Ataque.activo) return;
  if (typeof Sonido !== 'undefined') Sonido.vibrar(30);
  Ataque.mostrar(() => { irArriba(); window.location.href = url; });
}

crearPersonajesFlotantes();
