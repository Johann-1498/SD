#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PySimpleSOAP - Demo GUI
Interfaz grafica para probar servicios SOAP
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pysimplesoap.client import SoapClient
import threading

class SoapDemoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PySimpleSOAP - Demo GUI")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')

        # Header
        header = tk.Frame(root, bg='#2c3e50', height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="PySimpleSOAP - Cliente SOAP Interactivo",
            font=('Arial', 16, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title.pack(pady=25)

        # Main content
        main = tk.Frame(root, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=20, pady=20)

        # Service selection
        service_frame = tk.Frame(main, bg='#f0f0f0')
        service_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            service_frame,
            text="Servicio:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))

        self.service_var = tk.StringVar(value="temp")
        services = [
            ("Conversor de Temperatura", "temp"),
            ("Calculadora", "calc"),
            ("Validador de ISBN", "isbn")
        ]

        for text, value in services:
            rb = tk.Radiobutton(
                service_frame,
                text=text,
                variable=self.service_var,
                value=value,
                font=('Arial', 10),
                bg='#f0f0f0',
                command=self.update_operations
            )
            rb.pack(side='left', padx=10)

        # Operation selection
        op_frame = tk.Frame(main, bg='#f0f0f0')
        op_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            op_frame,
            text="Operacion:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))

        self.operation_var = tk.StringVar()
        self.op_combo = ttk.Combobox(
            op_frame,
            textvariable=self.operation_var,
            width=30,
            font=('Arial', 10)
        )
        self.op_combo.pack(side='left', padx=(0, 20))

        self.update_operations()

        # Parameters
        param_frame = tk.Frame(main, bg='#f0f0f0')
        param_frame.pack(fill='x', pady=(0, 15))

        tk.Label(
            param_frame,
            text="Parametros:",
            font=('Arial', 11, 'bold'),
            bg='#f0f0f0'
        ).pack(side='left', padx=(0, 10))

        self.param_entry = tk.Entry(
            param_frame,
            font=('Arial', 10),
            width=20
        )
        self.param_entry.pack(side='left', padx=(0, 10))

        # Execute button
        self.execute_btn = tk.Button(
            param_frame,
            text="Ejecutar",
            command=self.execute_soap,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        self.execute_btn.pack(side='left')

        # Notebook for tabs
        notebook = ttk.Notebook(main)
        notebook.pack(fill='both', expand=True)

        # Request tab
        request_frame = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(request_frame, text="Request SOAP")

        tk.Label(
            request_frame,
            text="XML Request enviado al servidor:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(10, 5))

        self.request_text = scrolledtext.ScrolledText(
            request_frame,
            font=('Courier New', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white',
            wrap='word'
        )
        self.request_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Response tab
        response_frame = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(response_frame, text="Response SOAP")

        tk.Label(
            response_frame,
            text="XML Response recibido del servidor:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(10, 5))

        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            font=('Courier New', 9),
            bg='#2c3e50',
            fg='#ecf0f1',
            insertbackground='white',
            wrap='word'
        )
        self.response_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Result tab
        result_frame = tk.Frame(notebook, bg='#f0f0f0')
        notebook.add(result_frame, text="Resultado")

        tk.Label(
            result_frame,
            text="Resultado parseado:",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0'
        ).pack(anchor='w', pady=(10, 5))

        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            font=('Courier New', 10),
            bg='#ecf0f1',
            fg='#2c3e50',
            wrap='word'
        )
        self.result_text.pack(fill='both', expand=True, padx=5, pady=5)

        # Status bar
        self.status_var = tk.StringVar(value="Listo - Selecciona servicio y operacion")
        status = tk.Label(
            root,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#34495e',
            fg='white',
            anchor='w',
            padx=10
        )
        status.pack(fill='x', side='bottom')

    def update_operations(self):
        """Update operations based on selected service"""
        service = self.service_var.get()

        if service == "temp":
            ops = ["CelsiusToFahrenheit", "FahrenheitToCelsius"]
        elif service == "calc":
            ops = ["Add", "Subtract", "Multiply", "Divide"]
        else:
            ops = ["CelsiusToFahrenheit", "FahrenheitToCelsius"]

        self.op_combo['values'] = ops
        if ops:
            self.op_combo.set(ops[0])

    def format_xml(self, xml_str):
        """Format XML with indentation"""
        if isinstance(xml_str, bytes):
            xml_str = xml_str.decode('utf-8')

        # Simple XML formatting
        lines = []
        indent = 0
        for line in xml_str.replace('>', '>\n').replace('<', '\n<').split('\n'):
            line = line.strip()
            if line:
                if line.startswith('</'):
                    indent -= 1
                lines.append('  ' * indent + line)
                if line.startswith('<') and not line.endswith('/>') and not line.startswith('</'):
                    indent += 1
        return '\n'.join(lines)

    def execute_soap(self):
        """Execute SOAP call"""
        operation = self.operation_var.get()
        param = self.param_entry.get()

        if not param:
            messagebox.showwarning("Advertencia", "Ingresa un parametro numerico")
            return

        try:
            param = float(param)
        except ValueError:
            messagebox.showerror("Error", "El parametro debe ser numerico")
            return

        # Disable button during execution
        self.execute_btn.config(state='disabled', bg='#95a5a6')
        self.status_var.set("Ejecutando...")

        # Run in thread to avoid freezing GUI
        thread = threading.Thread(target=self._execute_thread, args=(operation, param))
        thread.start()

    def _execute_thread(self, operation, param):
        """Execute SOAP call in background thread"""
        try:
            # Create client
            client = SoapClient(
                location="https://www.w3schools.com/xml/tempconvert.asmx",
                action="https://www.w3schools.com/xml/",
                namespace="https://www.w3schools.com/xml/",
                soap_ns="soap",
                trace=True
            )

            # Execute operation
            if operation == "CelsiusToFahrenheit":
                result = client.CelsiusToFahrenheit(Celsius=param)
            elif operation == "FahrenheitToCelsius":
                result = client.FahrenheitToCelsius(Fahrenheit=param)
            else:
                result = "Operacion no implementada"

            # Get XML
            request_xml = ""
            response_xml = ""
            if hasattr(client, 'xml_request'):
                request_xml = self.format_xml(client.xml_request)
            if hasattr(client, 'xml_response'):
                response_xml = self.format_xml(client.xml_response)

            # Update GUI from main thread
            self.root.after(0, lambda: self._update_gui(
                request_xml, response_xml, result, operation, param
            ))

        except Exception as e:
            self.root.after(0, lambda: self._show_error(str(e)))

    def _update_gui(self, request_xml, response_xml, result, operation, param):
        """Update GUI with results"""
        # Update request tab
        self.request_text.delete(1.0, tk.END)
        self.request_text.insert(1.0, request_xml)

        # Update response tab
        self.response_text.delete(1.0, tk.END)
        self.response_text.insert(1.0, response_xml)

        # Update result tab
        self.result_text.delete(1.0, tk.END)
        unit = "F" if "ToFahrenheit" in operation else "C"
        result_str = f"Operacion: {operation}\n"
        result_str += f"Entrada: {param}\n"
        result_str += f"Resultado: {result} {unit}\n\n"
        result_str += f"{'='*40}\n\n"
        result_str += f"Estado: EXITOSO\n"
        result_str += f"Tiempo: {self.get_timestamp()}"
        self.result_text.insert(1.0, result_str)

        # Re-enable button
        self.execute_btn.config(state='normal', bg='#27ae60')
        self.status_var.set(f"Completado: {operation}({param}) = {result}")

    def _show_error(self, error):
        """Show error message"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, f"ERROR: {error}")
        self.execute_btn.config(state='normal', bg='#27ae60')
        self.status_var.set("Error - Verifica la conexion")

    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def main():
    root = tk.Tk()
    app = SoapDemoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
