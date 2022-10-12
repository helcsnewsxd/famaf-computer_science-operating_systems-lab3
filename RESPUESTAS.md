# Primera Parte: Estudiando el planificador de xv6

## Pregunta 1

### ¿Qué política de planificación utiliza xv6 para elegir el próximo proceso a ejecutarse?

XV6 usa [**Round Robin**](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf) (RR) como política de planificación para elegir el próximo proceso a ejecutarse. Este scheduling funciona como se describe a continuación.

Se establece una run queue de procesos del mismo modo que la FIFO. Sin embargo, en vez de ejecutar un proceso hasta que finalice, lo ejecuta como máximo por un período de tiempo (*time slice*) conocido comúnmente como **quantum**. Una vez que al proceso actual se le haya acabado el quantum, este pasa a estar al final de la queue (en caso que no esté completo aún) y se switchea al siguiente en la cola.
Esto se realiza de forma repetida hasta que todos los procesos son terminados.

Respecto a la implementación en este SO, puede observarse en [proc.c](/kernel/proc.c) que la estructura de datos es, simplemente, un array estático de 64 elementos (`proc[NPROC]`) de tipo `struct proc`, el cual es la tabla de procesos.

En el scheduler, para simular una queue se usa como un arreglo circular (después del final va el principio), de modo que cuando se encuentra con un proceso en estado *RUNNABLE*, se lo asigna a la CPU y hace el cambio de contexto (context switch) pasando de kernel a user con `swtch` con el proceso actual. Se vuelve al scheduler cuando se haya acabado el quantum mediante una interrupción, de modo que se "desligue" el CPU y se itere por el siguiente en la lista.

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

### ¿Cuánto dura un cambio de contexto en xv6?

### ¿El cambio de contexto consume tiempo de un quantum?

### ¿Hay alguna forma de que a un proceso se le asigne menos tiempo?