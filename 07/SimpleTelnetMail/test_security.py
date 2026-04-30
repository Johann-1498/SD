#!/usr/bin/env python3
"""Test script for SimpleTelnetMail security improvements."""

from SimpleTelnetMail.SimpleTelnetMail import TelnetMail

print("=" * 60)
print("TEST 1: Email válido - debe pasar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="test@example.com",
        to=["valid@example.com"],
        message="Test message"
    )
    print("✅ PASS: Email válido aceptado\n")
except ValueError as e:
    print(f"❌ FAIL: {e}\n")

print("=" * 60)
print("TEST 2: Email inválido - debe fallar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="invalid-email",
        to=["valid@example.com"],
        message="Test message"
    )
    print("❌ FAIL: Email inválido aceptado\n")
except ValueError as e:
    print(f"✅ PASS: {e}\n")

print("=" * 60)
print("TEST 3: Destinatario duplicado - debe fallar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="test@example.com",
        to=["test@example.com", "test@example.com"],
        message="Test message"
    )
    print("❌ FAIL: Duplicado aceptado\n")
except ValueError as e:
    print(f"✅ PASS: {e}\n")

print("=" * 60)
print("TEST 4: Destinatario vacío - debe fallar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="test@example.com",
        to=["test@example.com", ""],
        message="Test message"
    )
    print("❌ FAIL: Destinatario vacío aceptado\n")
except ValueError as e:
    print(f"✅ PASS: {e}\n")

print("=" * 60)
print("TEST 5: Host vacío - debe fallar")
print("=" * 60)
try:
    client = TelnetMail(
        "",
        from_="test@example.com",
        to=["valid@example.com"],
        message="Test message"
    )
    print("❌ FAIL: Host vacío aceptado\n")
except ValueError as e:
    print(f"✅ PASS: {e}\n")

print("=" * 60)
print("TEST 6: Username inválido - debe fallar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="test@example.com",
        to=["valid@example.com"],
        message="Test message",
        username="not-an-email"
    )
    print("❌ FAIL: Username inválido aceptado\n")
except ValueError as e:
    print(f"✅ PASS: {e}\n")

print("=" * 60)
print("TEST 7: Múltiples destinatarios válidos - debe pasar")
print("=" * 60)
try:
    client = TelnetMail(
        "smtp.test.com",
        from_="test@example.com",
        to=["user1@example.com", "user2@example.com", "user3@example.com"],
        message="Test message"
    )
    print("✅ PASS: Múltiples destinatarios válidos aceptados\n")
except ValueError as e:
    print(f"❌ FAIL: {e}\n")

print("=" * 60)
print("Resumen: Revisa simple_telnet_mail.log para ver logs")
print("=" * 60)
