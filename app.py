from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
from prod import Process, LinkedList, cycle, set_next_process, lock
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'linprod-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Estado global de la simulación
simulation = {
    'process_list': LinkedList(),
    'running': False,
    'paused': False,
    'current_t': 0,
    'done': False,
    'processes_config': []  # guarda config para poder reiniciar
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
    nombre = data.get('nombre')
    cantidad = int(data.get('cantidad_producto'))
    tareas = data.get('tareas', [])  # lista de {tiempo_proceso: N}

    p = Process(nombre, cantidad)
    for t in tareas:
        p.CreateTask(int(t['tiempo_proceso']))
    p.QueueProducts()

    simulation['process_list'].Insert(p)
    simulation['processes_config'].append(data)

    return jsonify({'ok': True, 'mensaje': f'Proceso "{nombre}" creado'})

@app.route('/api/iniciar', methods=['POST'])
def iniciar():
    if simulation['running']:
        return jsonify({'ok': False, 'mensaje': 'Ya hay una simulación corriendo'})

    set_next_process(simulation['process_list'].GetHead())
    simulation['running'] = True
    simulation['done'] = False

    threading.Thread(target=_run_simulation, daemon=True).start()
    return jsonify({'ok': True})

@app.route('/api/pausar', methods=['POST'])
def pausar():
    simulation['paused'] = not simulation['paused']
    return jsonify({'paused': simulation['paused']})

@app.route('/api/estado', methods=['GET'])
def estado():
    return jsonify(_get_estado())

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
                'n': t.n,
                'procesando': t.is_processing,
                'en_cola': t.queue_n,
                'tiempo_proceso': t.processing_t,
                'completados': p.products - t.products if hasattr(t, 'products') else 0
            })
            t_node = t_node.next
        procesos.append({'nombre': p.name, 'tareas': tareas})
        node = node.next
    return {'procesos': procesos, 'tiempo': simulation['current_t'], 'paused': simulation['paused']}

def _run_simulation():
    import prod
    prod.done = False
    prod.current_t = 0

    head = simulation['process_list'].GetHead()
    if head is None:
        return

    clock_thread = threading.Thread(target=_clock, daemon=True)
    clock_thread.start()

    head.GetData().StartThreads()
    head.GetData().JoinThreads()

    simulation['running'] = False
    simulation['done'] = True
    socketio.emit('simulacion_terminada', {})

def _clock():
    import prod
    while not prod.done and simulation['running']:
        while simulation['paused']:
            time.sleep(0.1)
        with prod.lock:
            simulation['current_t'] = prod.current_t
            socketio.emit('tick', _get_estado())
        time.sleep(1)
        prod.current_t += 1

# ── SocketIO ───────────────────────────────────────────────────────────────────

@socketio.on('connect')
def on_connect():
    emit('estado', _get_estado())

if __name__ == '__main__':
    socketio.run(app, debug=True, use_reloader=False)
