#!/usr/bin/env python3
"""Demo de validaciones sin conexion SMTP."""

# Importamos solo las funciones de validacion
import sys
import re

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

print("=" * 50)
print("DEMO - Validaciones SimpleTelnetMail")
print("=" * 50)

# Casos de prueba
test_cases = [
    ("Email valido", "test@example.com"),
    ("Email invalido", "notanemail"),
    ("Email con espacios", " test@example.com "),
]

for name, email in test_cases:
    valid = validate_email(email)
    print(f"{name}: {email} -> {'VALIDO' if valid else 'INVALIDO'}")

print("\n" + "=" * 50)
print("Destinatarios multiples:")
print("=" * 50)

recipients_tests = [
    (["user1@example.com", "user2@example.com"], "validos"),
    (["user@example.com", "user@example.com"], "duplicados"),
    (["valid@example.com", ""], "vacio"),
]

for recipients, desc in recipients_tests:
    is_valid, error, cleaned = validate_recipients(recipients)
    print(f"\n{desc.upper()}: {recipients}")
    if is_valid:
        print(f"  -> OK: {cleaned}")
    else:
        print(f"  -> ERROR: {error}")
