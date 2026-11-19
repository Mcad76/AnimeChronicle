/* ============================================================
   ANIMECHRONICLE — Cambio de tema con tres clics en el título
   ============================================================ */
(() => {
  const CLAVE = 'ac-tema-v2';
  if (localStorage.getItem(CLAVE) === 'neon') {
    document.documentElement.classList.add('tema-neon');
  }
  let clics = [];
  document.querySelectorAll('.brand').forEach(brand => {
    brand.addEventListener('click', (e) => {
      const ahora = Date.now();
      clics = clics.filter(t => ahora - t < 1400);
      clics.push(ahora);
      if (clics.length >= 3) {
        clics = [];
        e.preventDefault();
        const neon = document.documentElement.classList.toggle('tema-neon');
        localStorage.setItem(CLAVE, neon ? 'neon' : 'principal');
        try { if (typeof Sonido !== 'undefined') Sonido.reproducir('tab', 0.5); } catch (_) {}
      }
    });
  });
})();
