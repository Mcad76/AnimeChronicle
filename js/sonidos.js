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
    hover: 'sonidos/hover.wav',
  };

  const FRASES = {
    click: [
      '¡Pika!', '¡Pikachu!', '¡Vamos!', '¡Sí!', '¡Genial!', '¡N!', '¡Yey!',
      '¡Bien!', '¡Perfecto!', '¡Eh!', '¡Oh!', '¡Guau!', '¡Listo!', '¡Pulsa!',
      '¡Activa!', '¡Vamos allá!', '¡Sigue!', '¡Toma!', '¡Eso!', '¡Ale!',
      '¡Hecho!', '¡Genial, nakama!', '¡Go!', '¡Dale!', '¡Pum!',
    ],
    select: [
      '¡Rasengan!', '¡Chidori!', '¡Kamehameha!', '¡Bankai!', '¡Sharingan!',
      '¡Rinnegan!', '¡Ultra Instinto!', '¡Gear Second!', '¡Gear Fourth!',
      '¡Haki!', '¡Nen!', '¡Stand!', '¡Ataque de los Titanes!', '¡ZanGetsu!',
      '¡Getsuga Tenshou!', '¡Gomu Gomu no!', '¡Tenshi no Ha!', '¡Amaterasu!',
      '¡Susanoo!', '¡Final Flash!', '¡Galick Gun!', '¡Spirit Bomb!',
      '¡Meteor!', '¡Senjutsu!', '¡Kurama!', '¡Sukuna!', '¡Domain Expansion!',
      '¡Iaido!', '¡Mugetsu!', '¡Kamehameha!',
    ],
    whoosh: [
      '¡RASENGAN!', '¡BANKAI!', '¡KAMEHAMEHA!', '¡CHIDORI!', '¡ZANGETSU!',
      '¡ULTRA INSTINTO!', '¡TENSHI NO HA!', '¡GETSUGA TENSHŌ!',
      '¡GOMU GOMU NO GATLING!', '¡AMATERASU!', '¡SUSANOO!', '¡SENJUTSU!',
      '¡CIEN VICTORIAS!', '¡FULL COUNTER!', '¡ÚLTIMO RECURSO!', '¡IZAYOI!',
      '¡KAGUTSUCHI!', '¡BARYON MODE!', '¡EXPANSIÓN DE DOMINIO!', '¡MAHŌ!',
      '¡PIKA PIKA!', '¡GOD SLICE!', '¡LUNA CRECIENTE!', '¡TITÁN!',
      '¡RAYO CELESTIAL!', '¡PUÑO DEL DRAGÓN!', '¡ESPADA DE LUZ!', '¡METEORO!',
    ],
    open: [
      '¡Aquí vamos!', '¡Empezó el episodio!', '¡Modo ataque activado!',
      '¡Allá vamos, nakama!', '¡Que comience el combate!', '¡Atentos!',
      '¡Listos, acción!', '¡A por todas!', '¡Desplegar equipamiento!',
      '¡Sistema activado!', '¡Vamos a ver esto!', '¡He decidido!',
      '¡A ventaja!', '¡Combate iniciado!', '¡Episodio nuevo!',
    ],
    close: [
      '¡Hasta el próximo episodio!', '¡Nos vemos, nakama!', '¡Fin del episodio!',
      '¡Retirada!', '¡Hasta luego!', '¡Misión cumplida!', '¡Buen combate!',
      '¡Descanso!', '¡Nos vemos pronto!', '¡Se acabó por hoy!',
      '¡Guardado!', '¡Gracias por ver!', '¡Hasta la victoria!', '¡Cerrado!',
    ],
    tab: [
      '¡Cambio de estrategia!', '¡Siguiente ronda!', '¡Selecciona, warrior!',
      '¡Otro objetivo!', '¡Cambio de escenario!', '¡Vamos con esta!',
      '¡Nueva ruta!', '¡Elegida!', '¡Siguiente!', '¡Cambio de plan!',
      '¡Aquí vamos!', '¡Modo alternativo!', '¡Otro género!', '¡Adelante!',
    ],
    hover: [
      '¡Eh!', '¡Oye!', '¡Mira!', '¡Mmm!', '¡Uoh!', '¡Hmm!', '¡Hey!',
      '¡Interesante!', '¡Ahí!', '¡Cuidado!', '¡Míralo!', '¡Listo!',
    ],
  };

  // Frases ligadas a la franquicia de la que habla cada noticia
  const FRASES_FRANQUICIA = [
    { k: ['one piece', 'luffy', 'zoro', 'nami'], f: '¡GOMU GOMU NO!' },
    { k: ['dragon ball', 'goku', 'vegeta', 'gohan'], f: '¡KAMEHAMEHA!' },
    { k: ['naruto', 'boruto', 'sasuke', 'kakashi'], f: '¡RASENGAN!' },
    { k: ['demon slayer', 'kimetsu', 'tanjiro', 'nezuko'], f: '¡TENSHI NO HA!' },
    { k: ['jujutsu', 'gojo', 'yuji', 'sukuna'], f: '¡EXPANSION DE DOMINIO!' },
    { k: ['attack on titan', 'shingeki', 'eren'], f: '¡ATAQUE DE LOS TITANES!' },
    { k: ['my hero', 'boku no hero', 'deku', 'bakugo'], f: '¡SMASH!' },
    { k: ['chainsaw man', 'denji', 'makima'], f: '¡CHAINSAW MAN!' },
    { k: ['spy x family', 'anya', 'loid', 'yor'], f: '¡WAKU WAKU!' },
    { k: ['pokemon', 'pikachu', 'ash ketchum'], f: '¡PIKACHU!' },
    { k: ['gundam', 'mecha', 'evangelion'], f: '¡SABER LAUNCH!' },
    { k: ['sailor moon', 'usagi'], f: '¡MOON PRISM POWER!' },
    { k: ['bleach', 'ichigo', 'rukia'], f: '¡BANKAI!' },
    { k: ['hunter x hunter', 'gon', 'killua'], f: '¡NEN!' },
    { k: ['death note', 'light yagami', 'ryuk'], f: '¡DEATH NOTE!' },
    { k: ['jojo', 'jotaro'], f: '¡ZA WARUDO!' },
    { k: ['one punch', 'saitama'], f: '¡UN SOLO GOLPE!' },
    { k: ['black clover', 'asta', 'yuno'], f: '¡MAGIA NEGRA!' },
    { k: ['solo leveling', 'jin woo'], f: '¡ARISE!' },
    { k: ['frieren'], f: '¡ZOLTRAAK!' },
    { k: ['oshi no ko', 'ai hoshino'], f: '¡BRILLA, ESTRELLA!' },
    { k: ['re:zero', 'subaru'], f: '¡RETORNO POR LA MUERTE!' },
    { k: ['tensura', 'rimuru'], f: '¡SLIME SUPREMO!' },
    { k: ['konosuba', 'kazuma'], f: '¡EXPLOSION!' },
    { k: ['jujutsu kaisen'], f: '¡DOMINIO EXPANSION!' },
    { k: ['anime', 'serie', 'estreno', 'manga', 'pelicula', 'temporada'], f: '¡A POR ESTA NOTICIA!' },
  ];

  /** Elige un grito según la noticia pulsada. */
  function frasePara(texto) {
    const t = (texto || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    for (const item of FRASES_FRANQUICIA) {
      if (item.k.some(clave => t.includes(clave))) return item.f;
    }
    return frase('whoosh');
  }

  const buffers = {};
  const ultimaFrasePorTipo = {};
  let activo = localStorage.getItem('ac-sonido') === 'on';
  let ultimoHover = 0;
  let vozElegida = null;
  let vocesCache = null;

  function hayVoz() {
    return typeof window !== 'undefined' && 'speechSynthesis' in window;
  }

  function elegirVoz(lang) {
    if (!hayVoz()) return null;
    if (!vozElegida || vozElegida.lang !== lang) {
      // getVoices() puede ser costoso la primera vez: se consulta una sola vez.
      if (!vocesCache) vocesCache = speechSynthesis.getVoices() || [];
      vozElegida = vocesCache.find(v => v.lang === lang) ||
                   vocesCache.find(v => v.lang && v.lang.startsWith(lang.slice(0, 2)));
    }
    return vozElegida;
  }

  /** Pronuncia una frase. `interrumpir=false` evita cortar otras voces (hover). */
  function decir(texto, lang = 'es-ES', volumen = 0.95, interrumpir = true) {
    if (!activo || !texto) return;
    if (!hayVoz()) { reproducirAudio('select', volumen * 0.6); return; }
    try {
      if (interrumpir) speechSynthesis.cancel();
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
    const anterior = ultimaFrasePorTipo[tipo];
    // Evita repetir la misma frase dos veces seguidas
    const opciones = lista.length > 1 ? lista.filter(x => x !== anterior) : lista;
    const elegida = opciones[Math.floor(Math.random() * opciones.length)];
    ultimaFrasePorTipo[tipo] = elegida;
    return elegida;
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
    if (sfx) {
      sfx.textContent = activo ? '🔊 ON' : '🔇 OFF';
      sfx.setAttribute('aria-pressed', String(activo));
      sfx.setAttribute('aria-label', activo ? 'Desactivar las voces' : 'Activar las voces');
      sfx.title = activo ? 'Voces otaku: activadas (pulsa para silenciar)' : 'Voces otaku: desactivadas (pulsa para activar)';
    }
  }

  function alternarSonido() {
    activo = !activo;
    localStorage.setItem('ac-sonido', activo ? 'on' : 'off');
    if (!activo) {
      if (hayVoz()) speechSynthesis.cancel();
    }
    sincronizarBotones();
    if (activo) decir('¡Modo otaku activado!');
    return activo;
  }

  function hover() {
    const ahora = Date.now();
    if (ahora - ultimoHover < 2400) return;
    ultimoHover = ahora;
    decir(frase('hover'), 'es-ES', 0.55, false);
  }

  const btnSfx = document.getElementById('btn-sonido');
  if (btnSfx) btnSfx.addEventListener('click', alternarSonido);
  if (hayVoz()) {
    speechSynthesis.onvoiceschanged = () => { vocesCache = null; vozElegida = null; };
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) speechSynthesis.cancel();
    });
  }
  sincronizarBotones();

  return {
    get activo() { return activo; },
    reproducir, decir, frase, frasePara, vibrar, hover,
    alternarSonido, sincronizarBotones,
  };
})();
