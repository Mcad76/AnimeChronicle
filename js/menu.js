/* ============================================================
   ANIMECHRONICLE — Menú persistente (compartido por todas las páginas)
   ============================================================ */

(() => {
  const btn = document.getElementById('menu-btn');
  const desplegable = document.getElementById('menu-desplegable');

  // Rellenar las secciones si la página no lo ha hecho todavía
  const menuSecciones = document.getElementById('menu-secciones');
  if (menuSecciones && !menuSecciones.children.length &&
      typeof SECCIONES !== 'undefined') {
    menuSecciones.innerHTML = '<div class="menu-desplegable__titulo">Secciones</div>' +
      SECCIONES.map(s => `<a href="index.html#${s.id}" style="--secc-color:${s.color}">${s.nombre}</a>`).join('');
  }

  if (!btn || !desplegable) return;

  function alternar(forzar) {
    const abierto = typeof forzar === 'boolean' ? forzar : desplegable.hidden;
    desplegable.hidden = !abierto;
    btn.setAttribute('aria-expanded', String(abierto));
    btn.setAttribute('aria-label', abierto ? 'Cerrar menú de secciones' : 'Abrir menú de secciones');
    btn.innerHTML = abierto ? '&#10005;' : '&#9776;';
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (typeof Sonido !== 'undefined') Sonido.reproducir('click', 0.45);
    alternar();
  });

  desplegable.addEventListener('click', (e) => {
    if (e.target.closest('a')) alternar(false);
  });

  document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-wrap')) alternar(false);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !desplegable.hidden) {
      alternar(false);
      btn.focus();
    }
  });
})();
