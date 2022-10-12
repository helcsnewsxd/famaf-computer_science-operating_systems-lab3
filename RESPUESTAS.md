# Primera Parte: Estudiando el planificador de xv6

## Pregunta 1

### ¿Qué política de planificación utiliza xv6 para elegir el próximo proceso a ejecutarse?

XV6 usa [**Round Robin**](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf) (RR) como política de planificación para elegir el próximo proceso a ejecutarse. Este scheduling funciona como se describe a continuación.

    Se establece una run queue de procesos del mismo modo que la FIFO. Sin embargo, en vez de ejecutar un proceso hasta que finalice, lo ejecuta como máximo por un período de tiempo (*time slice*) conocido comúnmente como **quantum**. Una vez que al proceso actual se le haya acabado el quantum, este pasa a estar al final de la queue (en caso que no esté completo aún) y se switchea al siguiente en la cola.
    Esto se realiza de forma repetida hasta que todos los procesos son terminados.

Por ello mismo, puede observarse en este SO (más específicamente en [proc.c](/kernel/proc.c)) que la estructura de datos es, simplemente, un array estático de 64 elementos (`proc[NPROC]`) en el cual cada proceso tiene la siguiente estructura:
```c
struct proc {
  struct spinlock lock;

  // p->lock must be held when using these:
  enum procstate state;        // Process state
  void *chan;                  // If non-zero, sleeping on chan
  int killed;                  // If non-zero, have been killed
  int xstate;                  // Exit status to be returned to parent's wait
  int pid;                     // Process ID

  // wait_lock must be held when using this:
  struct proc *parent;         // Parent process

  // these are private to the process, so p->lock need not be held.
  uint64 kstack;               // Virtual address of kernel stack
  uint64 sz;                   // Size of process memory (bytes)
  pagetable_t pagetable;       // User page table
  struct trapframe *trapframe; // data page for trampoline.S
  struct context context;      // swtch() here to run process
  struct file *ofile[NOFILE];  // Open files
  struct inode *cwd;           // Current directory
  char name[16];               // Process name (debugging)
};
```

Teniendo esto en cuenta, Round Robin se realiza en el Scheduler simplemente iterando a lo largo del arreglo repetidas veces y cuando se encuentra con un proceso con estado *RUNNABLE* lo ejecuta usando la función `swtch` para pasar de kernel a user. Esta función retorna cuando se le haya acabado el quantum al proceso de modo que se pueda iterar al siguiente en la lista.

## Pregunta 2

### ¿Cuánto dura un quantum en xv6?

### ¿Cuánto dura un cambio de contexto en xv6?

### ¿El cambio de contexto consume tiempo de un quantum?

### ¿Hay alguna forma de que a un proceso se le asigne menos tiempo?