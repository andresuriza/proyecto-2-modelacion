// socket viene de base.html como window.socket
const CIRCUM = 69.12; // 2 * π * 11

let estado = { procesos: [], tiempo: 0 };
let procesoActivo = 0;

// ── SocketIO ──────────────────────────────────────────────────────────────────
socket.on('estado', (data) => { actualizarEstado(data); });
socket.on('tick',   (data) => { actualizarEstado(data); });
socket.on('simulacion_terminada', (data) => {
    actualizarEstado(data);
    mostrarToast('Simulación completada');
});

// ── Actualizar estado completo ────────────────────────────────────────────────
function actualizarEstado(data) {
    estado = data;
    actualizarTiempo(data.tiempo);
    renderSelector(data.procesos);
    renderTareas(data.procesos[procesoActivo]);
    actualizarPausa(data.paused, data.running);
}

// ── Barra de tiempo ───────────────────────────────────────────────────────────
function actualizarTiempo(t) {
    const fill  = document.getElementById('tiempo-fill');
    const valor = document.getElementById('tiempo-valor');
    const max   = calcularTiempoMax();
    const pct   = max > 0 ? Math.min((t / max) * 100, 100) : 0;
    fill.style.width   = pct + '%';
    valor.textContent  = `t = ${t}`;
}

function calcularTiempoMax() {
    // Tiempo estimado: suma de tiempos de todas las tareas de la cadena * N productos
    // (aproximación conservadora para la barra de progreso)
    let sumaTareas = 0;
    let total = 0;
    estado.procesos.forEach(p => p.tareas.forEach(t => {
        sumaTareas += t.tiempo_proceso;
        total = t.total || total;
    }));
    return sumaTareas > 0 ? sumaTareas * (total || 1) : 50;
}

// ── Selector de procesos (panel izquierdo) ────────────────────────────────────
function renderSelector(procesos) {
    const sel = document.getElementById('p3-selector');
    if (procesos.length === 0) return;

    // Solo reconstruye si cambia el número de procesos
    if (sel.children.length === procesos.length) return;

    sel.innerHTML = '';
    procesos.forEach((p, i) => {
        const btn = document.createElement('button');
        btn.className = 'p3-selector-btn' + (i === procesoActivo ? ' activo' : '');
        btn.textContent = p.nombre;
        btn.addEventListener('click', () => {
            procesoActivo = i;
            sel.querySelectorAll('.p3-selector-btn').forEach((b, j) =>
                b.classList.toggle('activo', j === i));
            renderTareas(estado.procesos[i]); // siempre lee del estado actual
        });
        sel.appendChild(btn);
    });
}

// ── Tarjetas de tareas (panel derecho, scrolleable) ───────────────────────────
function renderTareas(proceso) {
    const scroll = document.getElementById('p3-tareas-scroll');
    const empty  = document.getElementById('p3-empty');

    if (!proceso) {
        empty.style.display = 'block';
        return;
    }
    empty.style.display = 'none';

    proceso.tareas.forEach((t, i) => {
        let card = document.getElementById(`card-tarea-${proceso.nombre}-${i}`);

        if (!card) {
            card = crearCard(proceso.nombre, t, i);
            scroll.appendChild(card);
        }

        actualizarCard(card, t, proceso);
    });

    // Eliminar cards de procesos anteriores que ya no corresponden
    scroll.querySelectorAll('.tarea-card').forEach(c => {
        if (!c.id.startsWith(`card-tarea-${proceso.nombre}`)) c.remove();
    });
}

function crearCard(nombreProceso, tarea, i) {
    const card = document.createElement('div');
    card.className = 'tarea-card';
    card.id = `card-tarea-${nombreProceso}-${i}`;
    card.innerHTML = `
        <div class="tarea-progress">
            <svg class="progress-svg" viewBox="0 0 24 24">
                <circle class="progress-bg"   cx="12" cy="12" r="11"/>
                <circle class="progress-fill" cx="12" cy="12" r="11"/>
            </svg>
            <span class="tarea-duracion">Duración: ${tarea.tiempo_proceso}s</span>
        </div>
        <div class="tarea-info">
            <div class="tarea-card-nombre">Tarea ${tarea.n}</div>
            <div class="tarea-estado">
                <span class="estado-proc">En espera</span>
                <span class="estado-cola">En cola: 0</span>
            </div>
            <div class="tarea-producto" id="prod-label-${nombreProceso}-${i}"></div>
        </div>
    `;
    return card;
}

function actualizarCard(card, tarea, proceso) {
    const fill      = card.querySelector('.progress-fill');
    const estadoEl  = card.querySelector('.estado-proc');
    const colaEl    = card.querySelector('.estado-cola');
    const prodLabel = card.querySelector('.tarea-producto');

    const completados = tarea.completados || 0;
    const pct         = tarea.total > 0 ? completados / tarea.total : 0;
    fill.style.strokeDashoffset = CIRCUM * (1 - pct);

    if (tarea.procesando && tarea.producto_actual != null) {
        estadoEl.textContent = 'Procesando...';
        estadoEl.className   = 'estado-proc activo';
        prodLabel.textContent = `Producto #${tarea.producto_actual}`;
        prodLabel.className   = 'tarea-producto activo';
    } else {
        estadoEl.textContent  = 'En espera';
        estadoEl.className    = 'estado-proc';
        prodLabel.textContent = completados > 0 ? `Completados: ${completados}` : '';
        prodLabel.className   = 'tarea-producto';
    }

    colaEl.textContent = `En cola: ${tarea.en_cola}`;
}

// ── Botón iniciar ─────────────────────────────────────────────────────────────
document.getElementById('btn-iniciar')?.addEventListener('click', async () => {
    const res  = await fetch('/api/iniciar', { method: 'POST' });
    const data = await res.json();
    mostrarToast(data.ok ? 'Simulación iniciada' : data.mensaje);
});

function actualizarPausa(paused, running) {
    const btn = document.getElementById('btn-pausa');
    if (!btn) return;
    btn.disabled = !running;
    btn.classList.toggle('paused', paused);
    btn.querySelector('.pausa-icon').innerHTML = paused ? '&#9646;&#9646;' : '&#9654;';
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
