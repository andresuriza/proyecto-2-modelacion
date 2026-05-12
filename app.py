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

@app.route('/procesos')
def procesos():
    return render_template('procesos.html')

@app.route('/estadisticas')
def estadisticas():
    return render_template('estadisticas.html')

# ── API ────────────────────────────────────────────────────────────────────────

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
    prod.done             = False
    prod.current_t        = 0

    threading.Thread(target=_run_simulation, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/api/pausar', methods=['POST'])
def pausar():
    simulation['paused'] = not simulation['paused']
    return jsonify({'paused': simulation['paused']})

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
        'paused':   simulation['paused']
    }

def _run_simulation():
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
