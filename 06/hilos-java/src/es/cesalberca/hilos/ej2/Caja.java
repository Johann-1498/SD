package es.cesalberca.hilos.ej2;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.Semaphore;
import java.util.stream.Collectors;

/**
 * Created by Cesar
 */
public class Caja {
    private int id;
    private Semaphore mutex;
    private List<Cliente> clientesEnCola;
    private int dineroEnCaja;

    public Caja(int id) {
        this.id = id;
        dineroEnCaja = 0;
        mutex = new Semaphore(1);
        clientesEnCola = new ArrayList<>();
    }

    public void addClienteACola(Cliente cliente) throws InterruptedException {
        if (!clientesEnCola.contains(cliente)) {
            clientesEnCola.add(cliente);
        }
    }

    public void removeCliente(Cliente cliente) {
        if (clientesEnCola.contains(cliente)) {
            clientesEnCola.remove(cliente);
        }
    }

    public void cobrarSiguienteCliente() throws InterruptedException {
        mutex.acquire();
        System.out.println(String.format("Bloqueando caja %d", this.id));
        Optional<Cliente> proximoCliente = clientesEnCola.stream().findFirst();
        if (proximoCliente.isPresent()) {
            Cliente cliente = proximoCliente.get();
            dineroEnCaja += cliente.pagar();
            System.out.println(String.format("Dinero en caja %d: %d", this.id, this.dineroEnCaja));
        }
        System.out.println(String.format("Desbloqueando caja %d", this.id));
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
                ", clientesEnCola=" + this.clientesEnCola
                    .stream()
                    .map(Cliente::toString)
                    .collect(Collectors.joining(", ")) +
                ", dineroEnCaja=" + dineroEnCaja +
                '}';
    }
}
