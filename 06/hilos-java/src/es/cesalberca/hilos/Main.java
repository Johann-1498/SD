package es.cesalberca.hilos;

import es.cesalberca.hilos.ej1.Ej1Gestor;
import es.cesalberca.hilos.ej2.Ej2Gestor;
import es.cesalberca.hilos.ej3.Ej3Gestor;
import es.cesalberca.hilos.ej4.Ej4Gestor;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        int opcion;

        do {
            mostrarMenu();

            try {
                opcion = Integer.parseInt(sc.nextLine());
            } catch (NumberFormatException e) {
                System.out.println("Introduce un número");
                opcion = -1;
            }

            int relevos, numeroCajas, numeroClientes, numeroCoches, numeroPlazas;
            switch (opcion) {
                case 1:
                    System.out.println("Introduce el número de relevos");
                    relevos = Integer.parseInt(sc.nextLine());
                    new Ej1Gestor(relevos);
                    break;
                case 2:
                    System.out.println("Introduce el número de cajas");
                    numeroCajas = Integer.parseInt(sc.nextLine());
                    System.out.println("Introduce el número de clientes");
                    numeroClientes = Integer.parseInt(sc.nextLine());
                    new Ej2Gestor(numeroCajas, numeroClientes);
                    break;
                case 3:
                    System.out.println("Introduce el número de cajas");
                    numeroCajas = Integer.parseInt(sc.nextLine());
                    System.out.println("Introduce el número de clientes");
                    numeroClientes = Integer.parseInt(sc.nextLine());
                    new Ej3Gestor(numeroCajas, numeroClientes);
                    break;
                case 4:
                    System.out.println("Introduce el número de plazas");
                    numeroPlazas = Integer.parseInt(sc.nextLine());
                    System.out.println("Introduce el número de coches");
                    numeroCoches = Integer.parseInt(sc.nextLine());
                    new Ej4Gestor(numeroPlazas, numeroCoches);
                    break;
                case 0:
                    break;
                default:
                    System.out.println("Introduce una opción válida");
                    break;
            }
        } while (opcion != 0);
    }

    private static void mostrarMenu() {
        System.out.println("1. Ejercicio 1");
        System.out.println("2. Ejercicio 2");
        System.out.println("3. Ejercicio 3");
        System.out.println("4. Ejercicio 4");
        System.out.println("0. Salir");
    }
}
