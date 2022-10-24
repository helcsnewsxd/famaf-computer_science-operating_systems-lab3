# Primera Parte: Estudiando el planificador de xv6

## Pregunta 1

### ¿Qué política de planificación utiliza xv6 para elegir el próximo proceso a ejecutarse?

XV6 usa [**Round Robin**](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf) (RR) como política de planificación para elegir el próximo proceso a ejecutarse. Este scheduling funciona como se describe a continuación.

Se establece una run queue de procesos del mismo modo que la FIFO. Sin embargo, en vez de ejecutar un proceso hasta que finalice, lo ejecuta como máximo por un período de tiempo (*time slice*) conocido comúnmente como **quantum**. Una vez que al proceso actual se le haya acabado el quantum, este pasa a estar al final de la queue (en caso que no esté completo aún) y se switchea al siguiente en la cola.
Esto se realiza de forma repetida hasta que todos los procesos son terminados.

Respecto a la implementación en este SO, puede observarse en [proc.c](/kernel/proc.c) que la estructura de datos es, simplemente, un array estático de 64 elementos (`proc[NPROC]`) de tipo `struct proc`, el cual es la tabla de procesos.

En el scheduler, para simular una queue se usa como un arreglo circular (después del final va el principio), de modo que cuando se encuentra con un proceso en estado *RUNNABLE*, se lo asigna a la CPU y hace el cambio de contexto (context switch) pasando de kernel a user con `swtch` con el proceso actual. Se vuelve al scheduler cuando se haya acabado el quantum mediante una interrupción (la cual es tratada por la función `yield`), de modo que se "desligue" el CPU y se itere por el siguiente en la lista.

Viendo esto, es importante destacar que el quantum no es asginado a los procesos en particular, sino que se ejecuta siempre de modo que si alguno termina antes del límite de tiempo, sigue el elegido a continuación con la cantidad de ticks de reloj ya transcurridos (i.e., con el mismo quantum y tiempo transcurrido).

El segmento de código de kernel que se encarga del scheduler de Round Robin está en [proc.c](/kernel/proc.c), siendo:

```c
// Per-CPU process scheduler.
// Each CPU calls scheduler() after setting itself up.
// Scheduler never returns.  It loops, doing:
//  - choose a process to run.
//  - swtch to start running that process.
//  - eventually that process transfers control
//    via swtch back to the scheduler.
void
scheduler(void)
{
  struct proc *p;
  struct cpu *c = mycpu();
  
  c->proc = 0;
  for(;;){
    // Avoid deadlock by ensuring that devices can interrupt.
    intr_on();

    for(p = proc; p < &proc[NPROC]; p++) {
      acquire(&p->lock);
      if(p->state == RUNNABLE) {
        // Switch to chosen process.  It is the process's job
        // to release its lock and then reacquire it
        // before jumping back to us.
        p->state = RUNNING;
        c->proc = p;
        swtch(&c->context, &p->context);

        // Process is done running for now.
        // It should have changed its p->state before coming back.
        c->proc = 0;
      }
      release(&p->lock);
    }
  }
}
```

## Pregunta 2

### ¿Cuánto dura un quantum en xv6?

Dado el funcionamiento de las interrupciones en XV6, podemos notar que los *timer interrupts* son habilitados en [start.c](/kernel/start.c) donde la función que nos interesa para responder la pregunta es `timerinit`.

```c
// arrange to receive timer interrupts.
// they will arrive in machine mode at
// at timervec in kernelvec.S,
// which turns them into software interrupts for
// devintr() in trap.c.
void
timerinit()
{
  // each CPU has a separate source of timer interrupts.
  int id = r_mhartid();

  // ask the CLINT for a timer interrupt.
  int interval = 1000000; // cycles; about 1/10th second in qemu.
  *(uint64*)CLINT_MTIMECMP(id) = *(uint64*)CLINT_MTIME + interval;

  // prepare information in scratch[] for timervec.
  // scratch[0..2] : space for timervec to save registers.
  // scratch[3] : address of CLINT MTIMECMP register.
  // scratch[4] : desired interval (in cycles) between timer interrupts.
  uint64 *scratch = &timer_scratch[id][0];
  scratch[3] = CLINT_MTIMECMP(id);
  scratch[4] = interval;
  w_mscratch((uint64)scratch);

  // set the machine-mode trap handler.
  w_mtvec((uint64)timervec);

  // enable machine-mode interrupts.
  w_mstatus(r_mstatus() | MSTATUS_MIE);

  // enable machine-mode timer interrupts.
  w_mie(r_mie() | MIE_MTIE);
}
```

la cual se encarga de inicializar el timer. En este caso, puede visualizarse cómo setea el quantum en la "comunicación" con el CLINT hardware (core-local interruptor) siendo:
```c
int interval = 1000000; // cycles; about 1/10th second in qemu.
```
lo que equivale aproximadamente a 0.1 segundos en qemu (como se especifica en el comentario).

De igual modo, cabe aclarar, el quantum es de 1000000 ciclos ya que el tiempo "real" depende del procesador y la velocidad en la que se hacen las instrucciones.

### ¿Cuánto dura un cambio de contexto en xv6? ¿El cambio de contexto consume tiempo de un quantum?

Como se ha hablado anteriormente, el cambio de contexto se realiza en [swtch.S](/kernel/swtch.S) bajo la función del mismo nombre, donde simplemente se guardan los registros del *old context* (el del proceso que dejó la CPU) y se cargan los del *new context* (nuevo proceso que se carga en la CPU). La cantidad de instrucciones ejecutadas por el procesador (guardado y cargado del estado de los procesos) son 28.
Como puede visualizarse en la siguiente imagen, el hacer el context switch durante la ejecución del cpubench e iobench de forma paralela (`cpubench &; iobench &`) tarda algunos ciclos de reloj produciendo, a veces, el aumento de un tick de reloj (lo que implica que el quantum terminó y comienza otro):
![](/Figures/Ticks-de-reloj-del-context-switch.png)

Esto se ha obtenido modificando levemente el scheduler en la parte en la que se hace el switcheo:
```c
uint inixticks; // ticks anteriores al switch
acquire(&tickslock);
inixticks = ticks;
release(&tickslock);

swtch(&c->context, &p->context);

uint finxticks; // ticks posteriores al switch
acquire(&tickslock);
finxticks = ticks;
release(&tickslock);

printf("ACTUAL TICK DE RELOJ:\n   Ini --> %d\n   Fin --> %d\n   Diff --> %d\n-------------------\n",inixticks,finxticks,finxticks-inixticks);
```

Finalmente, y respondiendo a la segunda pregunta, el cambio de contexto sí consume tiempo de un quantum ya que este es asignado como interrupción de forma global al SO y no a un proceso en particular (como se mencionó anteriormente).

### ¿Hay alguna forma de que a un proceso se le asigne menos tiempo?

Tal y como se mostró en las respuestas a las preguntas anteriores, más específicamente a la primera, el quantum es asignado mediante un timer interrupt al SO de forma global, no de forma particular a cada proceso. Motivo de esto, puede suceder que un proceso termine antes de la finalización del quantum, por lo que el siguiente elegido por el scheduler va a tener un tiempo menor asignado (el faltante) ya que comienza con el tiempo ya transcurrido.
