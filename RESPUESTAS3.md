# Tercera parte: Rastreando la prioridad de los procesos

## Nueva información de los procesos

La información que se decidió agregar para cada proceso fue la siguiente:

 - Prioridad: necesaria para MLFQ, nos marca la prioridad de ejecución del proceso y, por ende, en qué queue debe estar. El límite de prioridad es `NPRIO`, el cual se encuentra definido en [`param.h`](kernel/param.h).

 - Popularidad: la cantidad de veces que el proceso fue scheduleado por nuestro planificador

 - Firstelection: la cantidad de veces que el proceso fue scheduleado por nuestro planificador al principio de un quantum (es decir, luego de una interrupción por timer). En caso que venga luego del blocked de otro proceso, no se considera.

Todas fueron agregadas dentro del campo de la estructura `struct proc` con los nombres correspondientes a:

 - priority

 - popularity

 - firstelection

Además, fueron agregadas en el `printf` de `procdump`, de modo que cuando se la invoque con CTRL-P, se imprima esta información. El orden en el que van a mostrarse va a ser `PID, Priority, Firstelection, Popularity, State, Name`.

Respecto a cómo se modifica cada una de estas, podemos verlo a continuación.

### Prioridad

Los cambios que pueden darse en la prioridad de un proceso, siguiendo las reglas 3 y 4 son los siguientes:

 - Regla 3 (**prioridad por defecto**): cada proceso nuevo (i.e., que es allocado en `allocproc`) tiene asignada como prioridad la máxima (i.e., `NPRIO-1`), lo cual se consigue seteando este campo en la función donde se realiza el alocamiento de este.
 
 - Regla 4:

    - **Descenso de prioridad**: Cada vez que el proceso pasa todo un quantum realizando cómputo, se le baja la prioridad. Si bien no se puede saber con exactitud si pasó todo el quantum (porque puede suceder que primero lo tome un proceso iobench, haga una request de IO y luego sea scheduleado cpubench teniendo menos tiempo que un quantum), vamos a considerar al proceso cuya ejecución es interrumpida por una interrupción por timer (i.e., cuando se acabó el quantum). Por ello mismo, todo proceso que vaya a `sched` desde `yield` se le baja la prioridad.

    - **Ascenso de prioridad**: Cada vez que un proceso se bloquea antes de que termine el quantum, su prioridad va a ser aumentada. Esto se consigue si el proceso llega a la función `sched` desde `sleep`.

### Popularidad

La popularidad de un proceso es simplemente la cantidad de veces que este fue scheduleado por el planificador. Luego, debe ser seteado en `allocproc` en 0 y cada vez que sea seleccionado en `scheduler`, antes de realizar el context switch se aumenta su popularidad.

### Firstelection

Este campo es un poco más complejo que los anteriores ya que la idea es la misma que con la popularidad solo que se suma siempre y cuando se haya seleccionado al principio de un quantum (es decir, luego de una interrupción por timer, no porque otro proceso se haya bloqueado).

Por ello mismo, entonces se usa el array global `uint timerinterruption[NCPU]` que especifica con un 1 si el CPU recibió una interrupción por timer o 0 en caso contrario (el índice en el arreglo es la cpuid). Luego, esto significa que tenemos:

 - Si hay interrupción por timer: en `yield` se setea `timerinterruption[cpuid()]` en 1
 - Si no hay interrupción por timer: no se hace nada

Y respecto al aumento de `p->firstelection`, este funciona del mismo modo que `p->popularity` respecto al seteo y a su aumento, salvo las siguientes modificaciones:

 - En `scheduler`, en vez de sumarle 1, se suma `timerinterruption[cpuid()]`, lo que va a aumentar solo si viene desde yield
 - Luego del aumento, se setea `timerinterruption[cpuid()]` en 0 porque el siguiente, a menos que se produzca otra interrupción por timer, no es elegido al principio de un quantum

# Cuarta parte (y algún extra): Implementación de MLFQ

## Implementación

En las siguientes secciones se va a repasar la implementación de MLFQ realizada pasando por la estructura de datos usada, las funciones auxiliares de queue, las modificaciones en el scheduler y la realización del priority boost.

### Estructura de datos a usar

Para implementar MLFQ, se decidió cambiar la estructura de datos de los procesos a la siguiente:
```c
struct proctable
{
  uint cnt,maxprior;
  struct proc list[NPROC];
  struct proc *queue[NPRIO][NPROC];
  uint ini[NPRIO],size[NPRIO];
  struct spinlock lock;
} proc;
```

de modo que se pueda disponer de las queues para realizar la planificación de procesos de la forma más sencilla posible. Cada uno de los datos de la estructura sirve para lo siguiente:

 - **`cnt`**: cantidad de procesos en estado RUNNABLE

 - **`maxprior`**: máxima prioridad entre los procesos en estado RUNNABLE

 - **`list[NPROC]`**: lista de procesos. Tiene exactamente el mismo functionamiento que el XV6 por defecto. El único cambio que se realizó respecto a esta fue en su iteración ya que los procesos van a iterarse desde `proc.list` hasta `&proc.list[NPROC]`

 - **`*queue[NPRIO][NPROC]`**: queue de los procesos en estado RUNNABLE. Son punteros a los procesos que se encuentran en `proc.list` y son divididos según su prioridad. Se decidió implementarlo de forma estática por sencillez.

 - **`ini[NPRIO]`**: marca dónde inicia la queue correspondiente a la prioridad indexada

 - **`size[NPRIO]`**: marca cuántos procesos en estado RUNNABLE tiene la queue correspondiente a la prioridad indexada

 - **`lock`**: es el lock que vamos a utilizar para bloquear la tabla de procesos (solo lo relacionado con las queues) en los lugares críticos (encolamientos, desencolamientos y priority boost).

### Funciones auxiliares para queues

Para facilitar la realización del planificador, se decidió abstraer las operaciones de encolamiento y desencolamiento de procesos en la queue.

La idea para implementar la queue por prioridad de forma estática fue una matriz en donde la primera indexación marque la prioridad, de modo que nos queda el arreglo correspondiente a la queue. La queue fue realizada de modo que sea un arreglo estático circular (después del último elemento sigue el primero), por lo cual es importantísimo saber dónde inicia y dónde termina (o cuánto "mide", es decir, cuántos elementos tiene). Por ello mismo, las posiciones y las iteraciones en las queues son realizadas con posiciones modulares respecto a `NPROC` usando la función:

```c
uint
index(uint pos)
{
  return (pos+NPROC)%NPROC;
}
```

Sabiendo esto, queda ver cómo se realizan los encolamientos y cómo los desencolamientos. Veamos cada caso:

#### Encolar un proceso

Es una función de tipo `void` que recibe como parámetro un puntero a `struct proc` y lo encola en la queue correspondiente a la prioridad del proceso.

Para realizar esto último, siempre y cuando no se exceda el límite de procesos, se coloca el puntero en `proc.queue[prior][index(ini+size)]` y se aumenta el size de la queue.

Luego, en caso que la prioridad sea mayor a `proc.maxprior`, se actualiza esta última.

Además, para que no haya conflicto entre diferentes threads, esta función siempre debe ser usada dentro de un lockeo de la tabla de procesos. Es decir, entre `acquire(&proc.lock)` y `release(&proc.lock)`.

#### Desencolar un proceso

Es una función de tipo puntero a `struct proc` que no recibe parámetros y lo que hace es desencolar el proceso con la prioridad más alta y devolverlo a quien llamó la función. En caso que no haya ninguno, retorna 0 (un equivalente a `NULL`).

Para esto, es súmamente importante la variable `proc.maxprior` ya que nos dice de qué queue desencolar el primer elemento. Por ello mismo, el puntero que va a retornarse va a ser el que se encuentra en `proc.queue[prior][index(ini)]`, posición que después va a ser pisada con un 0. Luego, se aumenta el inicio de la queue y se reduce su size.

Respecto a la máxima prioridad, se itera por todas las queues para guardar la prioridad más alta en la que hay algún proceso. Esto se hace con la idea de actualizar esta variable.

Además, para que no haya conflicto entre diferentes threads, esta función siempre debe ser usada dentro de un lockeo de la tabla de procesos. Es decir, entre `acquire(&proc.lock)` y `release(&proc.lock)`.

Y, por último, se recalca que esta función ya lockea el proceso desencolado por lo que en el scheduler simplemente hay que hacer release en caso que sea distinto de 0.

### Modificaciones en el scheduler

Dado todo lo anterior, queda saber
 
 - ¿Dónde se encolan los procesos?
 - ¿Dónde se desencolan los procesos?

Respecto a la primera, como la idea es que las queues tengan solo procesos en estado RUNNABLE, estos van a encolarse cuando su estado sea cambiado al mecionado. Es decir, en las funciones correspondientes a:

 - `userinit`

 - `fork`

 - `yield`

 - `wakeup`

 - `kill`

siempre con la tabla de procesos lockeada antes de la enqueue y deslockeada después.

Luego, respecto a la segunda, un proceso es desencolado sólo cuando este cambie su estado RUNNABLE, es decir, cuando pase a RUNNING. Esto solo se realiza en el planificador, es decir, en la función `scheduler.

Ahora, sabiendo lo anterior, el scheduler queda de la siguiente forma:

```c
void
scheduler(void)
{
  struct proc *p;
  struct cpu *c = mycpu();
  uint id = cpuid();
  
  c->proc = 0;
  for(;;){
    // Avoid deadlock by ensuring that devices can interrupt.
    intr_on();

    acquire(&proc.lock);

    // Priority boost
    if(ticks % NBOOST == 0 && ticks != antboost){
      antboost = ticks;
      priority_boost();
    }
    
    if((p = deque()) != 0){
      release(&proc.lock);
      // Switch to chosen process.  It is the process's job
      // to release its lock and then reacquire it
      // before jumping back to us.
      p->state = RUNNING;
      p->popularity++;
      p->firstelection += timerinterruption[id];
      timerinterruption[id] = 0;
      c->proc = p;
      swtch(&c->context, &p->context);

      // Process is done running for now.
      // It should have changed its p->state before coming back.
      c->proc = 0;
      release(&p->lock);
    }else release(&proc.lock);
    
  }
}
```

en donde puede notarse que se realiza un ciclo infinito en el cual se lockea la tabla de procesos y se hace la deque del proceso correspondiente (del priority boost se va a hablar en la siguiente sección).

En caso que el proceso desencolado exista (i.e., sea distinto de 0), va a:

 - lockearse (lo hace `deque`)

 - cambiar su estado a RUNNING

 - aumentar la popularidad

 - aumentar el firstelection (en caso que venga desde `yield` la interrupción)

 - asignarse al cpu en el que se corrió la instancia del planificador

 - hacer el context switch

 - desligarse del cpu (cuando termina de ejecutarse, es decir, después de que pase por `sched`)

 - deslockearse

### Realización del Priority Boost

Finalmente, y ya respecto a este punto extra, nuestro planificador cuenta con el priority boost (en reemplazo de la regla de ascenso de prioridad de la 3era parte), el cual se realiza cada `NBOOST` ticks (es `1 << 8` y está puesto en [`param.h`](kernel/param.h)) y, básicamente, lo que hace se puede ver a continuación:

```c
void
priority_boost()
{
  struct proc *p;
  
  // Erase all process into the queue
  while((p = deque()) != 0)
    release(&p->lock);
  
  // Increment the priority for all process and insert into the queue
  for(p = proc.list; p < &proc.list[NPROC]; p++){
    if(p->state != UNUSED){
      p->priority = NPRIO-1;
      if(p->state == RUNNABLE)
        enqueue(p);
    }
  }
}
```
 
siendo, simplemente:

 - lockeo de la tabla de procesos (instrucción anterior al if en el scheduler)

 - desencolamiento de todos los procesos de las queues

 - se itera por la lista de procesos y, en caso que el estado no sea UNUSED (es decir, sea un proceso), se setea su prioridad en la máxima (`NPRIO-1`) y si es RUNNABLE, se lo encola nuevamente.

y luego sigue con la ejecución normal del scheduler, deslockeando luego la tabla de procesos.

**IMPORTANTE**: debido a que los ticks en el scheduler se repiten (porque no todos vienen desde yield), se decidió usar la variable global `antboost` en donde va a estar el valor del tick en el que se realizó el anterior priority boost y usarlo como condición en el condicional. Esto permite que se haga una sola vez esta acción cada `NBOOST` ticks.

## Mediciones

## ¿Se produce starvation?