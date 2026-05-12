const socket = io();

// ── Al cargar Home, mostrar procesos ya creados ───────────────────────────────
cargarProcesosExistentes();

async function cargarProcesosExistentes() {
    const res  = await fetch('/api/procesos-creados');
    const data = await res.json();
    if (data.procesos && data.procesos.length > 0) {
        renderLinea(data.procesos, data.cantidad_global);
        // Ya hay procesos: el campo cantidad ya no aplica
        const grupoCantidad = document.getElementById('grupo-cantidad');
        grupoCantidad.style.display = 'none';
        document.getElementById('cantidad-producto').removeAttribute('required');
    }
}

// ── Formulario nuevo proceso ──────────────────────────────────────────────────
document.getElementById('form-proceso')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const nombre   = document.getElementById('nombre-proceso').value.trim();
    const nTareas  = parseInt(document.getElementById('cantidad-tareas').value);
    const grupoCantidad = document.getElementById('grupo-cantidad');
    const cantidadInput = document.getElementById('cantidad-producto');
    const cantidad = grupoCantidad.style.display === 'none'
        ? 0  // backend usará cantidad_global
        : parseInt(cantidadInput.value);

    if (!nombre || !nTareas || (grupoCantidad.style.display !== 'none' && !cantidad)) {
        mostrarToast('Completa todos los campos');
        return;
    }

    sessionStorage.setItem('proceso_pendiente', JSON.stringify({ nombre, cantidad, nTareas }));
    window.location.href = '/tareas';
});

// ── Render lista de procesos ──────────────────────────────────────────────────
function renderLinea(lista, cantidadGlobal) {
    const card  = document.getElementById('card-linea');
    const linea = document.getElementById('linea-lista');
    card.style.display = 'block';
    linea.innerHTML = '';

    if (cantidadGlobal) {
        const resumen = document.createElement('p');
        resumen.style.cssText = 'font-size:0.82rem;color:var(--text-muted);margin-bottom:0.75rem';
        resumen.textContent = `${cantidadGlobal} producto(s) recorren toda la línea`;
        linea.appendChild(resumen);
    }

    lista.forEach(p => {
        const badges = [];
        if (p.inicial) badges.push('<span class="badge">Inicial</span>');
        if (p.final)   badges.push('<span class="badge">Final</span>');

        const item = document.createElement('div');
        item.className = 'proceso-item';
        item.innerHTML = `
            <div class="proceso-dot"></div>
            <span class="proceso-nombre">${p.nombre} ${badges.join('')}</span>
            <span class="proceso-meta">${p.n_tareas} tarea(s)</span>
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
