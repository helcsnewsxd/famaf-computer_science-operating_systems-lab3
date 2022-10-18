# General

## Problema
Comparar el desempeño de los planificadores Round Robin (por defecto en XV6) y MLFQ (implementado por nosotros), utilizando procesos CPU-bond e IO-bond en XV6 y contrastando con diferentes tamaños de quantum

## Hipótesis
El planificador MLFQ mejorará el desempeño en los procesos IO-bond y empeorará un poquito el desempeño de los procesos CPU-bond.
En general en los ejercicios, mientras menor sea el quantum, mejor desempeño tendrán los procesos IO-bond y peor desempeño los procesos CPU-bond. 

## Datos
Para responder a nuestras hipótesis, mediremos diferentes datos para los procesos IO-bond y los procesos CPU-bond.
Para los procesos IO-bond mediremos cuantas operaciones IO se realizaron (en promedio) durante un lapso de 100 ticks de reloj.
Para los procesos CPU-bond mediremos cuantas "1024 operaciones de punto flotante" (KFLOP) se realizaron (en promedio) durante un lapso de 100 ticks de reloj.


## Experimento
Vamos a ejecutar diferentes casos en diferentes escenarios donde mediremos los datos de los procesos IO-bond y los procesos CPU-bond.
Las mediciones se realizarán (aproximadamente) cada 100 ticks de reloj, para cada proceso en ejecución durante el caso. 
Todos los casos en los distintos escenarios se ejecutan durante 5 minutos en un equipo con las siguientes caracteristicas: 
- INSERTAR EQUIPO UTILIZADO 
- Desconectado de internet
- Cantidad mínima de procesos en ejecución en el sistema, además de QEMU y otros procesos necesarios para realizar el experimento
En cada caso, las mediciones de cada proceso se promediaran para luego analizarse.


### Casos
- **Caso 0**: 1 iobench solo. En este caso queremos investigar como se comporta un solo proceso iobench corriendo solo (sin otros procesos en paralelo) en xv6.
- **Caso 1**: 1 cpubench solo. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo solo (sin otros procesos en paralelo) en xv6. 
- **Caso 2**: 1 iobench con 1 cpubench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además esta corriendo otro poceso cpubench en paralelo en xv6. (En este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corre 1 iobench)
- **Caso 3**: 1 iobench con 1 iobench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además esta corriendo otro poceso iobench en paralelo en xv6.
- **Caso 4**: 1 cpubench con 1 cpubench. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo cuando además esta corriendo otro pocesos cpubench en paralelo en xv6.
- **\*Caso 5**: 1 cpubench con 2 iobench. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo cuando además estan corriendo otros 2 pocesos iobench en paralelo en xv6. (Con este mismo Caso podemos ver como se comporta 1 iobench cuando en paralelo corren 1 iobench y otro cpubench)
- **\*Caso 6**: 1 iobench con 2 cpubench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además estan corriendo otros 2 pocesos cpubench en paralelo en xv6. (En este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corren 1 iobench y otro cpubench)
- **\*Caso 7**: 1 iobench con 2 cpubench y 1 iobench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además estan corriendo otros 2 pocesos cpubench y otro proceso iobench en paralelo en xv6. (Con este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corren 2 iobench y otro cpubench)


###  Escenarios
- **Escenario 0**: quantum por defecto
- **Escenario 1**: quantum 10 veces más corto
- **Escenario 2**: quantum 100 veces más corto
- **Escenario 3**: quantum 1000 veces más corto

