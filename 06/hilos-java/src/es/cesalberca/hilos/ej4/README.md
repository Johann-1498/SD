# EJERCICIO 4

Escribe una clase llamada Parking que reciba el número de plazas del parking y el número de coches existentes en el sistema. 

Se deben crear tantos hilos como coches haya. El parking dispondrá de una única entrada y una única salida. 

En la entrada de vehículos habrá un dispositivo de control que permita o impida el acceso de los mismos al parking, dependiendo del estado actual del mismo (plazas de aparcamiento disponibles). 

Los tiempos de espera de los vehículos dentro del parking son aleatorios. En el momento en el que un vehículo sale del parking, notifica al dispositivo de control el número de la plaza que tenía asignada y se libera la plaza que estuviera ocupando, quedando así estas nuevamente disponibles. 

Un vehículo que ha salido del parking esperará un tiempo aleatorio para volver a entrar nuevamente en el mismo. Por tanto, los vehículos estarán entrando y saliendo indefinidamente del parking.
 
Es importante que se diseñe el programa de tal forma que se asegure que, antes o después, un vehículo que permanece esperando a la entrada del parking entrará en el mismo (no se produzca inanición).