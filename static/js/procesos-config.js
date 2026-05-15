// socket viene de base.html como window.socket

let procesoSeleccionado = null;

async function cargarProcesos() {
    const res  = await fetch('/api/procesos-creados');
    const data = await res.json();

    const empty = document.getElementById('proc-empty');
    const grid  = document.getElementById('proc-grid');

    if (!data.procesos || data.procesos.length === 0) {
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    grid.innerHTML = '';

    data.procesos.forEach((p, i) => {
        const card = document.createElement('div');
        card.className = 'proc-card';
        card.dataset.index = i;

        let badges = '';
        if (p.inicial) badges += '<span class="badge-sel">Inicial</span>';
        if (p.final)   badges += '<span class="badge-sel final">Final</span>';

        card.innerHTML = `
            <div class="letra-metal proc-letra">${p.nombre[0].toUpperCase()}</div>
            <div class="proc-card-nombre">${p.nombre}${badges ? ' ' + badges : ''}</div>
            <div class="proc-card-actions">
                <button class="btn-proc-pos" data-nombre="${p.nombre}" data-accion="head">Inicio</button>
                <button class="btn-proc-pos" data-nombre="${p.nombre}" data-accion="tail">Fin</button>
            </div>
        `;

        card.querySelectorAll('.btn-proc-pos').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const res  = await fetch('/api/mover-proceso', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ nombre: btn.dataset.nombre, accion: btn.dataset.accion })
                });
                const data = await res.json();
                if (data.ok) {
                    procesoSeleccionado = null;
                    document.getElementById('proc-panel').style.display = 'none';
                    cargarProcesos();
                } else {
                    mostrarToast(data.mensaje);
                }
            });
        });

        card.addEventListener('click', () => seleccionarProceso(p, i));
        grid.appendChild(card);
    });
}

function seleccionarProceso(proceso, index) {
    const panel   = document.getElementById('proc-panel');
    const allCards = document.querySelectorAll('.proc-card');

    // Toggle si ya estaba seleccionado
    if (procesoSeleccionado === index) {
        procesoSeleccionado = null;
        allCards.forEach(c => c.classList.remove('activo'));
        panel.style.display = 'none';
        return;
    }

    procesoSeleccionado = index;
    allCards.forEach((c, i) => c.classList.toggle('activo', i === index));

    document.getElementById('proc-panel-titulo').textContent = `Tareas de ${proceso.nombre}`;

    const tareasEl = document.getElementById('proc-panel-tareas');
    tareasEl.innerHTML = '';

    proceso.tareas.forEach(t => {
        const row = document.createElement('div');
        row.className = 'proc-task-row';
        const inputId = `t-inp-${proceso.nombre}-${t.n}`;
        row.innerHTML = `
            <span class="proc-task-nombre">Tarea ${t.n}</span>
            <input type="number" class="reiniciar-input" id="${inputId}" value="${t.tiempo_proceso}" min="1">
            <button class="btn-crear proc-task-save" data-proceso="${proceso.nombre}" data-tarea="${t.n}" data-input="${inputId}">Guardar</button>
        `;
        tareasEl.appendChild(row);
    });

    tareasEl.querySelectorAll('.proc-task-save').forEach(btn => {
        btn.addEventListener('click', async () => {
            const tiempo = parseInt(document.getElementById(btn.dataset.input).value);
            if (!tiempo || tiempo < 1) { mostrarToast('Tiempo inválido'); return; }

            const res  = await fetch('/api/actualizar-tarea', {
                method:  'POST',
                headers: { 'Content-Type': 'application/json' },
                body:    JSON.stringify({ proceso: btn.dataset.proceso, tarea: parseInt(btn.dataset.tarea), tiempo })
            });
            const data = await res.json();
            mostrarToast(data.ok ? `Tarea ${btn.dataset.tarea} actualizada` : data.mensaje);
        });
    });

    panel.style.display = 'block';
}

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

cargarProcesos();
