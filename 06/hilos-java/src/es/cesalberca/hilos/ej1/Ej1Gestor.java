package es.cesalberca.hilos.ej1;

import java.util.ArrayList;

/**
 * Created by Cesar
 */
public class Ej1Gestor {
    public Ej1Gestor(int numeroHilos) {
        ArrayList<Thread> relevos = new ArrayList<>();
        Relevo relevo = new Relevo();

        // Añadimos al arraylist los hilos
        for (int i = 0; i < numeroHilos; i++) {
            relevos.add(new Thread(relevo, String.valueOf(i)));
        }

        System.out.println("Comenzando carrera...");

        // Por cada hilo comenzamos la ejecución y hacemos un join para determinar el orden de ejecución de hilos.
        for (Thread hilo : relevos) {
            try {
                hilo.start();
                hilo.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        System.out.println("Carrera terminada");
    }
}
