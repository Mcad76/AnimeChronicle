/* ============================================================
   ANIMECHRONICLE — Motor de sonido
   Efectos sintetizados (WAV locales) sin dependencias externas.
   ============================================================ */

const Sonido = (() => {
  const CLAVES = {
    click: 'sonidos/click.wav',
    select: 'sonidos/select.wav',
    whoosh: 'sonidos/whoosh.wav',
    open: 'sonidos/open.wav',
    close: 'sonidos/close.wav',
    tab: 'sonidos/tab.wav',
    hover: 'sonidos/hover.wav',
    bgm: 'sonidos/bgm.wav',
  };

  const buffers = {};
  let activo = localStorage.getItem('ac-sonido') !== 'off';
  let musicaActiva = localStorage.getItem('ac-musica') === 'on';
  let nodoMusica = null;
  let ultimoHover = 0;

  function obtener(nombre) {
    if (!buffers[nombre]) {
      const a = new Audio(CLAVES[nombre]);
      a.preload = 'auto';
      buffers[nombre] = a;
    }
    return buffers[nombre];
  }

  function reproducir(nombre, volumen = 0.5) {
    if (!activo || !CLAVES[nombre]) return;
    try {
      const base = obtener(nombre);
      const nodo = base.cloneNode();
      nodo.volume = Math.max(0, Math.min(1, volumen));
      const p = nodo.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    } catch (_) {
      /* el navegador puede bloquear audio hasta el primer gesto */
    }
  }

  function vibrar(ms = 20) {
    try { if (navigator.vibrate) navigator.vibrate(ms); } catch (_) {}
  }

  function sincronizarBotones() {
    const sfx = document.getElementById('btn-sonido');
    const bgm = document.getElementById('btn-musica');
    if (sfx) {
      sfx.textContent = activo ? '🔊' : '🔇';
      sfx.setAttribute('aria-pressed', String(activo));
      sfx.setAttribute('aria-label', activo ? 'Silenciar efectos de sonido' : 'Activar efectos de sonido');
    }
    if (bgm) {
      bgm.textContent = musicaActiva ? '♫' : '♪';
      bgm.setAttribute('aria-pressed', String(musicaActiva));
      bgm.setAttribute('aria-label', musicaActiva ? 'Desactivar música de fondo' : 'Activar música de fondo');
    }
  }

  function alternarSonido() {
    activo = !activo;
    localStorage.setItem('ac-sonido', activo ? 'on' : 'off');
    if (!activo) pararMusica();
    sincronizarBotones();
    if (activo) reproducir('click', 0.5);
    return activo;
  }

  function arrancarMusica() {
    if (nodoMusica) return;
    const nodo = obtener('bgm');
    nodo.loop = true;
    nodo.volume = 0.08;
    nodo.play().then(() => { nodoMusica = nodo; }).catch(() => {});
  }

  function pararMusica() {
    if (nodoMusica) {
      nodoMusica.pause();
      nodoMusica = null;
    }
  }

  function alternarMusica() {
    musicaActiva = !musicaActiva;
    localStorage.setItem('ac-musica', musicaActiva ? 'on' : 'off');
    if (musicaActiva) arrancarMusica(); else pararMusica();
    sincronizarBotones();
    reproducir('click', 0.45);
    return musicaActiva;
  }

  function hover() {
    const ahora = Date.now();
    if (ahora - ultimoHover < 170) return;
    ultimoHover = ahora;
    reproducir('hover', 0.10);
  }

  // Botones de la barra superior
  const btnSfx = document.getElementById('btn-sonido');
  const btnBgm = document.getElementById('btn-musica');
  if (btnSfx) btnSfx.addEventListener('click', alternarSonido);
  if (btnBgm) btnBgm.addEventListener('click', alternarMusica);
  sincronizarBotones();

  return {
    get activo() { return activo; },
    get musicaActiva() { return musicaActiva; },
    reproducir, vibrar, hover,
    alternarSonido, alternarMusica, arrancarMusica, sincronizarBotones,
  };
})();
