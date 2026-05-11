const socket = io();

// ── Al cargar Home, mostrar procesos ya creados ───────────────────────────────
cargarProcesosExistentes();

async function cargarProcesosExistentes() {
    const res   = await fetch('/api/procesos-creados');
    const lista = await res.json();
    if (lista.length > 0) renderLinea(lista);
}

// ── Formulario nuevo proceso ──────────────────────────────────────────────────
document.getElementById('form-proceso')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const nombre   = document.getElementById('nombre-proceso').value.trim();
    const cantidad = parseInt(document.getElementById('cantidad-producto').value);
    const nTareas  = parseInt(document.getElementById('cantidad-tareas').value);

    if (!nombre || !cantidad || !nTareas) {
        mostrarToast('Completa todos los campos');
        return;
    }

    sessionStorage.setItem('proceso_pendiente', JSON.stringify({ nombre, cantidad, nTareas }));
    window.location.href = '/tareas';
});

// ── Render lista de procesos ──────────────────────────────────────────────────
function renderLinea(lista) {
    const card  = document.getElementById('card-linea');
    const linea = document.getElementById('linea-lista');
    card.style.display = 'block';
    linea.innerHTML = '';

    lista.forEach(p => {
        const badges = [];
        if (p.inicial) badges.push('<span class="badge">Inicial</span>');
        if (p.final)   badges.push('<span class="badge">Final</span>');

        const item = document.createElement('div');
        item.className = 'proceso-item';
        item.innerHTML = `
            <div class="proceso-dot"></div>
            <span class="proceso-nombre">${p.nombre} ${badges.join('')}</span>
            <span class="proceso-meta">${p.productos} productos · ${p.n_tareas} tareas</span>
        `;
        linea.appendChild(item);
    });
}

// ── Toast ─────────────────────────────────────────────────────────────────────
function mostrarToast(msg) {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
}
