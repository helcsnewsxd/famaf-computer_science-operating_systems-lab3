# Laboratorio número 3 de Sistemas Operativos 2022 - Grupo 12 | FaMAF UNC

## Integrantes del grupo:

- Lautaro Bachmann (lautaro.bachmann@mi.unc.edu.ar)
- Juan Bratti (juanbratti@mi.unc.edu.ar)
- Gonzalo Canavesio (gonzalo.canavesio@mi.unc.edu.ar)
- Emanuel Herrador (emanuel.nicolas.herrador@unc.edu.ar)


# Índice

[TOC]

# Introducción
En este laboratorio nos centramos en conocer el funcionamiento de xv6 con relación a la administración de los recursos usados por los procesos. Trabajamos sobre el algoritmo responsable del sistema de planificación (Round Robin), sus detalles de implementación en xv6 y su comportamiento ante exigencias de IO y/o CPU. Por último, implementamos un planificador de procesos nuevo inspirandonos en MLFQ. Para ello, agregamos prioridades a los procesos y, como punto extra, implementamos un priority boost.

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

## Parte 1

## Parte 2

## Parte 3

## Implementaciones en XV6
### Kernel
- **kernel/proc.c y kernel/proc.h:** 
- **kernel/param.h:** 
- **kernel/defs.h:**

# Herramientas de Programación
Las principales herramientas utilizadas por el grupo en la implementación y división del proyecto fueron las siguientes:

## *Material teórico de estudio y preparación*

 - [**Operating Systems: Three Easy Pieces**: Process virtualization](https://pages.cs.wisc.edu/~remzi/OSTEP/), principalmente el capítulo número 5 (*Process API*) y los capitulos de la sección de Concurrencia, sobre todo el capítulo número 31 (*Semaphores*), junto con las secciones de *Homework Simulation* y *Homework Code* de cada uno de esos capitulos.
 - [**Documentación de XV6**](https://course.ccs.neu.edu/cs3650/unix-xv6/index.html)
 - [**Repositorio XV6**](https://github.com/mit-pdos/xv6-book) 

### Conceptos teóricos utilizados

## *Desarrollo*

 - [Visual Studio Code](https://code.visualstudio.com/), editor de código

## *Compilación*

- [GNU Make](https://www.gnu.org/software/make/)

## *Debugging*

- [GDB](https://sourceware.org/gdb/), depurador estándar para el compilador GNU.

# Desarrollo del proyecto
Hicimos una división del trabajo centrándonos principalmente en las mediciones del cpubench e iobench, y por otro lado la implementación de MLFQ.

## Problemas

## *Comunicación*
La comunicación se basó fuertemente en plataformas como [Discord](https://discord.com/), donde la comunicación es más organizada y se pueden hacer llamadas de voz, y [Telegram](https://telegram.org/), donde conseguimos una comunicación más veloz e informal. 

## *Workflow de desarrollo*
### *Branches*
Nuestro workflow se apoyó fuertemente en el uso de branchs dentro del repositorio de bitbucket.

## *Pruebas utilizadas*


# Conclusiones
