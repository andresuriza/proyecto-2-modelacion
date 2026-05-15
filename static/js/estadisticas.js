async function cargarEstadisticas() {
    const res  = await fetch('/api/estadisticas');
    const data = await res.json();

    if (!data.disponible) return;

    document.getElementById('est-waiting').style.display = 'none';
    document.getElementById('est-content').style.display = 'block';

    // Métricas globales
    document.getElementById('m-primer').textContent   = data.t_primer_producto;
    document.getElementById('m-ultimo').textContent   = data.t_ultimo_producto;
    document.getElementById('m-promedio').textContent = data.t_promedio;
    document.getElementById('m-total').textContent    = data.tiempo_total;
    document.getElementById('m-espera').textContent   = data.espera_promedio;

    // Cuello de botella
    const cb = data.cuello_botella;
    const mx = data.tarea_max_espera;
    document.getElementById('est-letra-bn').textContent = cb.proceso[0].toUpperCase();
    document.getElementById('bn-nombre').textContent    = `${cb.proceso} — T${cb.tarea}`;
    document.getElementById('bn-espera').textContent    = cb.espera_promedio;
    document.getElementById('max-nombre').textContent   = `${mx.proceso} — T${mx.tarea}`;
    document.getElementById('max-espera').textContent   = mx.espera_max;

    // Tabla detallada
    const tbody    = document.getElementById('est-tbody');
    const cuelloKey = `${cb.proceso}-${cb.tarea}`;
    tbody.innerHTML = '';
    data.task_stats.forEach(ts => {
        const tr = document.createElement('tr');
        if (`${ts.proceso}-${ts.tarea}` === cuelloKey) tr.classList.add('cuello');
        tr.innerHTML = `
            <td>${ts.proceso}</td>
            <td>T${ts.tarea}</td>
            <td>${ts.tiempo_proceso}</td>
            <td>${ts.espera_promedio}</td>
            <td>${ts.espera_max}</td>
            <td>${ts.completados}</td>
        `;
        tbody.appendChild(tr);
    });
}

cargarEstadisticas();
socket.on('simulacion_terminada', cargarEstadisticas);
