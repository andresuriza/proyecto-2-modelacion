import threading
import time

current_t = 0
done = False
lock = threading.Lock()

# Contador de ciclos
def cycle():
    while not done:
        global current_t
        lock.acquire()
        print(f"---- Tiempo: {current_t}-----")
        lock.release()
        time.sleep(1)
        current_t += 1

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Process:
    def __init__(self, name, products):
        self.products = products
        self.name = name
        self.threads = []
        self.tasks = []
        self.n_tasks = 0
    
    def CreateTask(self, processing_t):
        self.n_tasks += 1
        t = Task(self.n_tasks, processing_t, None, self.products)
        self.tasks.append(t)
        self.threads.append(threading.Thread(target=t.Run))

    def QueueProducts(self):
        for task in self.tasks:
            for _ in range(self.products):
                task.Queue()

    def JoinThreads(self):
        for task in self.threads:
            task.join()

    def StartThreads(self):
        for task in self.threads:
            task.start()

class Task:
    def __init__(self, n, processing_t, next, products):
        self.products = products
        self.next = next
        # Numero de tarea
        self.n = n
        # Tiempo de procesamiento
        self.processing_t = processing_t
        # Bool, se esta procesando?
        self.is_processing = False
        # Contenido encolado
        self.queue_n = 0
        self.current = 1

    def Queue(self):
        if not self.is_processing:
            self.is_processing = True
            
        self.queue_n += 1
    
    def Run(self):
        prev_t = current_t

        while True:
            # Ya termino, no mas bucle
            if self.products == 0:
                break

            if self.is_processing:
                # Mientras queden productos
                if self.queue_n > 0:
                    # Si ha transcurrido ya el tiempo necesario
                    if ((current_t - prev_t) == self.processing_t):
                        lock.acquire()
                        print(f"Tarea{self.n}")
                        print(f"Procesando producto #{self.current}")
                        print(f"Se esta procesando? {self.is_processing}")
                        # Se desencola
                        self.queue_n -= 1
                        print(f"Encolados: {self.queue_n}")
                        lock.release()
                        # Pasa a siguiente producto
                        self.current += 1
                        # El tiempo empieza a contar a partir de ahora
                        prev_t = current_t
                        self.products -= 1

                        # Pasar producto a la siguiente tarea si existe
                        if self.next != None:
                            self.next.Queue()
                
                # Si no le han llegado mas productos, se espera
                if self.queue_n == 0:
                    self.is_processing = False
            else:
                prev_t = current_t

t1 = threading.Thread(target=cycle)
p1 = Process("procesoA", 5)

p1.CreateTask(1)
p1.CreateTask(2)
p1.QueueProducts()

# Iniciar los threads
t1.start()
p1.StartThreads()

# Join los threads
t1.join()
p1.JoinThreads()
