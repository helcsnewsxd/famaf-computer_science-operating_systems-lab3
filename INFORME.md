# Laboratorio número 3 de Sistemas Operativos 2022 - Grupo 12 | FaMAF UNC

## Integrantes del grupo:

- Lautaro Bachmann (lautaro.bachmann@mi.unc.edu.ar)
- Juan Bratti (juanbratti@mi.unc.edu.ar)
- Gonzalo Canavesio (gonzalo.canavesio@mi.unc.edu.ar)
- Emanuel Herrador (emanuel.nicolas.herrador@unc.edu.ar)


# Índice

 - [Introducción](#markdown-header-introduccion)
 - [¿Cómo correr el código?](#markdown-header-como-correr-el-codigo)
 - [Implementación del Proyecto](#markdown-header-implementación-del-proyecto)
    - [Primera Parte](#markdown-header-primera-parte)
        - [Pregunta 1](#markdown-header-pregunta-1)
        - [Pregunta 2](#markdown-header-pregunta-2)
    - [Segunda Parte](#markdown-header-segunda-parte)
    - [Tercera Parte](#markdown-header-tercera-parte)
        - [Nueva información de los procesos](#markdown-header-nueva-información-de-los-procesos)
        - [Prioridad](#markdown-header-prioridad)
        - [Popularidad](#markdown-header-popularidad)
        - [Firstelection](#markdown-header-firstelection)
    - [Cuarta Parte](#markdown-header-cuarta-parte)
 - [Herramientas de Programación](#markdown-header-herramientas-de-programacion)
 - [Desarrollo del proyecto](#markdown-header-desarrollo-del-proyecto)
 - [Conclusión](#markdown-header-conclusion)
 - [Webgrafía](#markdown-header-webgrafia)

# Introducción
En este laboratorio nos centramos en conocer el funcionamiento de xv6 con relación a la administración de los recursos usados por los procesos. Trabajamos sobre el algoritmo responsable del sistema de planificación (Round Robin), sus detalles de implementación en xv6 y su comportamiento ante exigencias de IO y/o CPU. También, implementamos un planificador de procesos nuevo, inspirándonos en MLFQ. Para ello, agregamos prioridades a los procesos y, como punto extra, implementamos un priority boost.
Por último, con ayuda de un script realizado en python, llevamos a cabo un estudio meticuloso sobre el rendimiento de los distintos planificadores en diversos casos y escenarios.

# ¿Cómo correr el código?
## Instalación
1. Clonar repositorio: `git clone https://bitbucket.org/sistop-famaf/so22lab2g12.git`
2. Instalar qemu (ubuntu): `sudo apt-get install qemu-system-riscv64`
    - Para otras distribuciones ver este [link](https://pdos.csail.mit.edu/6.828/2019/tools.html).

## Compilación y ejecución
### Compilar y ejecutar XV6
Ejecutar en *so22lab3g12/* el siguiente comando: 
```sh
make CPUS=1 qemu
```

# Implementación del proyecto

## Primera Parte
En esta primera parte, la mayoría del trabajo constó en conocer el funcionamiento del planificador de xv6 y responder las siguientes preguntas:

### **Pregunta 1**

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

### **Pregunta 2**

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

## Segunda Parte
En esta segunda parte del laboratorio, nos centramos en cuantificar el rendimiento del planificador con respecto a procesos CPU-bound e IO-bound. Realizamos mediciones y comparaciones entre el planificador por default en xv6, y el implementado (MLFQ). Las mediciones y sus conlusiones se pueden leer en el siguiente apartado: [**Mediciones**](/respuestas_mediciones.md)

## Tercera Parte
Aquí se comenzó a repensar el planificador de xv6 para que su funcionamiento se dicte por una ejecución prioritaria de los procesos, es decir, implementando un planificador MLFQ. Previo a esta implementación, en esta parte se introdujeron algunas variables y campos necesarios para su correcto funcionamiento.

### Nueva información de los procesos

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


## Cuarta Parte
Finalmente, se implementó por completo un planificador al estilo MLFQ.
### Implementación

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


# Herramientas de Programación
Las principales herramientas utilizadas por el grupo en la implementación y división del proyecto fueron las siguientes:

## *Material teórico de estudio y preparación*

 - [**Operating Systems: Three Easy Pieces**: Process virtualization](https://pages.cs.wisc.edu/~remzi/OSTEP/), principalmente el capítulo número 5 (*Process API*) y los capitulos de la sección de Concurrencia, sobre todo el capítulo número 31 (*Semaphores*), junto con las secciones de *Homework Simulation* y *Homework Code* de cada uno de esos capitulos.
 - [**Documentación de XV6**](https://course.ccs.neu.edu/cs3650/unix-xv6/index.html)
 - [**Repositorio XV6**](https://github.com/mit-pdos/xv6-book) 

### Conceptos teóricos utilizados
 - Planificador MLFQ y RR, reglas y funcionamiento
 - Quantum y context switch
 - Timer interrupts, ticks de reloj

## *Desarrollo*

 - [Visual Studio Code](https://code.visualstudio.com/), editor de código

## *Compilación*

- [GNU Make](https://www.gnu.org/software/make/)

## *Debugging*

- [GDB](https://sourceware.org/gdb/), depurador estándar para el compilador GNU.

# Desarrollo del proyecto

## *Problemas*
[AGREGAR]

## *Comunicación*
La comunicación se basó fuertemente en plataformas como [Discord](https://discord.com/), donde la comunicación es más organizada y se pueden hacer llamadas de voz, y [Telegram](https://telegram.org/), donde conseguimos una comunicación más veloz e informal. 

## *Workflow de desarrollo*
### *Branches*
Nuestro workflow se apoyó fuertemente en el uso de branchs dentro del repositorio de bitbucket. Para cada parte del proyecto, primero se creaba una nueva branch para desarrollarlo y cuando ya estaba completado, era fusionado a la rama principal

# Conclusiones
Este trabajo nos ayudó a entender de forma directa y real, el papel importante que toma un planificador de recursos y sus demás componentes en el funcionamiento del sistema operativo. Aprendimos cómo hace el OS para regular el tráfico de procesos y cómo administra el uso del procesador para ejecutar los mismo de forma eficiente, sin sobrecargar al CPU. También, gracias al estudio del código de xv6, entendimos cómo las partes vistas en los laboratorios se unen de forma íntegra para beneficiar un adecuado funcionamiento del OS.
Pudimos recorrer aquellas bases fundamentales de los planificadores de procesos gracias al estudio de los algoritmos de RR y MLFQ, como así también realizar un análisis métrico de sus rendimientos en distintos casos y escenarios.
