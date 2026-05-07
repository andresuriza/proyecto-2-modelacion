import time

class Process:
    def __init__(self, name):
        self.name = name
        self.tasks = None
        self.n_tasks = 0

    # Agrega una tarea al proceso
    def CreateTask(self, processing_t, is_processing, queue_n):
        if self.tasks == None:
            self.n_tasks = 1
            self.tasks = Node(Task(1, processing_t, is_processing, queue_n))
        else:
            new_val = Node(Task(self.n_tasks, processing_t, is_processing, queue_n))
            tmp = self.tasks

            while tmp.next != None:
                tmp = tmp.next

            tmp.next = new_val
        
        self.n_tasks += 1
    
    def ViewTasks(self):
        tmp = self.tasks

        while tmp != None:
            print(f"Tarea{tmp.data.GetN()}")
            print(f"Tiempo proceso = {tmp.data.GetProcessingT()}")
            print(f"Esta procesando? = {tmp.data.GetIsProcessing()}")
            print(f"Contenido esperando = {tmp.data.GetQueueN()}")
            tmp = tmp.next
        
class Task:
    def __init__(self, n, processing_t, is_processing, queue_n):
        # Numero de tarea
        self.n = n
        # Tiempo de procesamiento
        self.processing_t = processing_t
        # Bool, se esta procesando?
        self.is_processing = is_processing
        # Contenido encolado
        self.queue_n = queue_n
    
    def SetProcessingT(self, t):
        self.processing_t = t

    def SetIsProcessing(self, bool):
        self.is_processing = bool

    def SetQueueN(self, n):
        self.queue_n = n
    
    def GetN(self):
        return self.n

    def GetProcessingT(self):
        return self.processing_t

    def GetIsProcessing(self):
        return self.is_processing

    def GetQueueN(self):
        return self.queue_n
        

p = Process(input("Digite proceso: "))
print("Digite tareas:")

processing_t = input("Tiempo proceso=")
is_processing = input("Esta procesando=")
queue_n = input("Contenido esperando=")

p.CreateTask(processing_t, is_processing, queue_n)


while True:
    req = input("Requiere otra tarea? ").lower()

    if req == "s":
        processing_t = input("Tiempo proceso=")
        is_processing = input("Esta procesando=")
        queue_n = input("Contenido esperando=")
        p.CreateTask(processing_t, is_processing, queue_n)
        
    elif req == "n":
        break
    else:
        print("Invalido, por favor ingresar 's' o 'n'")

p.ViewTasks()

# print("Lets wait 5 seconds")
# start = time.time()
# time.sleep(5)
# end = time.time()
# elapsed = round(end-start)
# print(f"According to Python, this took exactly {elapsed} seconds!")

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

my_list = Node(1)

def insert(head, val):
    new_val = Node(val)
    tmp = head

    while tmp.next != None:
        tmp = tmp.next
    
    tmp.next = new_val

def remove_first(head):
    head = head.next
    return head

def remove_last(head):
    tmp = head

    if tmp.next == None:
        tmp = None
    else:
        while tmp.next.next != None:
            tmp = tmp.next
        tmp.next = None
    print(tmp)

for i in range(5):
    insert(my_list, i+2)

def print_list(head):
    tmp = head

    while tmp != None:
        print(tmp.data)
        tmp = tmp.next

print_list(my_list)
