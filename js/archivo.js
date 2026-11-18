/* Archivo de noticias — página independiente */
const fechaCorta = new Intl.DateTimeFormat('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });
const fechaLarga = new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
const HOY = new Date();
const FECHAS = {};
NOTICIAS.forEach(n => { FECHAS[n.id] = new Date(n.fecha || Date.now()); });

function seccionPorId(id) { return SECCIONES.find(s => s.id === id); }
function minutosLectura(n) {
  const palabras = (n.entradilla + ' ' + (n.cuerpo || []).join(' ')).split(/\s+/).length;
  return Math.max(1, Math.round(palabras / 200));
}

const POR_PAGINA = 30;
let listaActual = [];
let paginaActual = 0;

function itemHTML(n) {
  const sec = seccionPorId(n.sec);
  return `<article class="archivo__item" data-id="${n.id}" data-url="${n.url}"
             style="--secc-color:${sec.color}" tabindex="0" role="button"
             aria-label="Leer noticia: ${n.titulo}">
    <img class="archivo__thumb" src="${n.image}" alt="" loading="lazy"
         onerror="imgFallback(this,'${sec.color}')">
    <div class="archivo__info">
      <div class="archivo__item-titulo">${n.titulo}</div>
      <div class="archivo__item-sub">${sec.nombre} · ${n.autor} · ${minutosLectura(n)} min de lectura</div>
    </div>
    <div class="archivo__fecha"><strong>${sec.nombre}</strong>${fechaCorta.format(FECHAS[n.id])}</div>
  </article>`;
}

function renderizarPagina(anadir = false) {
  const lista = document.getElementById('archivo-lista');
  const trozo = listaActual.slice(paginaActual * POR_PAGINA, (paginaActual + 1) * POR_PAGINA);
  const html = trozo.map(itemHTML).join('');
  if (anadir) lista.insertAdjacentHTML('beforeend', html);
  else lista.innerHTML = html;

  const restantes = listaActual.length - (paginaActual + 1) * POR_PAGINA;
  document.getElementById('archivo-mas').innerHTML = restantes > 0
    ? `<button type="button" id="cargar-mas">Cargar ${Math.min(restantes, POR_PAGINA)} noticias más (${restantes} restantes) ↓</button>`
    : '';
}

function construirArchivo() {
  const buscar = document.getElementById('archivo-buscar').value.trim().toLowerCase();
  const seccion = document.getElementById('archivo-seccion').value;
  let noticias = [...NOTICIAS].sort((a, b) => FECHAS[b.id] - FECHAS[a.id]);
  if (seccion !== 'todas') noticias = noticias.filter(n => n.sec === seccion);
  if (buscar) noticias = noticias.filter(n =>
    (n.titulo + ' ' + n.entradilla + ' ' + (n.cuerpo || []).join(' ')).toLowerCase().includes(buscar));

  listaActual = noticias;
  paginaActual = 0;
  document.getElementById('archivo-contador').textContent =
    `${noticias.length} noticia${noticias.length === 1 ? '' : 's'}`;
  document.getElementById('archivo-vacio').hidden = noticias.length > 0;
  renderizarPagina();
}

function imgFallback(el, color) {
  el.onerror = null;
  const ps = PERSONAJES;
  const p = ps[Math.floor(Math.random() * ps.length)];
  el.src = 'fondos/personajes-famosos/' + p + '.svg';
  el.style.objectFit = 'contain';
  el.style.background = 'radial-gradient(circle,' + color + '55,#080616)';
}

document.getElementById('archivo-seccion').innerHTML = '<option value="todas">Todas las secciones</option>' +
  SECCIONES.map(s => `<option value="${s.id}">${s.nombre}</option>`).join('');
const params = new URLSearchParams(location.search);
if (params.get('q')) document.getElementById('archivo-buscar').value = params.get('q');
if (params.get('sec')) document.getElementById('archivo-seccion').value = params.get('sec');
document.getElementById('archivo-buscar').addEventListener('input', construirArchivo);
document.getElementById('archivo-seccion').addEventListener('change', construirArchivo);

document.addEventListener('click', (e) => {
  if (e.target.closest('#cargar-mas')) {
    paginaActual++;
    renderizarPagina(true);
    if (typeof Sonido !== 'undefined') Sonido.reproducir('click', 0.4);
    return;
  }
  const item = e.target.closest('[data-url]');
  if (item) {
    const n = NOTICIAS.find(x => x.url === item.dataset.url);
    const grito = n ? Sonido.frasePara(n.titulo + ' ' + n.entradilla) : undefined;
    abrirConAtaque(item.dataset.url, grito);
    return;
  }
  if (e.target.closest('button, a, input, select') && typeof Sonido !== 'undefined') {
    Sonido.reproducir('click', 0.4);
  }
});
document.addEventListener('keydown', (e) => {
  const item = e.target.closest('[data-url][role="button"]');
  if (item && (e.key === 'Enter' || e.key === ' ')) {
    e.preventDefault();
    const n = NOTICIAS.find(x => x.url === item.dataset.url);
    const grito = n ? Sonido.frasePara(n.titulo + ' ' + n.entradilla) : undefined;
    abrirConAtaque(item.dataset.url, grito);
  }
});

document.getElementById('fecha-topbar').textContent = fechaLarga.format(HOY);
document.getElementById('anio').textContent = HOY.getFullYear();
construirArchivo();

const barra = document.getElementById('progreso');
window.addEventListener('scroll', () => {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  barra.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
}, { passive: true });
