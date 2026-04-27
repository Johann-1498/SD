package es.cesalberca.hilos.ej3;

public class Ej3Gestor {
    private int numeroCajas;
    private int numeroClientes;

    public Ej3Gestor(int numeroCajas, int numeroClientes) {
        this.numeroCajas = numeroCajas;
        this.numeroClientes = numeroClientes;
        ModernSuperMarket modernSuperMarket = new ModernSuperMarket(this.numeroCajas, this.numeroClientes);
    }

}
