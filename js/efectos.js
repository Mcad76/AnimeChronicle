/* ============================================================
   ANIMECHRONICLE — Efectos compartidos (páginas secundarias)
   Personajes flotantes + ataque al abrir noticia + scroll limpio.
   ============================================================ */

const PERSONAJES_ATAQUE = PERSONAJES;

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

function irArriba() {
  document.documentElement.style.scrollBehavior = 'auto';
  window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  document.documentElement.scrollTop = 0;
}

window.addEventListener('pageshow', (e) => { if (e.persisted) irArriba(); });


const Ataque = {
  activo: false,
  mostrar(callback, gritoPersonalizado) {
    if (this.activo) return;
    this.activo = true;
    const personaje = PERSONAJES_ATAQUE[Math.floor(Math.random() * PERSONAJES_ATAQUE.length)];
    const grito = gritoPersonalizado || ((typeof Sonido !== 'undefined') ? Sonido.frase('whoosh') : '¡ATAQUE!');
    if (typeof Sonido !== 'undefined') Sonido.decir(grito, 'ja-JP', 1);
    const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) { setTimeout(() => { this.activo = false; if (callback) callback(); }, 400); return; }
    const capa = document.createElement('div');
    capa.className = 'ataque';
    capa.setAttribute('aria-hidden', 'true');
    capa.innerHTML = `
      <div class="ataque__rayo"></div>
      <div class="ataque__personaje"><img src="fondos/personajes-famosos/${personaje}.svg" alt=""></div>
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

function abrirConAtaque(url, grito) {
  if (Ataque.activo) return;
  if (typeof Sonido !== 'undefined') Sonido.vibrar(30);
  Ataque.mostrar(() => { irArriba(); window.location.href = url; }, grito);
}

