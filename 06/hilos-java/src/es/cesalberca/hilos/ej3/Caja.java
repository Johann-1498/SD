package es.cesalberca.hilos.ej3;

import java.util.concurrent.Semaphore;

/**
 * Created by Cesar
 */
@SuppressWarnings("ALL")
public class Caja {
    private int id;
    private Semaphore mutex;
    private int dineroEnCaja;

    public Caja(int id) {
        this.id = id;
        dineroEnCaja = 0;
        mutex = new Semaphore(1);
    }

    public void cobrarSiguienteCliente(Cliente proximoCliente) throws InterruptedException {
        mutex.acquire();
        Thread.sleep(1000);
        System.out.println(String.format("Bloqueando caja %d", this.id));
        dineroEnCaja += proximoCliente.pagar();
        System.out.println(String.format("Dinero en caja %d: %d", this.id, this.dineroEnCaja));
        System.out.println(String.format("Desbloqueando caja %d", this.id));
        ModernSuperMarket.removeCliente(proximoCliente);
        mutex.release();
    }

    public int getId() {
        return id;
    }

    public int getDineroEnCaja() {
        return dineroEnCaja;
    }

    @Override
    public String toString() {
        return "Caja{" +
                "id=" + id +
                ", dineroEnCaja=" + dineroEnCaja +
                '}';
    }
}
