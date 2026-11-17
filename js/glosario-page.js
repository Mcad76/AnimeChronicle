/* Glosario otaku — página independiente */
let categoriaGlosario = 'todas';

function construirCategorias() {
  document.getElementById('glosario-categorias').innerHTML =
    [{ id: 'todas', nombre: 'Todo', icono: '✦' }].concat(CATEGORIAS_GLOSARIO)
      .map(c => `<button type="button" data-cat="${c.id}"
        class="glosario__cat ${c.id === categoriaGlosario ? 'activa' : ''}">
        ${c.icono} ${c.nombre}</button>`).join('');
}

function construirGlosario() {
  const buscar = document.getElementById('glosario-buscar').value.trim().toLowerCase();
  const vocab = GLOSARIO.filter(x =>
    (categoriaGlosario === 'todas' || x.c === categoriaGlosario) &&
    (!buscar || (x.t + ' ' + x.d).toLowerCase().includes(buscar)));
  document.getElementById('glosario-contador').textContent = `${vocab.length} términos`;
  document.getElementById('glosario-vacio').hidden = vocab.length > 0;
  document.getElementById('glosario-lista').innerHTML = vocab.map((x, i) => {
    const cat = CATEGORIAS_GLOSARIO.find(c => c.id === x.c) || {};
    return `<article class="glosario__termino" style="--i:${i}">
      <span class="glosario__cat-tag">${cat.icono || '✦'} ${cat.nombre || ''}</span>
      <h3>${x.t}</h3>
      <p>${x.d}</p>
    </article>`;
  }).join('');
}

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
document.addEventListener('click', (e) => {
  if (e.target.closest('button, a, input') && !e.target.closest('[data-cat]')) {
    Sonido.reproducir('click', 0.4);
  }
});

document.getElementById('fecha-topbar').textContent =
  new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(new Date());
document.getElementById('anio').textContent = new Date().getFullYear();
construirCategorias();
construirGlosario();

const barra = document.getElementById('progreso');
window.addEventListener('scroll', () => {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  barra.style.width = (max > 0 ? (window.scrollY / max) * 100 : 0) + '%';
}, { passive: true });
