#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo simple de PySimpleSOAP - Cliente SOAP
Prueba un servicio público de conversión de temperatura
"""

from pysimplesoap.client import SoapClient
import xml.etree.ElementTree as ET

print("=" * 60)
print("PySimpleSOAP - Cliente SOAP Demo")
print("=" * 60)

# Crear cliente SOAP con servicio público de conversión
print("\n1. Conectando a servicio web...")
try:
    # Servicio público: W3Schools Temperature Converter
    client = SoapClient(
        location="https://www.w3schools.com/xml/tempconvert.asmx",
        action="https://www.w3schools.com/xml/",
        namespace="https://www.w3schools.com/xml/",
        trace=True,  # Mostrar mensajes SOAP
        soap_ns="soap"
    )
    print("[OK] Cliente SOAP creado exitosamente")

    # Llamada 1: Celsius a Fahrenheit
    print("\n2. Convirtiendo 100°C a Fahrenheit...")
    response = client.CelsiusToFahrenheit(Celsius=100)

    print("Respuesta recibida:")
    print(f"  100°C = {response}°F")

    # Llamada 2: Fahrenheit a Celsius
    print("\n3. Convirtiendo 32°F a Celsius...")
    response = client.FahrenheitToCelsius(Fahrenheit=32)

    print("Respuesta recibida:")
    print(f"  32°F = {response}°C")

    print("\n" + "=" * 60)
    print("¡Funciona! SOAP client operativo.")
    print("=" * 60)

except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    print("\nMostrando información de depuración:")

print("\nPresiona Enter para salir...")
input()
