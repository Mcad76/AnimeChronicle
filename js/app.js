/* ============================================================
   ANIMECHRONICLE — Lógica de la aplicación
   - Portada por secciones con rotación diaria
   - Pestañas por género, hero destacado, archivo y modal
   - Animaciones y sonidos al interactuar
   ============================================================ */

const MS_DIA = 86400000;
const ANCLAJE = new Date(2026, 0, 1);
const HOY = new Date();
let generoActual = 'todos';

const fechaLarga = new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const fechaCorta = new Intl.DateTimeFormat('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });

const DIA_ACTUAL = Math.round((new Date(HOY.getFullYear(), HOY.getMonth(), HOY.getDate()) - ANCLAJE) / MS_DIA);
const TAMANO_SECCION = 6;

function seccionPorId(id) { return SECCIONES.find(s => s.id === id); }
function indiceSeccion(id) { return SECCIONES.findIndex(s => s.id === id); }
function generoPorId(id) { return GENEROS.find(g => g.id === id); }

function inicioRotacion(idx, dia) {
  return (((dia * 5 + idx) % TAMANO_SECCION) + TAMANO_SECCION) % TAMANO_SECCION;
}
function sumarDias(d, n) { return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n); }

function tieneFechaReal(n) { return !!(n.fecha && !isNaN(new Date(n.fecha).getTime())); }

function noticiasDeHoy(idxSeccion, genero = generoActual) {
  const sec = SECCIONES[idxSeccion];
  const lista = NOTICIAS.filter(n => n.sec === sec.id &&
    (genero === 'todos' || (n.genero || 'todos') === genero));
  const ordenadas = lista.filter(tieneFechaReal).sort((a, b) =>
    (b.viral || 0) - (a.viral || 0) || new Date(b.fecha) - new Date(a.fecha));
  if (ordenadas.length) return ordenadas.slice(0, 3);
  if (!lista.length) return [];
  const ini = inicioRotacion(idxSeccion, DIA_ACTUAL);
  return [0, 1, 2].map(k => lista[(ini + k) % lista.length]);
}

function fechaPublicacion(articulo, idxSeccion) {
  for (let d = DIA_ACTUAL; d >= DIA_ACTUAL - (TAMANO_SECCION - 1); d--) {
    const ini = inicioRotacion(idxSeccion, d);
    if ([0, 1, 2].some(k => (ini + k) % TAMANO_SECCION === articulo.slot)) {
      return sumarDias(ANCLAJE, d);
    }
  }
  return sumarDias(ANCLAJE, DIA_ACTUAL);
}

const FECHAS_PUBLICACION = {};
NOTICIAS.forEach(n => {
  FECHAS_PUBLICACION[n.id] = tieneFechaReal(n)
    ? new Date(n.fecha)
    : fechaPublicacion(n, indiceSeccion(n.sec));
});

let IDS_HOY = new Set();
function actualizarIdsHoy() {
  IDS_HOY = new Set();
  SECCIONES.forEach((_, i) => noticiasDeHoy(i).forEach(n => IDS_HOY.add(n.id)));
}
actualizarIdsHoy();

function minutosLectura(articulo) {
  const palabras = (articulo.entradilla + ' ' + (articulo.cuerpo || []).join(' ')).split(/\s+/).length;
  return Math.max(1, Math.round(palabras / 200));
}

/* ---------- Imágenes ---------- */
const PERSONAJES_FALLBACK = [
  'guerrero', 'espadachina', 'ninja', 'maga', 'mecha', 'detective', 'idol', 'dragon',
];

function imgFallback(el, color) {
  el.onerror = null;
  const personaje = PERSONAJES_FALLBACK[Math.floor(Math.random() * PERSONAJES_FALLBACK.length)];
  el.src = 'fondos/personajes/' + personaje + '.svg';
  el.style.objectFit = 'contain';
  el.style.background = 'radial-gradient(circle at 50% 40%, ' + color + '55, #080616)';
}

function imagenHTML(noticia, clase, color) {
  return `<div class="${clase}">
    <img src="${noticia.image}" alt="${noticia.titulo}" loading="lazy"
         onerror="imgFallback(this,'${color}')">
  </div>`;
}

function categoriaHTML(noticia, extra = '') {
  const sec = seccionPorId(noticia.sec);
  return `<div class="noticia__cat" style="--secc-color:${sec.color}">
    <span class="noticia__cat-nombre">${sec.nombre}</span>${extra}
  </div>`;
}

/* ---------- Tarjetas ---------- */
function tarjetaHTML(noticia, variante = '', i = 0) {
  const color = seccionPorId(noticia.sec).color;
  const fecha = FECHAS_PUBLICACION[noticia.id];
  const tam = i === 0 ? 'tarjeta--ancho' : 'tarjeta--estrecho';
  return `<article class="tarjeta ${tam} ${variante}" data-id="${noticia.id}"
             style="--secc-color:${color};--i:${i}" tabindex="0" role="button"
             aria-label="Leer noticia: ${noticia.titulo}">
    ${categoriaHTML(noticia)}
    ${imagenHTML(noticia, 'tarjeta__img', color)}
    <div class="tarjeta__cuerpo">
      <h3 class="tarjeta__titulo">${noticia.titulo}</h3>
      <p class="tarjeta__entradilla">${noticia.entradilla}</p>
      <div class="tarjeta__meta">${noticia.autor} · ${fechaCorta.format(fecha)} · ${minutosLectura(noticia)} min</div>
    </div>
  </article>`;
}

const AD_HTML = '<aside class="ad ad--inline"><span class="ad__label">PUBLICIDAD</span><strong>PON AQUÍ TU PUBLICIDAD</strong><span class="ad__small">¿Tu marca también es otaku? Escríbenos</span></aside>';

/* ---------- Hero de destacadas ---------- */
function construirHero() {
  const hueco = document.getElementById('hero');
  if (!hueco) return;
  const lista = NOTICIAS
    .filter(n => generoActual === 'todos' || (n.genero || 'todos') === generoActual)
    .filter(tieneFechaReal)
    .sort((a, b) => (b.viral || 0) - (a.viral || 0) || new Date(b.fecha) - new Date(a.fecha))
    .slice(0, 3);
  if (!lista.length) { hueco.innerHTML = ''; return; }
  const nombreGenero = generoPorId(generoActual).nombre;
  hueco.innerHTML = `
    <div class="wrap">
      <div class="hero__titulo">✦ Destacadas · ${nombreGenero}</div>
      <div class="hero">
        ${tarjetaHTML(lista[0], 'tarjeta--grande hero__principal', 0)}
        ${lista.slice(1).map((n, i) => tarjetaHTML(n, 'tarjeta--pequena hero__lateral', i + 1)).join('')}
      </div>
    </div>`;
}

/* ---------- Radar de tendencias ---------- */
function construirTendencias() {
  const datos = (typeof TENDENCIAS !== 'undefined') ? TENDENCIAS : { es: [], mundo: [] };
  const paneles = [
    { id: 'panel-es', titulo: '🇪🇸 LO MÁS VISTO EN ESPAÑA', sub: 'Lo que triunfa aquí', datos: datos.es },
    { id: 'panel-mundo', titulo: '🌍 TRENDING MUNDIAL', sub: 'Lo que arrasa en el planeta', datos: datos.mundo },
  ];
  paneles.forEach(panel => {
    const hueco = document.getElementById(panel.id);
    if (!hueco) return;
    const filas = (panel.datos || []).map((x, i) => {
      const n = NOTICIAS.find(y => y.url === x.url);
      const ident = n ? n.id : '';
      return `<a class="tendencia ${i === 0 ? 'tendencia--top' : ''}" ${ident ? `data-id="${ident}"` : `href="${x.url}"`}
                 style="--i:${i}" tabindex="0" role="button">
        <span class="tendencia__num">${String(i + 1).padStart(2, '0')}</span>
        <img src="${x.image}" alt="" loading="lazy" onerror="imgFallback(this,'#ff2e88')">
        <span class="tendencia__info">
          <strong>${x.nombre}</strong>
          <small>${x.noticias} menciones · ${x.titulo.slice(0, 68)}…</small>
        </span>
        <span class="tendencia__flecha">↗</span>
      </a>`;
    }).join('');
    hueco.innerHTML = `
      <h3 class="panel-tendencia__titulo">${panel.titulo}</h3>
      <p class="panel-tendencia__sub">${panel.sub}</p>
      <div class="panel-tendencia__lista">${filas}</div>`;
  });
}

/* ---------- Glosario ---------- */
let categoriaGlosario = 'todas';

function construirCategoriasGlosario() {
  const hueco = document.getElementById('glosario-categorias');
  if (!hueco) return;
  const botones = [{ id: 'todas', nombre: 'Todo', icono: '✦' }]
    .concat(CATEGORIAS_GLOSARIO)
    .map(c => `<button type="button" data-cat="${c.id}"
      class="glosario__cat ${c.id === categoriaGlosario ? 'activa' : ''}">
      ${c.icono} ${c.nombre}</button>`).join('');
  hueco.innerHTML = botones;
}

function construirGlosario() {
  const lista = document.getElementById('glosario-lista');
  if (!lista || typeof GLOSARIO === 'undefined') return;
  const buscar = document.getElementById('glosario-buscar').value.trim().toLowerCase();
  const vocab = GLOSARIO.filter(x =>
    (categoriaGlosario === 'todas' || x.c === categoriaGlosario) &&
    (!buscar || (x.t + ' ' + x.d).toLowerCase().includes(buscar)));
  const cat = CATEGORIAS_GLOSARIO.find(c => c.id === categoriaGlosario);
  document.getElementById('glosario-contador').textContent = `${vocab.length} términos`;
  document.getElementById('glosario-vacio').hidden = vocab.length > 0;
  lista.innerHTML = vocab.map((x, i) => `
    <article class="glosario__termino" style="--i:${i}">
      <span class="glosario__cat-tag">${cat && categoriaGlosario !== 'todas' ? cat.icono + ' ' + cat.nombre : (CATEGORIAS_GLOSARIO.find(c => c.id === x.c) || {}).icono}</span>
      <h3>${x.t}</h3>
      <p>${x.d}</p>
    </article>`).join('');
}

/* ---------- Navegación, pestañas y ticker ---------- */
function construirNavegacion() {
  const tabs = document.getElementById('tabs-generos');
  if (tabs) {
    tabs.innerHTML = GENEROS.map(g =>
      `<button type="button" data-genero="${g.id}" class="${g.id === generoActual ? 'activa' : ''}"
        aria-pressed="${g.id === generoActual}">${g.nombre}</button>`).join('') +
      '<button type="button" data-vista="glosario" class="tabs-generos__glosario">📖 Glosario</button>';
  }
  const nav = document.getElementById('nav-secciones');
  const accesos = document.getElementById('accesos-rapidos');
  const selector = document.getElementById('archivo-seccion');
  const menuSecciones = document.getElementById('menu-secciones');
  if (menuSecciones) menuSecciones.innerHTML = '<div class="menu-desplegable__titulo">Secciones</div>';
  SECCIONES.forEach(s => {
    nav.insertAdjacentHTML('beforeend',
      `<a href="#${s.id}" style="--secc-color:${s.color}">${s.nombre}</a>`);
    if (accesos) accesos.insertAdjacentHTML('beforeend',
      `<a class="acceso" href="#${s.id}" style="--secc-color:${s.color}">${s.nombre}</a>`);
    if (menuSecciones) menuSecciones.insertAdjacentHTML('beforeend',
      `<a href="#${s.id}" style="--secc-color:${s.color}">${s.nombre}</a>`);
    selector.insertAdjacentHTML('beforeend', `<option value="${s.id}">${s.nombre}</option>`);
  });
}

function construirTicker() {
  const titulares = NOTICIAS
    .filter(n => tieneFechaReal(n) && (generoActual === 'todos' || (n.genero || 'todos') === generoActual))
    .sort((a, b) => (b.viral || 0) - (a.viral || 0) || new Date(b.fecha) - new Date(a.fecha))
    .slice(0, 6)
    .map(n => `<span data-id="${n.id}" role="button" tabindex="0" aria-label="Leer noticia: ${n.titulo}">${n.titulo}</span>`)
    .join('');
  document.getElementById('ticker-track').innerHTML = titulares + titulares;
}

/* ---------- Secciones temáticas ---------- */
function construirSecciones() {
  const contenedor = document.getElementById('secciones');
  contenedor.innerHTML = '';
  SECCIONES.forEach((sec, idx) => {
    const noticias = noticiasDeHoy(idx);
    const bloque = document.createElement('section');
    bloque.className = 'seccion bloque';
    bloque.id = sec.id;
    bloque.style.setProperty('--secc-color', sec.color);
    const contenido = noticias.length
      ? `<div class="rejilla">${noticias.map((n, i) => tarjetaHTML(n, '', i)).join('')}</div>`
      : '<p class="seccion__vacia">No hay noticias nuevas de este género aquí. Prueba otra pestaña o consulta el archivo.</p>';
    bloque.innerHTML = `
      <div class="wrap">
        <div class="seccion__cabecera">
          <div class="seccion__nombre"><span class="punto"></span>${sec.nombre}
            <span class="seccion__num">${noticias.length} noticias</span>
          </div>
          <a class="seccion__ver" href="#archivo" data-filtrar="${sec.id}">Ver todas las de ${sec.nombre.toLowerCase()} →</a>
        </div>
        ${contenido}
      </div>`;
    contenedor.appendChild(bloque);
    if (idx === 3) contenedor.insertAdjacentHTML('beforeend', AD_HTML);
  });
}

/* ---------- Archivo ---------- */
function construirArchivo() {
  const buscar = document.getElementById('archivo-buscar').value.trim().toLowerCase();
  const seccion = document.getElementById('archivo-seccion').value;
  const lista = document.getElementById('archivo-lista');

  let noticias = [...NOTICIAS].sort((a, b) => {
    const dif = FECHAS_PUBLICACION[b.id] - FECHAS_PUBLICACION[a.id];
    return dif !== 0 ? dif : a.slot - b.slot;
  });
  if (generoActual !== 'todos') noticias = noticias.filter(n => (n.genero || 'todos') === generoActual);
  if (seccion !== 'todas') noticias = noticias.filter(n => n.sec === seccion);
  if (buscar) noticias = noticias.filter(n =>
    (n.titulo + ' ' + n.entradilla + ' ' + (n.cuerpo || []).join(' ')).toLowerCase().includes(buscar));

  document.getElementById('archivo-contador').textContent =
    `${noticias.length} noticia${noticias.length === 1 ? '' : 's'}`;
  document.getElementById('archivo-vacio').hidden = noticias.length > 0;

  lista.innerHTML = noticias.map(n => {
    const sec = seccionPorId(n.sec);
    const f = FECHAS_PUBLICACION[n.id];
    return `<article class="archivo__item" data-id="${n.id}" style="--secc-color:${sec.color}"
               tabindex="0" role="button" aria-label="Leer noticia: ${n.titulo}">
      <img class="archivo__thumb" src="${n.image}" alt="" loading="lazy"
           onerror="imgFallback(this,'${sec.color}')">
      <div class="archivo__info">
        <div class="archivo__item-titulo">${n.titulo}</div>
        <div class="archivo__item-sub">${sec.nombre} · ${n.autor} · ${minutosLectura(n)} min de lectura</div>
      </div>
      <div class="archivo__fecha">
        <strong>${sec.nombre}</strong>
        ${fechaCorta.format(f)}
        ${IDS_HOY.has(n.id) ? '<span class="archivo__hoy">HOY</span>' : ''}
      </div>
    </article>`;
  }).join('');
}

/* ---------- Ataque: personaje + grito al abrir una noticia ---------- */
const PERSONAJES_ATAQUE = [
  'guerrero', 'espadachina', 'ninja', 'maga', 'mecha', 'detective', 'idol', 'dragon',
];

const Ataque = {
  activo: false,

  mostrar(callback) {
    if (this.activo) return;
    this.activo = true;

    const personaje = PERSONAJES_ATAQUE[Math.floor(Math.random() * PERSONAJES_ATAQUE.length)];
    const grito = Sonido.frase('whoosh');
    Sonido.decir(grito, 'ja-JP', 1);

    const reduce = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      setTimeout(() => { this.activo = false; if (callback) callback(); }, 420);
      return;
    }

    const capa = document.createElement('div');
    capa.className = 'ataque';
    capa.setAttribute('aria-hidden', 'true');
    capa.innerHTML = `
      <div class="ataque__rayo"></div>
      <div class="ataque__personaje">
        <img src="fondos/personajes/${personaje}.svg" alt="">
      </div>
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

/* ---------- Modal ---------- */
const modal = document.getElementById('modal');

function abrirNoticia(id) {
  const n = NOTICIAS.find(x => x.id === id);
  if (!n) return;
  // Página estática real: indexable y con URL limpia.
  // Se fuerza el scroll arriba para que la nueva página no "resbale".
  if (n.url) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    document.documentElement.scrollTop = 0;
    window.location.href = n.url;
    return;
  }
  const sec = seccionPorId(n.sec);
  const f = FECHAS_PUBLICACION[n.id];
  const relacionadas = NOTICIAS
    .filter(x => x.sec === n.sec && x.id !== n.id &&
      (x.genero || 'todos') === (n.genero || 'todos'))
    .slice(0, 2);

  document.getElementById('modal-contenido').innerHTML = `
    <img class="modal__img" src="${n.image}" alt="${n.titulo}" onerror="imgFallback(this,'${sec.color}')">
    <div class="modal__contenido-pad" style="--secc-color:${sec.color}">
      <span class="modal__tag">${sec.nombre}</span>
      <h1 class="modal__titulo" id="modal-titulo">${n.titulo}</h1>
      <div class="modal__meta">
        <span>Por <strong>${n.autor}</strong></span>
        <span>${fechaLarga.format(f)}</span>
        <span>${minutosLectura(n)} min de lectura</span>
      </div>
      <p class="modal__entradilla">${n.entradilla}</p>
      <div class="modal__cuerpo">${(n.cuerpo || []).map(p => `<p>${p}</p>`).join('')}</div>
      ${n.link ? `<a class="modal__fuente" href="${n.link}" target="_blank" rel="noopener noreferrer">Leer la noticia original en ${n.medio || 'la fuente'} ↗</a>` : ''}
      <div class="relacionadas">
        <h3>También en ${sec.nombre.toLowerCase()}</h3>
        ${relacionadas.map(r => `<a data-id="${r.id}">${r.titulo}</a>`).join('')}
      </div>
    </div>`;

  modal.hidden = false;
  document.body.classList.add('modal-abierto');
  modal.querySelector('.modal__panel').scrollTop = 0;
  document.getElementById('modal-close').focus();
}

function cerrarNoticia() {
  modal.hidden = true;
  document.body.classList.remove('modal-abierto');
}

/* ---------- Eventos ---------- */
document.addEventListener('click', (e) => {
  const cerrar = e.target.closest('[data-cerrar]');
  if (cerrar) { Sonido.reproducir('close', 0.55); cerrarNoticia(); return; }

  const vista = e.target.closest('[data-vista="glosario"]');
  if (vista) {
    Sonido.reproducir('tab', 0.6);
    Sonido.vibrar(18);
    document.querySelectorAll('#tabs-generos button').forEach(b =>
      b.classList.toggle('activa', b === vista));
    document.getElementById('glosario').scrollIntoView({ behavior: 'smooth' });
    return;
  }

  const pestaña = e.target.closest('[data-genero]');
  if (pestaña) {
    if (pestaña.dataset.genero === generoActual) return;
    Sonido.reproducir('tab', 0.6);
    Sonido.vibrar(18);
    generoActual = pestaña.dataset.genero;
    document.querySelectorAll('#tabs-generos button').forEach(b =>
      b.classList.toggle('activa', b === pestaña));
    actualizarIdsHoy();
    construirHero();
    construirTicker();
    construirSecciones();
    construirArchivo();
    return;
  }

  const filtrar = e.target.closest('[data-filtrar]');
  if (filtrar) {
    Sonido.reproducir('tab', 0.5);
    document.getElementById('archivo-seccion').value = filtrar.dataset.filtrar;
    construirArchivo();
    return;
  }

  const noticia = e.target.closest('[data-id]');
  if (noticia) {
    if (Ataque.activo) return;
    Sonido.vibrar(30);
    Ataque.mostrar(() => abrirNoticia(noticia.dataset.id));
    return;
  }

  if (e.target.closest('button, a, input, select')) Sonido.reproducir('click', 0.38);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !modal.hidden) { Sonido.reproducir('close', 0.55); cerrarNoticia(); }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[data-id][role="button"]')) {
    e.preventDefault();
    if (Ataque.activo) return;
    Sonido.vibrar(30);
    Ataque.mostrar(() => abrirNoticia(e.target.dataset.id));
  }
});

/* Sonido sutil al pasar el ratón por elementos interactivos */
document.addEventListener('mouseover', (e) => {
  if (e.target.closest('.tarjeta, .acceso, .archivo__item, .tabs-generos button, .audio-btn')) {
    Sonido.hover();
  }
});

document.getElementById('archivo-buscar').addEventListener('input', construirArchivo);
document.getElementById('archivo-seccion').addEventListener('change', construirArchivo);

document.getElementById('glosario-buscar').addEventListener('input', construirGlosario);
document.getElementById('glosario-categorias').addEventListener('click', (e) => {
  const boton = e.target.closest('[data-cat]');
  if (!boton) return;
  Sonido.reproducir('tab', 0.5);
  categoriaGlosario = boton.dataset.cat;
  document.querySelectorAll('#glosario-categorias .glosario__cat').forEach(b =>
    b.classList.toggle('activa', b === boton));
  construirGlosario();
});

document.getElementById('buscador-top').addEventListener('input', (e) => {
  document.getElementById('archivo-buscar').value = e.target.value;
  construirArchivo();
});
document.getElementById('buscador-top').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') document.getElementById('archivo').scrollIntoView({ behavior: 'smooth' });
});

/* ---------- Menú de 3 barras ---------- */
const menuBtn = document.getElementById('menu-btn');
const menuDesplegable = document.getElementById('menu-desplegable');

function alternarMenu(forzar) {
  const abierto = typeof forzar === 'boolean' ? forzar : menuDesplegable.hidden;
  menuDesplegable.hidden = !abierto;
  menuBtn.setAttribute('aria-expanded', String(abierto));
  menuBtn.setAttribute('aria-label', abierto ? 'Cerrar menú de secciones' : 'Abrir menú de secciones');
  menuBtn.innerHTML = abierto ? '&#10005;' : '&#9776;';
}

menuBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  Sonido.reproducir('click', 0.45);
  alternarMenu();
});
menuDesplegable.addEventListener('click', (e) => {
  if (e.target.closest('a')) alternarMenu(false);
});
document.addEventListener('click', (e) => {
  if (!e.target.closest('.menu-wrap')) alternarMenu(false);
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !menuDesplegable.hidden) { alternarMenu(false); menuBtn.focus(); }
});

/* ---------- Barra de progreso ---------- */
const barraProgreso = document.getElementById('progreso');
let desplazamientoPendiente = false;
function actualizarProgreso() {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  const valor = max > 0 ? (window.scrollY / max) * 100 : 0;
  barraProgreso.style.width = valor + '%';
  desplazamientoPendiente = false;
}
window.addEventListener('scroll', () => {
  if (!desplazamientoPendiente) {
    desplazamientoPendiente = true;
    requestAnimationFrame(actualizarProgreso);
  }
}, { passive: true });

/* ---------- Pétalos de sakura ---------- */
function crearPetalos() {
  const contenedor = document.getElementById('petalos');
  if (!contenedor) return;
  const simbolos = ['🌸', '✦', '✧', '🌙'];
  let html = '';
  for (let i = 0; i < 18; i++) {
    const izq = Math.random() * 100;
    const tam = 10 + Math.random() * 14;
    const dur = 11 + Math.random() * 13;
    const ret = -Math.random() * 20;
    const der = (Math.random() * 240 - 120).toFixed(0);
    const opa = (0.35 + Math.random() * 0.45).toFixed(2);
    html += `<span class="petalo" style="left:${izq.toFixed(1)}%;--tam:${tam}px;--dur:${dur}s;--ret:${ret}s;--der:${der}px;--opa:${opa}">${simbolos[i % simbolos.length]}</span>`;
  }
  contenedor.innerHTML = html;
}

/* ---------- Inicio ---------- */
document.getElementById('fecha-topbar').textContent = fechaLarga.format(HOY);
document.getElementById('anio').textContent = HOY.getFullYear();
if (typeof ACTUALIZADO !== 'undefined' && ACTUALIZADO) {
  document.querySelector('.topbar__edicion').textContent =
    'Actualizado el ' + new Date(ACTUALIZADO).toLocaleString('es-ES',
      { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

/* Canales de la comunidad (se rellenan en actualizar_noticias.py) */
try {
  const canales = [
    ['telegram', 'Telegram'], ['discord', 'Discord'], ['whatsapp', 'WhatsApp'],
  ].filter(([clave]) => CANALES && CANALES[clave]);
  document.getElementById('footer-canales').innerHTML = canales
    .map(([clave, nombre]) => `<a href="${CANALES[clave]}" target="_blank" rel="noopener noreferrer">${nombre} ↗</a>`)
    .join('');
} catch (_) { /* CANALES vacío: no se muestra nada */ }

if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
window.addEventListener('pageshow', (e) => {
  if (e.persisted) {
    document.documentElement.style.scrollBehavior = 'auto';
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  }
});

crearPetalos();
construirNavegacion();
construirHero();
construirTendencias();
construirCategoriasGlosario();
construirGlosario();
construirTicker();
construirSecciones();
construirArchivo();
actualizarProgreso();

/* Revelado suave al entrar en pantalla */
if ('IntersectionObserver' in window) {
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('revelado');
        observador.unobserve(en.target);
      }
    });
  }, { threshold: 0.06 });
  document.querySelectorAll('.panel-tendencia, .glosario__termino, .bloque--archivo')
    .forEach(el => observador.observe(el));
}

/* Si el usuario dejó la música activada, se arranca tras el primer gesto */
if (typeof Sonido !== 'undefined' && Sonido.musicaActiva) {
  window.addEventListener('pointerdown', function arrancar() {
    Sonido.arrancarMusica();
    window.removeEventListener('pointerdown', arrancar);
  }, { once: true });
}

/* ---------- Contador de visitas ---------- */
(async function contadorDeVisitas() {
  const hueco = document.getElementById('contador-visitas');
  if (!hueco) return;
  try {
    const respuesta = await fetch(
      'https://countapi.mileshilliard.com/api/v1/hit/animechronicle-visitas-2026',
      { cache: 'no-store' });
    if (!respuesta.ok) throw new Error('Contador no disponible');
    const datos = await respuesta.json();
    hueco.textContent = new Intl.NumberFormat('es-ES').format(datos.value);
  } catch (error) {
    hueco.textContent = '—';
    hueco.title = 'El contador no está disponible temporalmente';
  }
})();
