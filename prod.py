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

    def GetData(self):
        return self.data

class LinkedList:
    def __init__(self):
        self.head = None

    def GetHead(self):
        return self.head
    
    def Insert(self, val):
        if self.head == None:
            self.head = Node(val)

        else:
            new_val = Node(val)
            tmp = self.head

            while tmp.next != None:
                tmp = tmp.next
            
            tmp.next = new_val

class Process:
    def __init__(self, name, products):
        self.enabled = True
        self.next = None
        self.name = name
        self.n_tasks = 0
        self.products = products
        self.threads = []
        self.tasks = LinkedList()

    # Referencia a siguiente proceso
    def SetNext(self, next):
        self.next = next

    def SetEnabled(self):
        self.enabled = True
    
    def CreateTask(self, processing_t):
        self.n_tasks += 1
        t = Task(self.n_tasks, processing_t, self.products)
        self.tasks.Insert(t)
        self.threads.append(threading.Thread(target=t.Run))

    def JoinThreads(self):
        n = len(self.threads)
        for i in range(n):
            self.threads[i].join()

            # Si es la ultima tarea, iniciar proximo proceso
            if (i == (n - 1)):
                if self.next != None:
                    self.next.StartThreads()
                    self.next.JoinThreads()

    def QueueProducts(self):
        head = self.tasks.GetHead()

        while head != None:
            for _ in range(self.products):
                head.GetData().Queue()

            if head.next != None:
                head.GetData().SetNext(head.next.GetData())

            head = head.next


    # Comienza a ejecutar las tareas
    def StartThreads(self):
        print(f"--- {self.name} ---")

        for task in self.threads:
            task.start()

class Task:
    def __init__(self, n, processing_t, products):
        self.products = products
        self.next = None
        # Numero de tarea
        self.n = n
        # Tiempo de procesamiento
        self.processing_t = processing_t
        # Bool, se esta procesando?
        self.is_processing = False
        # Contenido encolado
        self.queue_n = 0
        self.current = 1

    def SetNext(self, next):
        self.next = next

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
p1 = Process("procesoA", 3)
p2 = Process("procesoB", 3)

p1.CreateTask(1)
p1.CreateTask(2)
p1.QueueProducts()

p2.CreateTask(1)
p2.QueueProducts()

p1.SetNext(p2)
p1.SetEnabled()

# Iniciar los threads
t1.start()
p1.StartThreads()

# Join los threads
p1.JoinThreads()