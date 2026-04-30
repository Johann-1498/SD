#!/usr/bin/env python3
"""
DEMO INTERACTIVO - SimpleTelnetMail con Validaciones de Seguridad
Para capturas de pantalla sin conexion SMTP real.
"""

import sys
import re
from datetime import datetime

# Email regex
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    return EMAIL_PATTERN.match(email.strip()) is not None

def validate_recipients(recipients):
    if not recipients:
        return False, "Error: La lista de destinatarios esta vacia.", []
    if isinstance(recipients, str):
        recipients = [recipients]
    cleaned = []
    seen = set()
    for recipient in recipients:
        if not recipient or not recipient.strip():
            return False, "Error: Se detecto un destinatario vacio.", []
        recipient = recipient.strip()
        if recipient in seen:
            return False, f"Error: Destinatario duplicado detectado: {recipient}", []
        if not validate_email(recipient):
            return False, f"Error: Formato de email invalido: {recipient}", []
        seen.add(recipient)
        cleaned.append(recipient)
    return True, None, cleaned

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_test(test_num, description):
    print(f"\n{'-' * 70}")
    print(f"TEST {test_num}: {description}")
    print('-' * 70)

def main():
    print_header("SIMPLETELNETMAIL - DEMO VALIDACIONES DE SEGURIDAD")
    print("Version: 0.1.2 (con mejoras de seguridad)")
    print("Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # TEST 1: Email invalido en remitente
    print_test(1, "Validacion de formato de email - Remitente invalido")
    print("\nComando: python -m SimpleTelnetMail -H 'smtp.gmail.com' \\")
    print("         -f 'email_invalido' -t 'destino@example.com' -m 'Mensaje'")
    print("\n>> Ejecutando...")

    from_ = "email_invalido"
    if not validate_email(from_):
        print(f"\n[X] ERROR: Formato de email invalido en 'from': {from_}")
        print("    El email debe contener @ y un dominio valido.")
        input("\n[PRESIONA ENTER para continuar...]")

    # TEST 2: Destinatario duplicado
    print_test(2, "Deteccion de destinatarios duplicados")
    print("\nComando: SimpleTelnetMail -H 'smtp.gmail.com' \\")
    print("         -f 'remitente@example.com' \\")
    print("         -t 'user@example.com,user@example.com' \\")
    print("         -m 'Mensaje duplicado'")
    print("\n>> Ejecutando...")

    to = ["user@example.com", "user@example.com"]
    is_valid, error, cleaned = validate_recipients(to)
    if not is_valid:
        print(f"\n[X] {error}")
        input("\n[PRESIONA ENTER para continuar...]")

    # TEST 3: Destinatario vacio
    print_test(3, "Deteccion de destinatario vacio")
    print("\nComando: SimpleTelnetMail -H 'smtp.gmail.com' \\")
    print("         -f 'remitente@example.com' \\")
    print("         -t 'user1@example.com,,user2@example.com' \\")
    print("         -m 'Mensaje con vacio'")
    print("\n>> Ejecutando...")

    to = ["user1@example.com", "", "user2@example.com"]
    is_valid, error, cleaned = validate_recipients(to)
    if not is_valid:
        print(f"\n[X] {error}")
        input("\n[PRESIONA ENTER para continuar...]")

    # TEST 4: Host faltante
    print_test(4, "Validacion de campo obligatorio - Host faltante")
    print("\nComando: SimpleTelnetMail -f 'remitente@example.com' \\")
    print("         -t 'destino@example.com' -m 'Mensaje'")
    print("\n>> Ejecutando...")

    host = ""
    if not host or not host.strip():
        print("\n[X] ERROR: El servidor SMTP (host) es obligatorio.")
        print("    Debe especificar el host con -H o --host")
        input("\n[PRESIONA ENTER para continuar...]")

    # TEST 5: Username invalido
    print_test(5, "Validacion de formato de username")
    print("\nComando: SimpleTelnetMail -H 'smtp.gmail.com' \\")
    print("         -f 'remitente@example.com' \\")
    print("         -t 'destino@example.com' -m 'Mensaje' \\")
    print("         -U 'username_sin_arroba'")
    print("\n>> Ejecutando...")

    username = "username_sin_arroba"
    if username and not validate_email(username):
        print(f"\n[X] ERROR: Formato de username invalido: {username}")
        input("\n[PRESIONA ENTER para continuar...]")

    # TEST 6: Caso EXITOSO
    print_test(6, "ENVIO EXITOSO - Todos los campos validos")
    print("\nComando: SimpleTelnetMail -H 'smtp.gmail.com' -p 587 -s \\")
    print("         -f 'remitente@example.com' \\")
    print("         -t 'destino1@example.com,destino2@example.com' \\")
    print("         -m 'Este es un mensaje de prueba' \\")
    print("         -U 'remitente@example.com' -W 'password123' -d 4")
    print("\n>> Ejecutando...")

    print("\n[*] Validando host... smtp.gmail.com:587 [OK]")
    print("[*] Validando remitente... remitente@example.com [OK]")
    print("[*] Validando destinatarios...")
    to = ["destino1@example.com", "destino2@example.com"]
    is_valid, error, cleaned = validate_recipients(to)
    if is_valid:
        for recipient in cleaned:
            print(f"    - {recipient} [OK]")
    print("[*] Validando username... remitente@example.com [OK]")
    print("[*] Validando mensaje... [OK]")
    print("\n[*] Conectando a smtp.gmail.com:587...")
    print("[*] Iniciando TLS/SSL...")
    print("[*] Autenticando como remitente@example.com...")
    print("[*] Enviando email...")

    print("\n[+] CORREO ENVIADO EXITOSAMENTE!")
    print(f"[+] Estado: SUCCESS")
    print(f"[+] Destinatarios: {', '.join(cleaned)}")
    print(f"[+] Log guardado en: simple_telnet_mail.log")

    # Mostrar contenido del log simulado
    print("\n" + "-" * 70)
    print("Contenido del log (simple_telnet_mail.log):")
    print("-" * 70)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - INFO - INICIO - Servidor: smtp.gmail.com:587, Remitente: remitente@example.com, Destinatarios: destino1@example.com, destino2@example.com")
    print(f"{timestamp} - INFO - EXITO - Correo enviado a destino1@example.com, destino2@example.com")
    print("-" * 70)

    print_header("FIN DE LA DEMO")
    print("\nResumen de validaciones implementadas:")
    print("  [OK] Formato de email (remitente, destinatarios, username)")
    print("  [OK] Deteccion de destinatarios duplicados")
    print("  [OK] Deteccion de destinatarios vacios")
    print("  [OK] Validacion de campos obligatorios (host, from, to, message)")
    print("  [OK] Sistema de logging en simple_telnet_mail.log")
    print("\n")

if __name__ == "__main__":
    main()
