package es.cesalberca.hilos.ej3;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Collectors;

@SuppressWarnings("ALL")
public class ModernSuperMarket {
    private static Thread[] clientes;
    private static Caja[] cajas;

    private static List<Cliente> colaClientes;

    private static int numeroCajas;
    private static int numeroClientes;

    public ModernSuperMarket(int numeroCajas, int numeroClientes) {
        ModernSuperMarket.numeroCajas = numeroCajas;
        ModernSuperMarket.numeroClientes = numeroClientes;

        clientes = new Thread[ModernSuperMarket.numeroClientes];
        cajas = new Caja[ModernSuperMarket.numeroCajas];
        colaClientes = new ArrayList<>();

        iniciarCajas();
        iniciarClientes();
        finalizarPrograma();
    }

    private void iniciarCajas() {
        for (int i = 0; i < cajas.length; i++) {
            cajas[i] = new Caja(i);
        }
    }

    private void iniciarClientes() {
        System.out.println("Iniciando clientes...");
        Cliente cliente;
        Thread t;
        for (int i = 0; i < ModernSuperMarket.numeroClientes; i++) {
            cliente = new Cliente(i);
            t = new Thread(cliente);
            clientes[i] = t;
            t.start();
        }
    }

    public static void agregarClienteACola(Cliente cliente) {
        try {
            addClienteACola(cliente);
            System.out.println("Cola actual: " + colaClientes
                    .stream()
                    .map(Cliente::toString)
                    .collect(Collectors.joining(", ")));

            Caja cajaElegida = cajas[ThreadLocalRandom.current().nextInt(numeroCajas)];
            cajaElegida.cobrarSiguienteCliente(cliente);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public static void addClienteACola(Cliente cliente) {
        if (!colaClientes.contains(cliente)) {
            colaClientes.add(cliente);
        }
    }

    public static void removeCliente(Cliente cliente) {
        if (colaClientes.contains(cliente)) {
            colaClientes.remove(cliente);
        }
    }

    private void finalizarPrograma() {
        for (Thread cliente : clientes) {
            try {
                cliente.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println("Programa finalizado");

        for (Caja caja : cajas) {
            System.out.println(caja);
        }

        System.out.println(String.format("Total ganado: %d", Arrays.stream(cajas)
                .mapToInt(Caja::getDineroEnCaja)
                .reduce(0, Integer::sum)));
    }
}
