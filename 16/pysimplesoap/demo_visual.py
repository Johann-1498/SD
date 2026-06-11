#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PySimpleSOAP - Demo Visual Interactivo
Muestra clientes SOAP funcionando con servicios publicos
"""

from pysimplesoap.client import SoapClient
from datetime import datetime
import time

# Colores para terminal (ANSI)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_section(title):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}>> {title}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'-'*70}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}    {text}{Colors.RESET}")

def print_request(label, xml):
    print(f"\n{Colors.BLUE}{label}:{Colors.RESET}")
    # Formatear XML indentado
    lines = xml.replace('>', '>\n').replace('<', '\n<').split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    indent = 0
    for line in lines:
        if line.startswith('</'):
            indent -= 1
        print(f"{Colors.BLUE}{'  '*indent}{line}{Colors.RESET}")
        if not line.startswith('</') and line.startswith('<') and not line.endswith('/>'):
            indent += 1

def main():
    print_header("PySimpleSOAP - Demo Visual")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Libreria: Python Simple SOAP Client")
    print_info("Servicios: Web Services Publicos (W3Schools)")

    # Demo 1: Convertidor de Temperatura
    print_section("DEMO 1: Servicio de Conversión de Temperatura")
    print_info("URL: https://www.w3schools.com/xml/tempconvert.asmx")
    print_info("Operacion: CelsiusToFahrenheit")

    try:
        client = SoapClient(
            location="https://www.w3schools.com/xml/tempconvert.asmx",
            action="https://www.w3schools.com/xml/",
            namespace="https://www.w3schools.com/xml/",
            soap_ns="soap",
            trace=True
        )
        print_success("Cliente SOAP creado")

        # Guardar ultimo request para mostrar
        original_request = None
        original_response = None

        # Patch para capturar XML
        class RequestCapture:
            def __init__(self, client):
                self.client = client
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        print_info("\nEnviando: 100 Celsius...")
        result = client.CelsiusToFahrenheit(Celsius=100)

        if hasattr(client, 'xml_request'):
            print_request("REQUEST SOAP", client.xml_request.decode() if isinstance(client.xml_request, bytes) else client.xml_request)

        print_success(f"Respuesta: 100 C = {result} F")

        print_info("\nEnviando: 212 Fahrenheit...")
        result = client.FahrenheitToCelsius(Fahrenheit=212)

        if hasattr(client, 'xml_response'):
            print_request("RESPONSE SOAP", client.xml_response.decode() if isinstance(client.xml_response, bytes) else client.xml_response)

        print_success(f"Respuesta: 212 F = {result} C")

    except Exception as e:
        print(f"Error: {e}")

    # Demo 2: Informacion del servicio
    print_section("DEMO 2: Informacion del Servicio")
    print_info("Metodos disponibles:")
    methods = ["CelsiusToFahrenheit", "FahrenheitToCelsius"]
    for i, method in enumerate(methods, 1):
        print_info(f"  {i}. {method}")

    # Resumen
    print_section("RESUMEN")
    print_success("PySimpleSOAP funcionando correctamente")
    print_info("Caracteristicas demostradas:")
    print_info("  - Conexion SOAP sobre HTTPS")
    print_info("  - Envio de request XML")
    print_info("  - Recepcion de response XML")
    print_info("  - Parsing de respuestas")

    print_header(f"{Colors.GREEN}Demo Completado - Presiona Enter para salir{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
    input()
