# Problema
Comparar el desempeño de los planificadores Round Robin (por defecto en XV6) y MLFQ (implementado por nosotros), utilizando procesos CPU-bound e IO-bound en XV6 y contrastando también los diferentes tamaños de quantum en cada caso.

# Hipótesis
El planificador MLFQ mejorará el desempeño en los procesos IO-bound y empeorará un poquito el desempeño de los procesos CPU-bound.
En general en los casos, mientras menor sea el quantum, mejor desempeño tendrán los procesos IO-bound y peor desempeño los procesos CPU-bound. 

# Datos
Para responder a nuestras hipótesis, mediremos diferentes datos para los procesos IO-bound y los procesos CPU-bound.
Para los procesos IO-bound mediremos cuantas operaciones IO se realizaron (en promedio) durante un lapso de 100 (MINTICKS=100) ticks de reloj.
Para los procesos CPU-bound mediremos cuantas "1024 operaciones de punto flotante" (KFLOP) se realizaron (en promedio) durante un lapso de 100 (MINTICKS=100) ticks de reloj.

# Experimento
Vamos a ejecutar diferentes casos en diferentes escenarios donde mediremos los datos de los procesos IO-bound y los procesos CPU-bound.
Las mediciones se realizarán (aproximadamente) cada 100 (MINTICKS=100) ticks de reloj, para cada proceso en ejecución durante el caso. 
Todos los casos en los distintos escenarios se ejecutan durante 5 minutos en dos equipos, para analizar si se ve un mayor cambio en un procesador potente o en uno de menores recursos. Los equipos cuentan con las siguientes caracteristicas: 
- i5 12400f y 16GB de RAM / Celeron N4000 y 4GB de RAM
- Desconectado de internet
- Cantidad mínima de procesos en ejecución en el sistema, además de QEMU y otros procesos necesarios para realizar el experimento
En cada caso, las mediciones de cada proceso se promediaran para luego analizarse.


## Casos
- **Caso 0**: 1 iobench solo. En este caso queremos investigar como se comporta un solo proceso iobench corriendo solo (sin otros procesos en paralelo) en xv6.
- **Caso 1**: 1 cpubench solo. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo solo (sin otros procesos en paralelo) en xv6. 
- **Caso 2**: 1 iobench con 1 cpubench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además esta corriendo otro poceso cpubench en paralelo en xv6. (En este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corre 1 iobench)
- **Caso 3**: 1 iobench con 1 iobench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además esta corriendo otro poceso iobench en paralelo en xv6.
- **Caso 4**: 1 cpubench con 1 cpubench. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo cuando además esta corriendo otro pocesos cpubench en paralelo en xv6.
- **\*Caso 5**: 1 cpubench con 2 iobench. En este caso queremos investigar como se comporta un solo proceso cpubench corriendo cuando además estan corriendo otros 2 pocesos iobench en paralelo en xv6. (Con este mismo Caso podemos ver como se comporta 1 iobench cuando en paralelo corren 1 iobench y otro cpubench)
- **\*Caso 6**: 1 iobench con 2 cpubench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además estan corriendo otros 2 pocesos cpubench en paralelo en xv6. (En este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corren 1 iobench y otro cpubench)
- **\*Caso 7**: 1 iobench con 2 cpubench y 1 iobench. En este caso queremos investigar como se comporta un solo proceso iobench corriendo cuando además estan corriendo otros 2 pocesos cpubench y otro proceso iobench en paralelo en xv6. (Con este mismo Caso podemos ver como se comporta 1 cpubench cuando en paralelo corren 2 iobench y otro cpubench)

##  Escenarios
- **Escenario 0**: quantum por defecto 
- **Escenario 1**: quantum 10 veces más corto (Para mantener un comportamiento similar en las mediciones, el valor de MINTICKS es 10 veces más largo)
- **Escenario 2**: quantum 100 veces más corto (Para mantener un comportamiento similar en las mediciones, el valor de MINTICKS es 100 veces más largo)
- **Escenario 3**: quantum 1000 veces más corto (Para mantener un comportamiento similar en las mediciones, el valor de MINTICKS es 1000 veces más largo)

# Resultados RR (Planificador original) 

## Mediciones (i5 12400f)

### Caso 0: 1 iobench solo

| Escenario                    | 0 | 1 | 2 | 3 |
|------------------------------|---|---|---|---|
| Prom. de ops IO en intervalo |12740.13|13286.8|12572.03|4420.55|

### Caso 1: 1 cpubench solo

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 160742.0 | 14936.03 | 1408.37 | 7.21 |

### Caso 2: 1 iobench y 1 cpubench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 159644.43 | 14682.3 | 1058.24 | 10.81 |
| Prom. de ops IO en intervalo  | 32.93 | 332.85 | 3196.8 | 2049.13 |


### Caso 3: 1 iobench con 1 iobench

| Escenario                              | 0 | 1 | 2 | 3 |
|----------------------------------------|---|---|---|---|
| Prom. de ops IO (proc. A) en intervalo | 12554.33 | 10508.76 | 14064.62 | 4213.14 |
| Prom. de ops IO (proc. B) en intervalo | 12152.07 | 10511.2 | 14130.6 | 4443.95 |


### Caso 4: 1 cpubench con 1 cpubench

| Escenario                               | 0 | 1 | 2 | 3 |
|-----------------------------------------|---|---|---|---|
| Prom. de ops CPU (proc. A) en intervalo | 80132.63 | 7134.23 | 717.1 | 3.43 |
| Prom. de ops CPU (proc. B) en intervalo | 79991.46 | 7140.62 | 730.55 | 11.81 |

### Caso 5: 1 cpubench con 2 iobench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 159182.48 | 15067.7 | 1065.48 | 5.47 |
| Prom. de ops IO (proc. A) en intervalo  | 161.06 | 332.77 | 1711.52 | 3301.78 |
| Prom. de ops IO (proc. B) en intervalo  | - | - | 1648.3 | 3181.82 |

*La simbología "-" significa que no fueron registrados datos de ese proceso durante el periodo de tiempo que duro la medición (Nuestra hipótesis es que el proceso en cuestión sufrió de starvation por culpa de las llamadas a IO)

### Caso 6: 1 iobench con 2 cpubench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops IO en intervalo  | 16.0 | 165.96 | 1614.66 | 1722.74 |
| Prom. de ops CPU (proc. A) en intervalo | 79871.21 | 7100.93 | 537.7 | 6.0 |
| Prom. de ops CPU (proc. B) en intervalo | 79983.97 | 6859.53 | 723.14 | 4.0 |


### Caso 7: 1 iobench con 2 cpubench y 1 iobench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops IO (proc. A) en intervalo  | 84.25 | 168.92 | 854.86 | 2071.52 |
| Prom. de ops IO (proc. B) en intervalo  | - | - | 893.93 | 2094.13 |
| Prom. de ops CPU (proc. A) en intervalo | 79557.67 | 7728.93 | 718.34 | 5.0 |
| Prom. de ops CPU (proc. B) en intervalo | 79732.38 | 7929.59 | 534.17 | 4.0 |

*La simbología "-" significa que no fueron registrados datos de ese proceso durante el periodo de tiempo que duro la medición (Nuestra hipótesis es que el proceso en cuestión sufrió de starvation por culpa de las llamadas a IO)

# Resultados MLFQ sin priority boost (Planificador nuevo) 

## Mediciones (i5 12400f)

### Caso 0: 1 iobench solo

| Escenario                    | 0 | 1 | 2 | 3 |
|------------------------------|---|---|---|---|
| Prom. de ops IO en intervalo |12667.87|13643.03|12742.87|6036.53|

### Caso 1: 1 cpubench solo

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 160084.93 | 15790.43 | 1453.0 | 15.54 |

### Caso 2: 1 iobench y 1 cpubench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 159911.5 | 15790.43 | 1076.17 | 11.24 |
| Prom. de ops IO en intervalo  | 32.87 | 332.81 | 3207.28 | 2867.43 |


### Caso 3: 1 iobench con 1 iobench

| Escenario                              | 0 | 1 | 2 | 3 |
|----------------------------------------|---|---|---|---|
| Prom. de ops IO (proc. A) en intervalo | 12300.1 | 13078.93 | 13048.1 | 6183.55 |
| Prom. de ops IO (proc. B) en intervalo | 12346.1 | 13110.55 | 12964.03 | 6200.05 |


### Caso 4: 1 cpubench con 1 cpubench

| Escenario                               | 0 | 1 | 2 | 3 |
|-----------------------------------------|---|---|---|---|
| Prom. de ops CPU (proc. A) en intervalo | 80053.03 | 7921.87 | 724.37 | 7.5 |
| Prom. de ops CPU (proc. B) en intervalo | 80024.5 | 7916.45 | 725.28 | 7.68 |

### Caso 5: 1 cpubench con 2 iobench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops CPU en intervalo | 159573.4 | 15365.67 | 1068.07 | 9.0 |
| Prom. de ops IO (proc. A) en intervalo  | 32.8 | 334.85 | 1741.19 | 3330.36 |
| Prom. de ops IO (proc. B) en intervalo  | - | - | 1787.36 | 3336.71 |

*La simbología "-" significa que no fueron registrados datos de ese proceso durante el periodo de tiempo que duro la medición (Nuestra hipótesis es que el proceso en cuestión sufrió de starvation por culpa de las llamadas a IO)

### Caso 6: 1 iobench con 2 cpubench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops IO en intervalo  | 32.93 | 331.62 | 2500.34 | 1868.0 |
| Prom. de ops CPU (proc. A) en intervalo | 80268.57 | 7725.07 | 579.79 | 4.9 |
| Prom. de ops CPU (proc. B) en intervalo | 79994.52 | 7731.73 | 576.89 | 4.11 |


### Caso 7: 1 iobench con 2 cpubench y 1 iobench

| Escenario                     | 0 | 1 | 2 | 3 |
|-------------------------------|---|---|---|---|
| Prom. de ops IO (proc. A) en intervalo  | 59.6 | 332.42 | 1732.08 | 2242.09 |
| Prom. de ops IO (proc. B) en intervalo  | - | - | 1620.93 | 2260.5 |
| Prom. de ops CPU (proc. A) en intervalo | 79718.9 | 7731.73 | 542.76 | 4.53 |
| Prom. de ops CPU (proc. B) en intervalo | 79867.9 | 7710.17 | 544.24 | 4.0 |

*La simbología "-" significa que no fueron registrados datos de ese proceso durante el periodo de tiempo que duro la medición (Nuestra hipótesis es que el proceso en cuestión sufrió de starvation por culpa de las llamadas a IO)

## Conclusiones y gráficos de interes

![](graphs/iobench-i512400f-RR.png)
![](graphs/iobench-i512400f-MLFQ.png)
![](graphs/cpubench-i512400f-RR.png)
![](graphs/cpubench-i512400f-MLFQ.png)

### Diferentes tamaños de quantums

- En el **caso 0** se observa que el mejor escenario para los proceso IO-bond es el **escenario 1**, teniendo resultados ligeramente mejores que los de los **escenarios 0 y 2**. El **escenario 3** da el peor desempeño, debido a lo corto de su quantum, que lo vuelve inviable.

- En el **caso 1** se observa que se cumplió la hipótesis de que menor quantum implica peor desempeño para los procesos CPU-bond, esto porque mientras más largo el quantum, menor cantidad de tiempo se lo pasa el SO haciendo context switch.

- En todos los casos, aunque se ve en particular reflejado en el **caso 0 y 1**, el **escenario 3** dio un desempeño lamentable, adectando sobre todo a los procesos CPU-bond al punto de volverlos inutilizables, pero tampoco ayudando demasiado a los procesos IO-bond. Esto puede deberse a que al implementar un quantum tan pequeño, el SO gasta más tiempo realizando los context switch que realmente ejecutando procesos.

- En el **caso 2**, al ejecutar en paralelo un proceso IO-bound y CPU-bound, ambos procesos bajan su desempeño como es de esperar. Los quantums más grandes (**escenario 0 y 1**) hacen que el proceso CPU-bound tenga una disminución de desempeño mínima, pero el proceso IO-bound pierde muchisimo desempeño, y los quantums más pequeños (**escenario 2 y 3**) implica mayor equilibrio en la baja de desempeño de cada proceso (Es decir, ambos procesos disminuyen su desempeño en un porcentaje similar comparando con las mediciones de los **casos 1 y 2**)

- En los casos donde se ejecutan procesos IO-bond junto con CPU-bond (**casos 2,5,6 y7**), el escenario más beneficioso para los procesos IO-bond es generalmente el **escenario 3**, y el más beneficioso para los procesos CPU-bond es generalmente el **escenario 1**, apoyando la hipótesis dicha anteriormente. Sin embargo, varia un poco entre el planificador RR y MLFQ y no es absoluto, ya que en algunos casos el **escenario 2** es más beneficioso que el **escenario 3** para los procesos IO-bond.

- Todas las conclusiones anteriores aplican tanto para el planificador RR como para el MLFQ sin priority boost, ya que los resultados entre ambos planificadores no tienen grandes variaciones.


### Desempeño de los procesos al realizar time-sharing

- El funcionamiento del **caso 2** ya fue explicado en la sección anterior

- En el **caso 3** se observa que al ejecutar 2 procesos IO-bond en paralelo, el desempeño de cada proceso es similar a si cada proceso se ejecutara solo en el CPU. Esto se debe a que al hacer las peticiones de IO se van turnando los procesos, y el tiempo que un proceso espera el otro lo aprovecha para realizar cosas en el CPU.

- En el **caso 4** se observa que al ejecutar 2 procesos CPU-bound en paralelo, el desempeño de cada proceso baja a la mitad (Respecto al desempeño al ejecutarse solo, en el **caso 1**).


- En el **caso 5** se observa que al ejecutar un proceso CPU-bound en paralelo con 2 procesos IO-bound, el desempeño del proceso CPU-bound es similar a que si se ejecutara con un solo proceso IO-bound en paralelo. Los procesos IO-bound tienen problemas para ejecutarse en simultaneo junto con el proceso CPU-bound, y creemos que uno de los 2 procesos sufre starvation en los **escenarios 0 y 1**. Una vez ambos procesos IO-bond nos devuelven mediciones con las cuales poder trabajar, se observa que el desempeño de cada proceso IO-bond es la mitad del desempeño que tendría si se ejecutará un proceso CPU-bond en paralelo con un solo proceso IO-bond (**caso 2**). Esto se debe a que, a comparación del **caso 3**, acá los tiempos de espera de IO los aprovecha sobre todo el proceso CPU-bond y una vez obtiene el control del CPU no lo suelta hasta finalizar su quantum (En el **caso 2**, los procesos al ser ambos IO-bond iban soltando el control del CPU de manera alternada y nadie "acaparaba" el uso del CPU).

- En el **caso 6**: Al ejecutar un proceso IO-bound en paralelo con 2 procesos CPU-bound, el desempeño del proceso IO-bound es similar a que si se ejecutara en paralelo con 1 solo proceso CPU-bound (**caso 2**). Los procesos CPU-bound tienen un desempeño similar a cuando se ejecutan en paralelo pero sin el proceso IO-bound (**caso 4**).

- **Caso 7**: Al ejecutar 2 procesos IO-bound en paralelo con 2 procesos CPU-bound, los 2 procesos CPU-bound tienen un desempeño similar a cuando se ejecutan en paralelo pero sin los procesos IO-bound (**caso 4**). Los procesos IO-bound tienen menor desempeño que si solo se ejecutara un proceso IO-bound (**caso 6**).

- Para los análisis anteriores se usaron sobre todo los **escenarios 0, 1 y 2**, ya que el **escenario 3** al tener un quantum tan pequeño genera ciertas mediciones extrañas, además de que no consideramos que sea viable querer utilizar XV6 con un planificador que tenga el quantum así de pequeño.

### Comparación MLFQ vs RR
- En los casos básicos (**casos 0, 1, 2, 3 y 4**) no se ve gran diferencia entre los resultados de los planificadores MLFQ y RR.
- En los casos opcionales (**casos 5, 6 y 7**) si se ve una mayor diferencia, aunque tampoco es muy grande. En esos casos opcionales se ve que los procesos IO-bond tienen una mejor respuesta y desempeño sin que los procesos CPU-bond se vean muy perjudicados, mostrando que el SO los ejecuta mayor cantidad de veces, priorizandolos frente a los procesos CPU-bond y generando un contraste con el planificador RR.


# Resumen de los resultados
- 