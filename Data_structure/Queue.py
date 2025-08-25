class Queue:
   
    def __init__(self, capacity=16):
        self.__queue = [None]*capacity
        self.__head = 0
        self.__tail = 0 
        self.__size = 0  

    # Like an array, when fully of capacity, we need to resize to double his capacity
    def __resize(self):
        b = [None]*(len(self.__queue)*2)
        for i in range(self.__size):
            b[i] = self.__queue[(self.__head+i) % len(self.__queue)]
        self.__queue = b
        self.__head = 0
        self.__tail = self.__size

    def push(self, x):
        if self.__size == len(self.__queue): 
            self.__resize()
        self.__queue[self.__tail] = x
        self.__tail = (self.__tail+1) % len(self.__queue)
        self.__size += 1
        
    def pop(self):
        if self.__size == 0: 
            raise IndexError("pop from empty Queue")
        x = self.__queue[self.__head]
        self.__queue[self.__head] = None
        self.__head = (self.__head+1) % len(self.__queue)
        self.__size -= 1
        return x
    
    def empty(self): 
        return self.__size == 0