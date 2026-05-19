# Informe tecnico - Library Simulator

## 1) Revision del documento y codigo: funcionalidad de la aplicacion

La aplicacion es un simulador visual de concurrencia en una biblioteca usando **JavaFX + Threads + Semaforos**.

Funcionalidad principal:
- Permite crear lectores de dos tipos: **Student** y **Professor**.
- Cada lector solicita un libro (A..Z) y recorre un ciclo de vida animado:
  entrada -> cola inicial -> zona de importacion del libro -> espera/silla -> mesa de lectura -> devolucion -> salida.
- Controla recursos limitados con semaforos:
  - cola de entrada (4 posiciones)
  - importacion (5 posiciones)
  - sillas de espera (3)
  - mesa de lectura (12)
  - devolucion (2)
  - cadena de salida (exclusion en tramo critico)
- Controla disponibilidad de libros (1 copia por libro por defecto) y sincroniza acceso por libro.

Archivos clave:
- `src/com/librarysimulator/Application/Main.java`: GUI, inicializacion de semaforos y recursos, botones de creacion de hilos.
- `src/com/librarysimulator/Models/Student.java`: ciclo de vida y reglas de sincronizacion para estudiante.
- `src/com/librarysimulator/Models/Professor.java`: ciclo de vida y reglas de sincronizacion para profesor.
- `src/com/librarysimulator/Providers/*.java`: datos estaticos (libros, coordenadas, imagenes).
- `src/com/librarysimulator/Utilities/ImagesUtilities.java`: construccion de ImageView.

## 2) Implementar, ejecutar y probar: resultados

### Cambios implementados
Se agrego un algoritmo faltante de planificacion justa (FIFO en semaforos):
- Se actualizaron los semaforos a modo **fair** (`new Semaphore(permisos, true)`) en `Main.java`.
- Esto aplica cola FIFO a la asignacion de permisos y reduce el riesgo de inanicion por adelantamientos repetidos.

Adicional:
- Se elimino import no usado/invalido en `CoordinatesProvider.java`:
  - `com.mysql.fabric.xmlrpc.base.Array`

### Ejecucion y prueba realizadas en este entorno
Comandos ejecutados:
1. `java -version` -> Java 25 LTS detectado.
2. `javac -version` -> javac 25 detectado.
3. Compilacion de fuentes con `javac`.

Resultado real observado:
- **La compilacion falla en este entorno** porque **JavaFX no esta instalado/configurado** en classpath/module-path.
- Error dominante: `package javafx.* does not exist`.

Conclusion de prueba:
- El codigo fuente es consistente con una app JavaFX, pero requiere dependencias de JavaFX para compilar/ejecutar fuera de IntelliJ configurado.

## 3) Algoritmos simulados y descripcion

1. **Exclusion mutua con semaforos binarios**
- Protege secciones criticas (mapas de disponibilidad, contadores, etiquetas y tramos de movimiento).

2. **Semaforos contadores para recursos finitos**
- Modela capacidad de zonas: mesa (12), espera (3), importacion (5), retorno (2), cola (4).

3. **Productor/consumidor de recursos por libro**
- Cada libro actua como recurso con capacidad limitada (`NUMBER_OF_BOOKS=1`).
- Un lector adquiere y luego libera el libro al finalizar.

4. **Prioridad por clase de lector (Professor sobre Student)**
- Con mapas de contadores y semaforo de prioridad por libro, se fuerza preferencia de profesor cuando corresponde.

5. **Planificacion por disponibilidad espacial (asignacion de primer hueco libre)**
- Uso de hash maps de posiciones para reservar/liberar coordenadas en importacion, mesa, espera y retorno.

6. **(Agregado) FIFO/Fair Semaphore Scheduling**
- Semaforos inicializados con `fair=true` para atender en orden de llegada y mejorar justicia.

## 4) Algoritmo faltante agregado

Se agrego: **FIFO fairness en semaforos**.

Impacto esperado:
- Menos adelantamientos entre hilos bajo alta contencion.
- Comportamiento mas determinista en orden de acceso a recursos.
- Menor probabilidad de inanicion por competencia reiterada.

Nota:
- La prioridad de profesor sigue existiendo por logica de negocio del simulador; el fairness mejora equidad dentro de cada cola/semaforo.

## Paso a paso para ejecutar la aplicacion y probarla

### Opcion A (recomendada): IntelliJ IDEA
1. Instalar JDK (17+ recomendado; 25 tambien funciona).
2. Descargar JavaFX SDK compatible con tu JDK (por ejemplo OpenJFX 25).
3. Abrir el proyecto en IntelliJ.
4. Ir a **File > Project Structure > Libraries** y agregar la carpeta `lib` del JavaFX SDK.
5. Crear/editar configuracion de ejecucion de `Main` (`com.librarysimulator.Application.Main`).
6. En **VM options**, agregar:
   ```
   --module-path "C:\ruta\a\javafx-sdk\lib" --add-modules javafx.controls,javafx.fxml,javafx.graphics
   ```
7. Ejecutar `Main`.
8. Pruebas funcionales sugeridas:
   - Caso 1: clic en **Add Student** y verificar recorrido completo.
   - Caso 2: clic en **Add Professor** y verificar recorrido completo.
   - Caso 3: usar **Add Randomly** para estres de concurrencia.
   - Caso 4: marcar checkbox y usar mismo libro para varios lectores; observar bloqueos/desbloqueos.
   - Caso 5: provocar saturacion (muchos lectores) y observar que no se superen capacidades de zonas.

### Opcion B: Terminal (manual)
1. Definir variable `JAVAFX_LIB` con la ruta a `javafx-sdk\lib`.
2. Compilar:
   ```powershell
   javac --module-path "$env:JAVAFX_LIB" --add-modules javafx.controls,javafx.fxml,javafx.graphics -d build\classes (Get-ChildItem -Recurse -Filter *.java | ForEach-Object { $_.FullName })
   ```
3. Copiar recursos `src\res` a `build\classes\res`.
4. Ejecutar:
   ```powershell
   java --module-path "$env:JAVAFX_LIB" --add-modules javafx.controls,javafx.fxml,javafx.graphics -cp build\classes com.librarysimulator.Application.Main
   ```

## Resultado esperado al probar
- Se abre una ventana "Library Simulator".
- Los botones generan hilos animados de estudiantes/profesores.
- Se observan esperas cuando recursos estan llenos.
- Se observa devolucion/salida al terminar lectura.
- Bajo carga, con semaforos justos, la atencion sigue un patron mas ordenado por llegada.
