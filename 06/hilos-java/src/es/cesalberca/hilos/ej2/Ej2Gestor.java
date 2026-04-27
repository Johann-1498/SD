package es.cesalberca.hilos.ej2;

/**
 * Created by Cesar
 */
public class Ej2Gestor {
    private int numeroCajas;
    private int numeroClientes;

    public Ej2Gestor(int numeroCajas, int numeroClientes) {
        this.numeroCajas = numeroCajas;
        this.numeroClientes = numeroClientes;
        SuperMarket superMarket = new SuperMarket(this.numeroCajas, this.numeroClientes);
    }

}
