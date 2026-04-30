#!/usr/bin/env python3
"""Test security validations without SMTP connection."""

import sys
import re

# Email regex pattern (same as in SimpleTelnetMail.py)
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False
    return EMAIL_PATTERN.match(email.strip()) is not None

def validate_recipients(recipients):
    """Validate recipients list."""
    if not recipients:
        return False, "Error: La lista de destinatarios está vacía.", []

    if isinstance(recipients, str):
        recipients = [recipients]

    cleaned = []
    seen = set()

    for recipient in recipients:
        if not recipient or not recipient.strip():
            return False, "Error: Se detectó un destinatario vacío.", []

        recipient = recipient.strip()

        if recipient in seen:
            return False, f"Error: Destinatario duplicado detectado: {recipient}", []

        if not validate_email(recipient):
            return False, f"Error: Formato de email inválido: {recipient}", []

        seen.add(recipient)
        cleaned.append(recipient)

    return True, None, cleaned

def run_test(test_name, test_func):
    """Run a test and print result."""
    print("=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)
    try:
        test_func()
    except AssertionError as e:
        print(f"[X] FAIL: {e}\n")
        return False
    print("[OK] PASS\n")
    return True

def test_valid_email():
    """Test valid email format."""
    assert validate_email("test@example.com"), "Email válido rechazado"
    assert validate_email("user.name@domain.co.uk"), "Email con subdominio rechazado"
    assert validate_email("user+tag@example.org"), "Email con + rechazado"

def test_invalid_email():
    """Test invalid email format."""
    assert not validate_email("invalid"), "Email sin @ aceptado"
    assert not validate_email("@"), "Solo @ aceptado"
    assert not validate_email("test@"), "Email sin dominio aceptado"
    assert not validate_email("@example.com"), "Email sin usuario aceptado"
    assert not validate_email(""), "Email vacío aceptado"
    assert not validate_email(None), "None aceptado"

def test_single_recipient():
    """Test single recipient validation."""
    is_valid, error, cleaned = validate_recipients(["test@example.com"])
    assert is_valid, f"Destinatario válido rechazado: {error}"
    assert len(cleaned) == 1, "Lista cleaned incorrecta"

def test_multiple_recipients():
    """Test multiple recipients validation."""
    recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
    is_valid, error, cleaned = validate_recipients(recipients)
    assert is_valid, f"Destinatarios válidos rechazados: {error}"
    assert len(cleaned) == 3, "Número de destinatarios incorrecto"

def test_duplicate_recipient():
    """Test duplicate recipient rejection."""
    recipients = ["test@example.com", "test@example.com"]
    is_valid, error, cleaned = validate_recipients(recipients)
    assert not is_valid, "Duplicado no detectado"
    assert "duplicado" in error.lower(), "Mensaje de error incorrecto"

def test_empty_recipient():
    """Test empty recipient rejection."""
    recipients = ["test@example.com", ""]
    is_valid, error, cleaned = validate_recipients(recipients)
    assert not is_valid, "Destinatario vacío no detectado"
    assert "vacío" in error.lower(), "Mensaje de error incorrecto"

def test_empty_recipient_list():
    """Test empty recipient list rejection."""
    is_valid, error, cleaned = validate_recipients([])
    assert not is_valid, "Lista vacía no detectada"
    assert "vacía" in error.lower(), "Mensaje de error incorrecto"

def test_invalid_recipient_email():
    """Test invalid email in recipients."""
    recipients = ["valid@example.com", "invalid-email"]
    is_valid, error, cleaned = validate_recipients(recipients)
    assert not is_valid, "Email inválido no detectado"
    assert "inválido" in error.lower(), "Mensaje de error incorrecto"

def test_whitespace_handling():
    """Test whitespace handling in recipients."""
    recipients = [" test@example.com ", "  user@example.com  "]
    is_valid, error, cleaned = validate_recipients(recipients)
    assert is_valid, f"Espacios no manejados: {error}"
    assert cleaned[0] == "test@example.com", "Espacios no eliminados"
    assert cleaned[1] == "user@example.com", "Espacios no eliminados"

def test_string_recipients():
    """Test string input (comma-separated)."""
    is_valid, error, cleaned = validate_recipients("user1@example.com,user2@example.com")
    assert not is_valid, "String con comas debería fallar (necesita split previo)"

# Run all tests
print("\n" + "=" * 60)
print("SIMPLETELNETMAIL - PRUEBAS DE SEGURIDAD")
print("=" * 60 + "\n")

tests = [
    ("Email válido", test_valid_email),
    ("Email inválido", test_invalid_email),
    ("Un destinatario", test_single_recipient),
    ("Múltiples destinatarios", test_multiple_recipients),
    ("Destinatario duplicado", test_duplicate_recipient),
    ("Destinatario vacío", test_empty_recipient),
    ("Lista vacía", test_empty_recipient_list),
    ("Email inválido en lista", test_invalid_recipient_email),
    ("Manejo de espacios", test_whitespace_handling),
    ("String separado por comas", test_string_recipients),
]

passed = 0
failed = 0

for test_name, test_func in tests:
    if run_test(test_name, test_func):
        passed += 1
    else:
        failed += 1

print("=" * 60)
print(f"RESUMEN: {passed} pasaron, {failed} fallaron")
print("=" * 60)

if failed > 0:
    sys.exit(1)
