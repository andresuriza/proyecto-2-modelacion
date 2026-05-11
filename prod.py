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

        # Se encolan productos a la primera tarea
        for _ in range(self.products):
            head.GetData().Queue()

        while head != None:

            # Tarea referencia a la siguiente
            if head.next != None:
                head.GetData().SetNext(head.next.GetData())

            head = head.next


    # Comienza a ejecutar las tareas
    def StartThreads(self):
        print(f"\033[91m --- {self.name} --- \033[0m")

        # Crea threads frescos cada vez (los threads de Python no se pueden reiniciar)
        self.threads = []
        node = self.tasks.GetHead()
        while node:
            self.threads.append(threading.Thread(target=node.GetData().Run, daemon=True))
            node = node.next

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

            time.sleep(0.05)  # evita busy-wait que bloquea el GIL

            if self.is_processing:
                # Mientras queden productos
                if self.queue_n > 0:
                    # >= en vez de == para no perderse un ciclo si el thread se atrasa
                    if ((current_t - prev_t) >= self.processing_t):
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

# Pide al usuario ingresar cuantas tareas desee al proceso de entrada
def input_tasks(p):
    print("Digite tareas:")

    p.CreateTask(int(input("Tiempo proceso= ")))

    while True:
        req = input("Requiere otra tarea? ").lower()
        if req == "s":
            p.CreateTask(int(input("Tiempo proceso= ")))
        elif req == "n":
            p.QueueProducts()
            break
        else:
            print("Uso incorrecto: por favor escribir 's' o 'n'")

def set_next_process(head):
    tmp = head

    while tmp.next != None:
        tmp.GetData().SetNext(tmp.next.GetData())
        tmp = tmp.next


if __name__ == '__main__':
    process_list = LinkedList()

    first_p = Process(input("Digite proceso: "), int(input("Numero de productos=")))
    input_tasks(first_p)
    first_p.SetEnabled()

    process_list.Insert(first_p)

    while True:
        req = input("Crear otro proceso? ").lower()

        if req == "s":
           p = Process(input("Digite proceso: "), int(input("Numero de productos=")))
           input_tasks(p)
           process_list.Insert(p)
        elif req == "n":
            break
        else:
            print("Uso incorrecto: por favor escribir 's' o 'n'")

    # Asociar procesos entre si
    set_next_process(process_list.GetHead())

    t1 = threading.Thread(target=cycle)

    process_list.GetHead().GetData().SetEnabled()

    t1.start()
    process_list.GetHead().GetData().StartThreads()
    process_list.GetHead().GetData().JoinThreads()