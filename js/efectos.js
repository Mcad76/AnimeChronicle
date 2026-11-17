/* ============================================================
   ANIMECHRONICLE — Efectos compartidos (páginas secundarias)
   Personajes flotantes + ataque al abrir noticia + scroll limpio.
   ============================================================ */

const PERSONAJES_ATAQUE = [
  'guerrero', 'espadachina', 'ninja', 'maga', 'mecha', 'detective', 'idol', 'dragon',
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
  for (let i = 0; i < 14; i++) {
    const p = PERSONAJES_ATAQUE[i % PERSONAJES_ATAQUE.length];
    const izq = Math.random() * 100;
    const tam = 34 + Math.random() * 48;
    const dur = 14 + Math.random() * 16;
    const ret = -Math.random() * 26;
    const der = (Math.random() * 260 - 130).toFixed(0);
    const opa = (0.18 + Math.random() * 0.34).toFixed(2);
    html += `<img class="personaje-flotante" src="fondos/personajes/${p}.svg" alt=""
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
