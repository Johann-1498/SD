# EJERCICIO 1

Escribe una clase llamada Relevos que simule una carrera de relevo de la siguiente forma:

Cree 4 hilos, que se quedarán a la espera de recibir alguna señal para comenzar a correr.

Una vez creados los hilos, se indicará que comience la carrera, con lo que uno de los hilos deberá empezar a correr. Este primer hilo será lógicamente el primer corredor.

Cuando un hilo termina de correr, pone algún mensaje en pantalla y espera un par de segundos, pasando el testigo a otro de los hilos para que comience a correr, y terminando su ejecución (la suya propia), debería poner otro mensaje.

Cuando el último hilo termine de correr, el programa padre mostrará un mensaje indicando que todos los hijos han terminado.