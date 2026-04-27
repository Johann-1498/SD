package es.cesalberca.hilos.ej3;

import java.util.concurrent.ThreadLocalRandom;

/**
 * Created by César
 */
@SuppressWarnings("ALL")
public class Cliente implements Runnable {
    private static int MAX_ITERACIONES = 1;
    private int id;

    public Cliente(int id) {
        this.id = id;
    }

    @Override
    public void run() {
        int iteracionActual = 0;
        while (iteracionActual < MAX_ITERACIONES) {
            try {
                System.out.println(String.format("Cliente %d buscando en el supermercado productos", this.id));
                Thread.sleep(ThreadLocalRandom.current().nextInt(1000,2000));
                irACola();
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                iteracionActual++;
            }
        }
    }

    public int pagar() {
        System.out.println(String.format("Cliente %d está pagando su compra", this.id));
        return ThreadLocalRandom.current().nextInt(5,20);
    }

    private void irACola() {
        System.out.println(String.format("Cliente %d ha hecho su compra, yendo a la cola común", this.id));
        ModernSuperMarket.agregarClienteACola(this);
    }

    public int getId() {
        return id;
    }

    @Override
    public String toString() {
        return "Cliente{" +
                "id=" + id +
                '}';
    }
}
