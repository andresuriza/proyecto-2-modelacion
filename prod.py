import threading
import time

current_t = 0
done = False

def cycle():
    while not done:
        global current_t
        print(f"---- Tiempo: {current_t}-----")
        time.sleep(1)
        current_t += 1

class Process:
    def __init__(self, name, products):
        self.products = products
        self.name = name
        self.tasks = []
        self.n_tasks = 0
    
    def CreateTask(self, processing_t):
        self.tasks.append(Task(1, processing_t, self.products))

    def Run(self):
        for t in self.tasks:
            # Ejecute task y espere a que termine producto
            while t.Run() == False:
                pass         

class Task:
    def __init__(self, n, processing_t, next):
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
        while True:
            if self.is_processing:
                # Tiempo en que inicio para comparar
                prev_t = current_t

                print(f"Tarea{self.n}")
                print(f"Procesando producto #{self.current}")
                self.is_processing = True
                print(f"Se esta procesando? {self.is_processing}")
                self.queue_n -= 1
                print(f"Encolados: {self.queue_n}")
                self.current += 1

                # Mientras queden productos
                while self.queue_n > 0:
                    if (current_t == (prev_t + self.processing_t)):
                        print(f"Tarea{self.n}")
                        print(f"Procesando producto #{self.current}")
                        self.is_processing = True
                        print(f"Se esta procesando? {self.is_processing}")
                        self.queue_n -= 1
                        print(f"Encolados: {self.queue_n}")
                        self.current += 1
                        prev_t = current_t

                        # Pasar producto a la siguiente tarea si existe
                        if self.next != None:
                            self.next.Queue()
                            
                if self.queue_n == 0:
                    self.is_processing = False

def main():
    products = 5
    
    t1 = threading.Thread(target=cycle)
    
    task2 = Task(2, 2, None)
    task1 = Task(1, 1, task2)

    for p in range(products):
        task1.Queue()

    t2 = threading.Thread(target=task1.Run)
    t3 = threading.Thread(target=task2.Run)

    # Iniciar los threads
    t1.start()
    t2.start()
    t3.start()

    # Join los threads
    t1.join()
    t2.join()
    t3.join()

main()