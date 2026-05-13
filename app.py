from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import prod

app = Flask(__name__)
app.config['SECRET_KEY'] = 'linprod-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

simulation = {
    'process_list': prod.LinkedList(),
    'running': False,
    'paused': False,
    'current_t': 0,
    'done': False,
    'processes_config': [],
    'cantidad_global': 0
}

# ── Rutas ──────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tareas')
def tareas():
    return render_template('tareas.html')

@app.route('/simulacion')
def simulacion():
    return render_template('simulacion.html')

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

# ── API ────────────────────────────────────────────────────────────────────────

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas_api():
    if not simulation['done']:
        return jsonify({'disponible': False})

    task_stats = []
    last_task_records = []

    node = simulation['process_list'].GetHead()
    while node:
        p = node.GetData()
        t_node = p.tasks.GetHead()
        # Encontrar la última tarea de este proceso
        last_t_node = t_node
        while last_t_node.next:
            last_t_node = last_t_node.next

        t_node = p.tasks.GetHead()
        while t_node:
            t = t_node.GetData()
            records = t._records
            if records:
                waits = [r['wait'] for r in records]
                task_stats.append({
                    'proceso':         p.name,
                    'tarea':           t.n,
                    'tiempo_proceso':  t.processing_t,
                    'espera_promedio': round(sum(waits) / len(waits), 2),
                    'espera_max':      max(waits),
                    'completados':     len(records)
                })
            # Registros de la última tarea del último proceso = tiempos de salida de la línea
            if t_node == last_t_node and node.next is None:
                last_task_records = records
            t_node = t_node.next
        node = node.next

    if not last_task_records or not task_stats:
        return jsonify({'disponible': False})

    exit_times = [r['done_at'] for r in last_task_records]
    all_waits  = [r['wait'] for ts in task_stats for r in []]  # placeholder
    # Recalcular espera global desde task_stats
    total_wait = sum(ts['espera_promedio'] * ts['completados'] for ts in task_stats)
    total_comp = sum(ts['completados'] for ts in task_stats)
    espera_global = round(total_wait / total_comp, 2) if total_comp else 0

    cuello    = max(task_stats, key=lambda x: x['espera_promedio'])
    max_espera = max(task_stats, key=lambda x: x['espera_max'])

    return jsonify({
        'disponible':          True,
        't_primer_producto':   min(exit_times),
        't_ultimo_producto':   max(exit_times),
        't_promedio':          round(sum(exit_times) / len(exit_times), 2),
        'tiempo_total':        simulation['current_t'],
        'espera_promedio':     espera_global,
        'cuello_botella':      {'proceso': cuello['proceso'],    'tarea': cuello['tarea'],    'espera_promedio': cuello['espera_promedio']},
        'tarea_max_espera':    {'proceso': max_espera['proceso'],'tarea': max_espera['tarea'],'espera_max': max_espera['espera_max']},
        'task_stats':          task_stats
    })

@app.route('/api/crear-proceso', methods=['POST'])
def crear_proceso():
    data = request.get_json()
    nombre        = data.get('nombre')
    tareas_config = data.get('tareas', [])

    is_first = simulation['process_list'].GetHead() is None
    if is_first:
        cantidad = int(data.get('cantidad_producto', 1))
        simulation['cantidad_global'] = cantidad
    else:
        cantidad = simulation['cantidad_global']

    p = prod.Process(nombre, cantidad)
    p.is_first = is_first
    for t in tareas_config:
        p.CreateTask(int(t['tiempo_proceso']))
    p.QueueProducts(queue=is_first)

    simulation['process_list'].Insert(p)
    simulation['processes_config'].append(data)

    return jsonify({'ok': True, 'mensaje': f'Proceso "{nombre}" creado'})

@app.route('/api/iniciar', methods=['POST'])
def iniciar():
    if simulation['running']:
        return jsonify({'ok': False, 'mensaje': 'Ya hay una simulación corriendo'})
    if simulation['process_list'].GetHead() is None:
        return jsonify({'ok': False, 'mensaje': 'No hay procesos creados'})

    simulation['running'] = True
    simulation['done']    = False
    simulation['paused']  = False
    prod.done             = False
    prod.paused           = False
    prod.current_t        = 0

    threading.Thread(target=_run_simulation, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/api/reset-linea', methods=['POST'])
def reset_linea():
    if simulation['running'] and not simulation['paused']:
        return jsonify({'ok': False, 'mensaje': 'Pausá la simulación antes de borrar la línea'})

    # Imprimir procesos que se van a borrar
    nombres = []
    node = simulation['process_list'].GetHead()
    while node:
        nombres.append(node.GetData().name)
        node = node.next
    print(f"=== Línea borrada: {nombres if nombres else '(vacía)'} ===")

    prod.paused                    = False
    prod.done                      = True   # señal para que todos los threads salgan
    simulation['process_list']     = prod.LinkedList()
    simulation['processes_config'] = []
    simulation['cantidad_global']  = 0
    simulation['running']          = False
    simulation['paused']           = False
    simulation['done']             = False
    simulation['current_t']        = 0
    prod.current_t                 = 0
    # prod.done se resetea en iniciar/reiniciar, no acá
    socketio.emit('estado', _get_estado())
    return jsonify({'ok': True})

@app.route('/api/reiniciar', methods=['POST'])
def reiniciar():
    if simulation['running']:
        return jsonify({'ok': False, 'mensaje': 'Ya hay una simulación corriendo'})
    if simulation['process_list'].GetHead() is None:
        return jsonify({'ok': False, 'mensaje': 'No hay procesos creados'})

    data = request.get_json() or {}
    nueva_cantidad = data.get('cantidad')
    if nueva_cantidad:
        nueva_cantidad = int(nueva_cantidad)
        simulation['cantidad_global'] = nueva_cantidad
        node = simulation['process_list'].GetHead()
        while node:
            p = node.GetData()
            p.products = nueva_cantidad
            t_node = p.tasks.GetHead()
            while t_node:
                t_node.GetData()._initial_products = nueva_cantidad
                t_node = t_node.next
            node = node.next

    simulation['running'] = True
    simulation['done']    = False
    simulation['paused']  = False
    prod.done             = False
    prod.paused           = False
    prod.current_t        = 0

    threading.Thread(target=_run_simulation, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/api/pausar', methods=['POST'])
def pausar():
    simulation['paused'] = not simulation['paused']
    prod.paused = simulation['paused']
    return jsonify(_get_estado())

@app.route('/api/estado', methods=['GET'])
def estado():
    return jsonify(_get_estado())

@app.route('/api/procesos-creados', methods=['GET'])
def procesos_creados():
    lista = []
    node = simulation['process_list'].GetHead()
    i = 0
    total = 0
    while node:
        node = node.next
        total += 1
    node = simulation['process_list'].GetHead()
    while node:
        p = node.GetData()
        es_inicial = (i == 0)
        es_final   = (i == total - 1)
        lista.append({
            'nombre':   p.name,
            'productos': simulation['cantidad_global'],
            'n_tareas':  p.n_tasks,
            'inicial':   es_inicial,
            'final':     es_final
        })
        node = node.next
        i += 1
    return jsonify({
        'procesos': lista,
        'cantidad_global': simulation['cantidad_global']
    })

# ── Lógica de simulación ───────────────────────────────────────────────────────

def _get_estado():
    procesos = []
    node = simulation['process_list'].GetHead()
    while node:
        p = node.GetData()
        tareas = []
        t_node = p.tasks.GetHead()
        while t_node:
            t = t_node.GetData()
            tareas.append({
                'n':              t.n,
                'procesando':     t.is_processing,
                'en_cola':        t.queue_n,
                'tiempo_proceso': t.processing_t,
                'completados':    p.products - t.products,
                'total':          p.products,
                'producto_actual': t.current if t.is_processing else None
            })
            t_node = t_node.next
        procesos.append({'nombre': p.name, 'tareas': tareas})
        node = node.next
    return {
        'procesos': procesos,
        'tiempo':   simulation['current_t'],
        'paused':   simulation['paused'],
        'running':  simulation['running']
    }

def _run_simulation():
    print(f"=== Iniciando simulación: {simulation['cantidad_global']} producto(s) ===")
    # Resetea todos los procesos; marca cuál es el primero para el encolado inicial
    node = simulation['process_list'].GetHead()
    is_first = True
    while node:
        p = node.GetData()
        p.is_first = is_first
        p.Reset()
        is_first = False
        node = node.next

    # Re-encadena la línea: también une última tarea de P[i] con primera de P[i+1]
    prod.set_next_process(simulation['process_list'].GetHead())

    # Clock y emit loop
    clock_thread = threading.Thread(target=prod.cycle, daemon=True)
    clock_thread.start()
    emit_thread = threading.Thread(target=_emit_loop, daemon=True)
    emit_thread.start()

    # Arranca TODOS los procesos simultáneamente (pipeline)
    node = simulation['process_list'].GetHead()
    while node:
        node.GetData().StartThreads()
        node = node.next

    # Espera a que todos terminen (P1 termina antes que P2, etc.)
    node = simulation['process_list'].GetHead()
    while node:
        node.GetData().JoinThreads()
        node = node.next

    prod.done = True
    simulation['running'] = False
    simulation['done']    = True
    simulation['current_t'] = prod.current_t
    socketio.emit('simulacion_terminada', _get_estado())

def _emit_loop():
    """Solo lee estado y emite al UI. No toca el timing."""
    while simulation['running']:
        while simulation['paused']:
            time.sleep(0.1)
        simulation['current_t'] = prod.current_t
        socketio.emit('tick', _get_estado())
        time.sleep(0.5)  # refresca la UI dos veces por segundo

# ── SocketIO ───────────────────────────────────────────────────────────────────

@socketio.on('connect')
def on_connect():
    emit('estado', _get_estado())

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)
