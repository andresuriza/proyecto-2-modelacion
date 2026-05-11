const socket = io();

let tiempoMax = 50;

socket.on('tick', (data) => {
    actualizarTiempo(data.tiempo);
});

function actualizarTiempo(t) {
    const fill = document.getElementById('tiempo-fill');
    const valor = document.getElementById('tiempo-valor');
    if (!fill || !valor) return;
    const pct = Math.min((t / tiempoMax) * 100, 100);
    fill.style.width = pct + '%';
    valor.textContent = `t = ${t}`;
}

// ── Formulario Home ───────────────────────────────────────────────────────────
document.getElementById('form-proceso')?.addEventListener('submit', function (e) {
    e.preventDefault();

    const nombre   = document.getElementById('nombre-proceso').value.trim();
    const cantidad = parseInt(document.getElementById('cantidad-producto').value);
    const nTareas  = parseInt(document.getElementById('cantidad-tareas').value);

    if (!nombre || !cantidad || !nTareas) {
        mostrarToast('Completa todos los campos');
        return;
    }

    // Guarda datos en sessionStorage y va a página de tareas
    sessionStorage.setItem('proceso_pendiente', JSON.stringify({ nombre, cantidad, nTareas }));
    window.location.href = '/tareas';
});

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
