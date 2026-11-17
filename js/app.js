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
function imgFallback(el, color) {
  el.onerror = null;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="640">
    <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#080616"/><stop offset="1" stop-color="${color}"/>
    </linearGradient></defs>
    <rect width="100%" height="100%" fill="url(#g)"/>
    <text x="50%" y="46%" fill="#fff" font-family="Arial,sans-serif" font-size="58"
          font-weight="bold" text-anchor="middle">ANIMECHRONICLE</text>
    <text x="50%" y="60%" fill="#fff" opacity=".8" font-family="Arial,sans-serif"
          font-size="26" text-anchor="middle">IMAGEN ILUSTRATIVA ✦</text>
  </svg>`;
  el.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
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
  return `<article class="tarjeta ${variante}" data-id="${noticia.id}"
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

/* ---------- Navegación, pestañas y ticker ---------- */
function construirNavegacion() {
  const tabs = document.getElementById('tabs-generos');
  if (tabs) {
    tabs.innerHTML = GENEROS.map(g =>
      `<button type="button" data-genero="${g.id}" class="${g.id === generoActual ? 'activa' : ''}"
        aria-pressed="${g.id === generoActual}">${g.nombre}</button>`).join('');
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

/* ---------- Modal ---------- */
const modal = document.getElementById('modal');

function abrirNoticia(id) {
  const n = NOTICIAS.find(x => x.id === id);
  if (!n) return;
  // Página estática real: indexable y con URL limpia
  if (n.url) { window.location.href = n.url; return; }
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
    Sonido.reproducir('select', 0.5);
    Sonido.vibrar(25);
    abrirNoticia(noticia.dataset.id);
    return;
  }

  if (e.target.closest('button, a, input, select')) Sonido.reproducir('click', 0.38);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && !modal.hidden) { Sonido.reproducir('close', 0.55); cerrarNoticia(); }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[data-id][role="button"]')) {
    e.preventDefault();
    Sonido.reproducir('select', 0.5);
    abrirNoticia(e.target.dataset.id);
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

crearPetalos();
construirNavegacion();
construirHero();
construirTicker();
construirSecciones();
construirArchivo();
actualizarProgreso();

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
