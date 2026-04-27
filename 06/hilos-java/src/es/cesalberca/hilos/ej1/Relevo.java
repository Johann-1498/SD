package es.cesalberca.hilos.ej1;

import java.util.Date;

public class Relevo implements Runnable {
    public synchronized void correr() {
        Thread hilo = Thread.currentThread();
        System.out.println("Relevo llevado por hilo: " + hilo.getName() + " | " + new Date());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println(String.format("Relevo %s finalizado ", hilo.getName()));
    }

    @Override
    public void run() {
        this.correr();
    }
}