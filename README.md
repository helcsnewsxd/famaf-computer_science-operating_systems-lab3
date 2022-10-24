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
Todos los casos en los distintos escenarios se ejecutan durante 5 minutos en un equipo con las siguientes caracteristicas: 
- INSERTAR EQUIPO UTILIZADO 
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

## Conclusiones RR y gráficos de interes
- **Caso 0 y 1**: Se cumplió la hipótesis de que menor quantum implica mejor desempeño para procesos IO-bound y peor desempeño para procesos CPU-bound (**escenarios 0, 1 y 2**). En el **escenario 3** ambos tipos de proceso tuvieron un peor desempeño que en el caso anterior. Esto puede deberse a que al implementar un quantum tan pequeño, el SO gasta más tiempo realizando los context switch que realmente ejecutando procesos.
- **Caso 2**: Al ejecutar en paralelo un proceso IO-bound y CPU-bound, ambos procesos bajan su desempeño. Con los escenarios se ve que un mayor quantum hace que el proceso CPU-bound tenga una disminución de desempeño mínima en este caso, pero el proceso IO-bound pierde muchisimo desempeño, y un quantum más pequeño implica mayor equilibrio en la baja de desempeño de cada proceso (Es decir, ambos procesos disminuyen su desempeño de manera similar, comparando con las mediciones de los **casos 1 y 2**)

- En el **caso 3** de las mediciones de RR se observa que

- **Caso 4**: Al ejecutar 2 procesos CPU-bound en paralelo, el desempeño de cada proceso baja a la mitad (Respecto al desempeño al ejecutarse solo, en el **caso 1**) y esto se mantiene en todos los escenarios excepto el **escenario 3**, donde el quantum pequeño puede ser que propicie un funcionamiento extraño del planificador.
- **Caso 5**: Al ejecutar un proceso CPU-bound en paralelo con 2 procesos IO-bound, el desempeño del proceso CPU-bound es similar a que si se ejecutara con un solo proceso IO-bound en paralelo. Los procesos IO-bound tienen problemas para ejecutarse en simultaneo junto con el proceso CPU-bound, y creemos que uno de los 2 procesos sufre starvation en los **escenarios 0 y 1**.
- **Caso 6**: Al ejecutar un proceso IO-bound en paralelo con 2 procesos CPU-bound, el desempeño del proceso IO-bound es aproximadamente la mitad que si se ejecutara en paralelo con 1 solo proceso CPU-bound (**caso 2**). Los procesos CPU-bound tienen un desempeño similar a cuando se ejecutan en paralelo pero sin el proceso IO-bound (**caso 4**).
- **Caso 7**: Al ejecutar 2 procesos IO-bound en paralelo con 2 procesos CPU-bound, los 2 procesos CPU-bound tienen un desempeño similar a cuando se ejecutan en paralelo pero sin los procesos IO-bound (**caso 4**). Los procesos IO-bound tienen la mitad de desempeño que si solo se ejecutará un proceso IO-bound (**caso 6**).







