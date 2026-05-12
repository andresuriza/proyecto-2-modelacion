// socket viene de base.html como window.socket

const proceso = JSON.parse(sessionStorage.getItem('proceso_pendiente') || 'null');

// Si llegaron sin datos, vuelven a Home
if (!proceso) window.location.href = '/';

const ciclos = Array(proceso.nTareas).fill(1);

function renderTareas() {
    const lista = document.getElementById('tareas-lista');
    lista.innerHTML = '';

    for (let i = 0; i < proceso.nTareas; i++) {
        const row = document.createElement('div');
        row.className = 'tarea-item';
        row.innerHTML = `
            <span class="tarea-nombre">Tarea ${i + 1}</span>
            <button class="btn-pm" data-i="${i}" data-op="mas">+</button>
            <span class="tarea-ciclos" id="ciclo-${i}">${ciclos[i]}</span>
            <button class="btn-pm minus" data-i="${i}" data-op="menos">−</button>
        `;
        lista.appendChild(row);
    }

    lista.querySelectorAll('.btn-pm').forEach(btn => {
        btn.addEventListener('click', () => {
            const i  = parseInt(btn.dataset.i);
            const op = btn.dataset.op;
            if (op === 'mas') ciclos[i]++;
            if (op === 'menos' && ciclos[i] > 1) ciclos[i]--;
            document.getElementById(`ciclo-${i}`).textContent = ciclos[i];
        });
    });
}

renderTareas();

// ── Guardar proceso ───────────────────────────────────────────────────────────
document.getElementById('btn-guardar')?.addEventListener('click', async () => {
    const tareas = ciclos.map(t => ({ tiempo_proceso: t }));

    const res = await fetch('/api/crear-proceso', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            nombre: proceso.nombre,
            cantidad_producto: proceso.cantidad,
            tareas
        })
    });

    const data = await res.json();
    if (data.ok) {
        sessionStorage.removeItem('proceso_pendiente');
        mostrarToast(data.mensaje);
        setTimeout(() => window.location.href = '/', 1200);
    }
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
