/* ============================================================
   ANIMECHRONICLE — Voces otaku
   En lugar de pitidos, la web habla frases míticas de anime.
   Usa speechSynthesis del navegador; si no está disponible,
   cae a los efectos WAV sintetizados que ya incorporábamos.
   ============================================================ */

const Sonido = (() => {
  const CLAVES = {
    click: 'sonidos/click.wav', select: 'sonidos/select.wav',
    whoosh: 'sonidos/whoosh.wav', open: 'sonidos/open.wav',
    close: 'sonidos/close.wav', tab: 'sonidos/tab.wav',
    hover: 'sonidos/hover.wav', bgm: 'sonidos/bgm.wav',
  };

  const FRASES = {
    click:  ['¡Pika!', '¡Pikachu!', '¡Vamos!', '¡Sí!', '¡Genial!', '¡N!'],
    select: ['¡Rasengan!', '¡Bankai!', '¡Sharingan!', '¡Kamehameha!',
             '¡Ultra Instinto!', '¡Ataque de los Titanes!', '¡Chidori!'],
    whoosh: ['¡RASENGAN!', '¡BANKAI!', '¡KAMEHAMEHA!', '¡GOMU GOMU NO!',
             '¡ZANGETSU!', '¡ULTRA INSTINTO!', '¡TENSHI NO HA!'],
    open:   ['¡Aquí vamos!', '¡Empezó el episodio!', '¡Modo ataque activado!',
             '¡Allá vamos, nakama!'],
    close:  ['¡Hasta el próximo episodio!', '¡Nos vemos, nakama!', '¡Fin del episodio!'],
    tab:    ['¡Cambio de estrategia!', '¡Siguiente ronda!', '¡Selecciona, warrior!'],
    hover:  ['¡Eh!', '¡Oye!', '¡Mira!'],
  };

  const buffers = {};
  let activo = localStorage.getItem('ac-sonido') !== 'off';
  let musicaActiva = localStorage.getItem('ac-musica') === 'on';
  let nodoMusica = null;
  let ultimoHover = 0;
  let vozElegida = null;

  function hayVoz() {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  function elegirVoz(lang) {
    if (!hayVoz()) return null;
    if (!vozElegida || vozElegida.lang !== lang) {
      const voces = speechSynthesis.getVoices() || [];
      vozElegida = voces.find(v => v.lang === lang) ||
                   voces.find(v => v.lang && v.lang.startsWith(lang.slice(0, 2)));
    }
    return vozElegida;
  }

  /** Pronuncia una frase. `lang` permite usar voz japonesa en some gritos. */
  function decir(texto, lang = 'es-ES', volumen = 0.95) {
    if (!activo || !texto) return;
    if (!hayVoz()) { reproducirAudio('select', volumen * 0.6); return; }
    try {
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(texto);
      u.lang = lang;
      u.rate = 1.16;
      u.pitch = 1.32;
      u.volume = Math.max(0, Math.min(1, volumen));
      const voz = elegirVoz(lang);
      if (voz) u.voice = voz;
      speechSynthesis.speak(u);
    } catch (_) {
      reproducirAudio('select', volumen * 0.6);
    }
  }

  function frase(tipo) {
    const lista = FRASES[tipo] || FRASES.click;
    return lista[Math.floor(Math.random() * lista.length)];
  }

  /** Respaldo: reproduce el WAV antiguo si no hay síntesis de voz. */
  function reproducirAudio(nombre, volumen = 0.5) {
    if (!activo || !CLAVES[nombre]) return;
    try {
      if (!buffers[nombre]) {
        const a = new Audio(CLAVES[nombre]);
        a.preload = 'auto';
        buffers[nombre] = a;
      }
      const nodo = buffers[nombre].cloneNode();
      nodo.volume = Math.max(0, Math.min(1, volumen));
      const p = nodo.play();
      if (p && typeof p.catch === 'function') p.catch(() => {});
    } catch (_) {}
  }

  function reproducir(nombre, volumen = 0.95) {
    const texto = frase(nombre);
    decir(texto, nombre === 'whoosh' ? 'ja-JP' : 'es-ES', volumen);
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
      sfx.setAttribute('aria-label', activo ? 'Silenciar las voces' : 'Activar las voces');
      sfx.title = activo ? 'Voces otaku: activadas' : 'Voces otaku: silenciadas';
    }
    if (bgm) {
      bgm.textContent = musicaActiva ? '♫' : '♪';
      bgm.setAttribute('aria-pressed', String(musicaActiva));
      bgm.setAttribute('aria-label', musicaActiva ? 'Desactivar música' : 'Activar música');
    }
  }

  function alternarSonido() {
    activo = !activo;
    localStorage.setItem('ac-sonido', activo ? 'on' : 'off');
    if (!activo) {
      if (hayVoz()) speechSynthesis.cancel();
      pararMusica();
    }
    sincronizarBotones();
    if (activo) decir('¡Modo otaku activado!');
    return activo;
  }

  function arrancarMusica() {
    if (nodoMusica) return;
    try {
      if (!buffers.bgm) {
        buffers.bgm = new Audio(CLAVES.bgm);
        buffers.bgm.preload = 'auto';
      }
      const nodo = buffers.bgm;
      nodo.loop = true;
      nodo.volume = 0.08;
      nodo.play().then(() => { nodoMusica = nodo; }).catch(() => {});
    } catch (_) {}
  }

  function pararMusica() {
    if (nodoMusica) { nodoMusica.pause(); nodoMusica = null; }
  }

  function alternarMusica() {
    musicaActiva = !musicaActiva;
    localStorage.setItem('ac-musica', musicaActiva ? 'on' : 'off');
    if (musicaActiva) arrancarMusica(); else pararMusica();
    sincronizarBotones();
    decir(musicaActiva ? '¡Que empiece el combate!' : '¡Pausa!', 'es-ES', 0.8);
    return musicaActiva;
  }

  function hover() {
    const ahora = Date.now();
    if (ahora - ultimoHover < 1100) return;
    ultimoHover = ahora;
    decir(frase('hover'), 'es-ES', 0.55);
  }

  const btnSfx = document.getElementById('btn-sonido');
  const btnBgm = document.getElementById('btn-musica');
  if (btnSfx) btnSfx.addEventListener('click', alternarSonido);
  if (btnBgm) btnBgm.addEventListener('click', alternarMusica);
  if (hayVoz()) speechSynthesis.onvoiceschanged = () => { vozElegida = null; };
  sincronizarBotones();

  return {
    get activo() { return activo; },
    get musicaActiva() { return musicaActiva; },
    reproducir, decir, frase, vibrar, hover,
    alternarSonido, alternarMusica, arrancarMusica, sincronizarBotones,
  };
})();
