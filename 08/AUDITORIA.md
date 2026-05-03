# Auditoría de Comunicación en Red - Sockets

## 1. Funcionalidad Original

### echo-server.py / echo-client.py
Servidor eco simple TCP:
- Servidor escucha en `127.0.0.1:65432`
- Un solo cliente conectado
- Recibe datos y los reenvía (eco)
- Modo bloqueante

### multiconn-server.py / multiconn-client.py
Servidor multi-conexión con selectores:
- Múltiples clientes simultáneos
- `selectors.DefaultSelector()` para I/O no-bloqueante
- Cada cliente independiente con `connid`
- Buffer `outb` para datos pendientes

## 2. Estrategia de Auditoría Aplicada

### 2.1 Logging de Conexiones
- Registro timestamp de cada conexión/desconexión
- Captura de `(host, port)` del cliente
- Asignación de ID único por conexión

### 2.2 Auditoría de Mensajes
- Timestamp de cada mensaje enviado/recibido
- Formato `[username]: mensaje` trazable
- Log en archivo `audit.log` rotativo
- Bytes transferidos por conexión

### 2.3 Seguridad Implementada
- Validación de nombre usuario (sin caracteres especiales)
- Límite de longitud mensaje (prevenir DoS)
- Rate limiting por cliente
- Cifrado opcional TLS

## 3. Mejoras Implementadas

### Servidor (chat-server.py)
- Broadcast a todos los clientes conectados
- Gestión de usernames dinámicos
- Thread-safe logging
- Auditoría completa

### Cliente (chat-client.py)
- Envío username al conectar
- Interfaz interactiva
- Manejo desconexión graceful
- Reconexión automática

## 4. Conclusiones

### 4.1 Patrones Observados
- **Selectores**: Superior para multi-conexión vs threads
- **Non-blocking**: Escalabilidad mayor
- **Namespace**: `types.SimpleNamespace` limpia para data por conexión

### 4.2 Seguridad
- Auditoría es crítica para trazabilidad
- Logs deben protegerse (permisos restringidos)
- TLS recomendado para producción

### 4.3 Trade-offs
- Simple vs funcional: echo-server es demo, chat-server es real
- Sync vs async: selectores median, async.io grande escala
- Memoria vs CPU: buffering aumenta throughput
