from telnetlib import Telnet
from ssl import _create_stdlib_context
from base64 import b64decode, b64encode
from hmac import new
import re
import logging
from datetime import datetime
from os import path

""" This file implement the TelnetMail class. """

# Configure logging
LOG_FILE = "simple_telnet_mail.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Email regex pattern
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def validate_email(email):
    """Validate email format. Returns True if valid, False otherwise."""
    if not email or not isinstance(email, str):
        return False
    return EMAIL_PATTERN.match(email.strip()) is not None

def validate_recipients(recipients):
    """Validate recipients list. Returns (is_valid, error_message, cleaned_list)."""
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

###################
#    This package implement a simple SMTP client with Telnet.
#    Copyright (C) 2020, 2021  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

# Datetime Format : Sat, 25 Dec 2021 05:35:23 -0000

# Importance : low, normal, hight
# Priority : non-urgent, normal, urgent
# Sensibility : Personal, Private, Company-Confidential


class TelnetMail:

    """ This class send plaintext email (not secure) with Telnet """

    def __init__(
        self,
        host: str,
        port: int = None,
        from_: str = None,
        to: list = None,
        message: str = None,
        ehlo: str = "SimpleTelnetMail",
        pseudo: str = "",
        ssl: bool = True,
        debug: int = 0,
        username: str = None,
        password: str = None,
        **kwargs,
    ):

        # Validate required fields
        if not host or not host.strip():
            raise ValueError("Error: El servidor SMTP (host) es obligatorio.")

        self.host = host.strip()

        if port:
            self.port = port
        elif ssl:
            self.port = 465
        else:
            self.port = 25

        # Validate from email
        if from_ and not validate_email(from_):
            raise ValueError(f"Error: Formato de email inválido en 'from': {from_}")
        self.from_ = from_.strip() if from_ else None

        # Validate username if provided
        if username and not validate_email(username):
            raise ValueError(f"Error: Formato de username inválido: {username}")
        self.username = username.strip() if username else None

        # Validate and clean recipients
        if to:
            is_valid, error_msg, cleaned_to = validate_recipients(to)
            if not is_valid:
                raise ValueError(error_msg)
            self.to = cleaned_to
        else:
            self.to = None

        self.message = message
        if message and not message.strip():
            raise ValueError("Error: El mensaje no puede estar vacío.")

        self.ehlo = ehlo
        self.headers = kwargs
        self.responses = b""
        self.pseudo = pseudo
        self.ssl = ssl
        self.debug = debug
        self.password = password
        self.send_status = "PENDING"  # Track send status for logging

    def __repr__(self):
        return f"<TelnetMail : SERVER={self.host}:{self.port} COMPUTERNAME={self.ehlo} FROM={self.from_} TO={self.to} SSL={self.ssl}>"

    def __str__(self):
        string = (
            f"{self.host}:{self.port}\n\tEHLO {self.ehlo}\n\tMAIL FROM: {self.from_}"
        )
        for t in self.to:
            string += f"\n\tRCPT TO: {t}"

        message = self.message.replace("\n\r", "\n").replace("\n", "\n\t\t")
        string += f"\n\tDATA:\n\t\t{message}"

        return string + "\bQUIT"

    def end_message(self):

        """ This method add "END" characters to close the mail. """

        self.message += "\n.\n"

    def add_headers(self):

        """ This method add headers in mail. """

        headers_string = ""

        for key, value in self.headers.items():
            key = key.replace("_", "-")
            headers_string += f"{key}: {value}\n"

        self.message = headers_string + "\n\r" + self.message

    def get_response(self, client, starttls=False):

        """ Get response and return True if request is accepted or False if isn't. """

        responses = client.read_some().split(b"\r\n")
        while responses[-1] != b"":
            new_responses = client.read_some().split(b"\r\n")
            responses[-1] += new_responses[0]
            responses += new_responses[1:]

        for response in responses[:-1]:
            # print(responses) # DEBUG
            self.responses += response + b"\r\n"
            if response[:3] == b"220":
                if starttls:
                    return 6
                code = self.ehlo_and_helo(client)
                if code == 1:
                    code = 0  # New connection initalised
            elif response[:3] == b"250":
                if response[3] == b"-":  # For EHLO multilines responses
                    code = 5
                code = 1  # OK
            elif response[0] == 51:  # Error 3xy
                code = 2
            elif response[0] == 52:  # Error 4xy
                code = 3
            elif response[0] == 53:  # Error 5xy
                code = 4
            else:  # UNKNOW : not in RFC
                code = 7

        if code == 5:  # For EHLO multilines responses
            code = self.get_response(client)
        return code

    def authentication(self, client):

        """ This method perform an SMTP authentication. """

        def get_auth_type(responses):

            """ This method return the auth type """

            for auth_type in ("CRAM-MD5", "PLAIN", "LOGIN"):
                if auth_type in responses.decode():
                    return auth_type

        def send_password(client, password):

            """ This function encode and send the password. """

            client.write(b64encode(password.encode()) + b"\r\n")

        auth_type = get_auth_type(self.responses)

        if auth_type:
            client.write(f"AUTH {auth_type}\r\n".encode())
            self.get_response(client)
        else:
            print("ERROR: this server don't have authentication method.")
            return

        response = self.responses.decode().split("\r\n")[-2]

        if auth_type == "CRAM-MD5" and len(response) > 4 and response[:4] == "334 ":
            send_password(
                client,
                f"{self.username} "
                + new(
                    self.password.encode(), b64decode(response[4:].encode()), "md5"
                ).hexdigest(),
            )
        elif auth_type == "PLAIN" and response[:3] == "334":
            send_password(client, f"\0{self.username}\0{self.password}")
        elif auth_type == "LOGIN":
            send_password(client, f"{self.username}")
            self.get_response(client)
            send_password(client, self.password)
        else:
            return

        self.get_response(client)

    def ehlo_and_helo(self, client):

        """ Send ehlo and helo message to initialize the mail connection. """

        client.write(f"EHLO {self.ehlo}\r\n".encode())
        self.get_response(client)
        client.write(f"HELO {self.ehlo}\r\n".encode())
        return self.get_response(client)

    def starttls(self, client):

        """ This method start the TLS connection. """

        client.write("STARTTLS\r\n".encode())
        response = self.get_response(client, starttls=True)
        if response == 6:
            context = _create_stdlib_context()
            client.sock = context.wrap_socket(client.sock, server_hostname=self.host)
            self.ehlo_and_helo(client)
            return True
        return False

    def send_mail(self):

        """ This method send mail with Telnet. """

        # Final validation before sending
        if not self.from_:
            raise ValueError("Error: El remitente (from) es obligatorio para enviar.")
        if not self.to:
            raise ValueError("Error: Los destinatarios (to) son obligatorios para enviar.")
        if not self.message:
            raise ValueError("Error: El mensaje es obligatorio para enviar.")

        # Log attempt
        logging.info(f"INICIO - Servidor: {self.host}:{self.port}, Remitente: {self.from_}, Destinatarios: {', '.join(self.to)}")

        self.add_headers()
        self.end_message()

        try:
            client = Telnet(self.host, port=self.port)
            client.set_debuglevel(self.debug)
            self.get_response(client)

            if self.ssl:
                self.starttls(client)
            if self.username and self.password:
                self.authentication(client)

            if self.pseudo:
                client.write(f"MAIL FROM: <{self.from_}>\r\n".encode())
            else:
                client.write(f"MAIL FROM: <{self.from_}>\r\n".encode())
            self.get_response(client)

            for address in self.to:
                client.write(f"RCPT TO: <{address}>\r\n".encode())
                self.get_response(client)

            client.write("DATA\r\n".encode())
            self.get_response(client)
            for line in self.message.split("\n"):
                client.write(f"{line}\r\n".encode())
            self.get_response(client)
            client.write("QUIT \r\n".encode())

            try:
                self.responses += client.read_all()
            except ConnectionResetError:
                pass
            except ConnectionAbortedError:
                pass

            # Check if email was sent successfully
            response_str = self.responses.decode()
            if "250" in response_str and "2.0.0" in response_str:
                self.send_status = "SUCCESS"
                logging.info(f"EXITO - Correo enviado a {', '.join(self.to)}")
            else:
                self.send_status = "FAILED"
                logging.warning(f"FALLO - Respuesta SMTP: {response_str[:200]}")

        except Exception as e:
            self.send_status = f"ERROR: {str(e)}"
            logging.error(f"EXCEPCION - {str(e)}")
            raise


def simple_usage():
    client = TelnetMail(
        "my.server.com",
        from_="my.address@domain.com",
        to=["receiver@domain.com"],
        message="Secret and not secure email with Telnet.",
        ssl=False,
    )
    client.send_mail()

    client = TelnetMail(
        "my.server.com",
        from_="my.address@domain.com",
        to=["receiver@domain.com"],
        message="Secret and not secure email with Telnet.",
        ssl=False,
        username="my.address@domain.com",
        password="password",
    )
    client.send_mail()

    print(repr(client))
    print(client)
    print(client.responses.decode())


def advanced_usage():
    client = TelnetMail(
        "my.server.com",
        port=587,
        from_="my.address@domain.com",
        to=["receiver1@domain.com", "receiver2@domain.com"],
        message="Secret and secure email with Telnet.",
        ehlo="H4CK3R",
        pseudo="Mr_X",
        ssl=True,
        debug=4,
        Subject="Secret Email",
        Date="Sat, 19 Dec 2020 01:02:03 -0000",
        MIME_Version="1.0",
        Encrypted="ROT13",
        Fake="Fake hearder",
        Sender="PSEUDO <test@free.fr>",
        Comments="My comment",
        Keywords="Email, Secret",
        Expires="Sat, 25 Dec 2021 05:35:23 -0000",
        Language="en-EN, it-IT",
        Importance="hight",
        Priority="urgent",
        Sensibility="Company-Confidential",
        From="PSEUDO <test@free.fr>",
        To="receiver1@domain.com,receiver2@domain.com",
        Content_Type="text/plain; charset=us-ascii",
        Content_Transfer_Encoding="quoted-printable",
    )
    client.send_mail()

    print(repr(client))
    print(client)
    print(client.responses.decode())


def main():
    from sys import argv
    from getopt import getopt

    help_ = False
    arguments = {
        "host": None,
        "from": None,
        "to": None,
        "message": None,
        "port": 25,
        "ehlo": "SimpleTelnetMail",
        "pseudo": " ",
        "debug": 0,
        "ssl": False,
        "username": False,
        "password": False,
    }
    headers = {}

    optlist, args = getopt(
        argv[1:],
        "H:p:f:t:e:m:P:d:U:W:s",
        [
            "host=",
            "port=",
            "from=",
            "to=",
            "ehlo=",
            "message=",
            "pseudo=",
            "debug=",
            "username=",
            "password=",
            "ssl",
        ],
    )

    for argument in optlist:
        if argument[0] == "--host" or argument[0] == "-H":
            client = TelnetMail(argument[1])
            arguments["host"] = argument[1]
        elif argument[0] == "--from" or argument[0] == "-f":
            arguments["from"] = argument[1]
        elif argument[0] == "--to" or argument[0] == "-t":
            arguments["to"] = argument[1]
        elif argument[0] == "--message" or argument[0] == "-m":
            arguments["message"] = argument[1]
        elif argument[0] == "--port" or argument[0] == "-p":
            try:
                arguments["port"] = int(argument[1])
            except ValueError:
                print(
                    "ArgumentError: --port value or -p value must be an integer. Port is set to 25."
                )
        elif argument[0] == "--ehlo" or argument[0] == "-e":
            arguments["ehlo"] = argument[1]
        elif argument[0] == "--pseudo" or argument[0] == "-P":
            arguments["pseudo"] = argument[1]
        elif argument[0] == "--username" or argument[0] == "-U":
            arguments["username"] = argument[1]
        elif argument[0] == "--password" or argument[0] == "-W":
            arguments["password"] = argument[1]
        elif argument[0] == "--ssl" or argument[0] == "-s":
            arguments["ssl"] = True
        elif argument[0] == "--debug" or argument[0] == "-d":
            try:
                arguments["debug"] = int(argument[1])
            except ValueError:
                print(
                    "ArgumentError: --debug value or -d value must be an integer. Debug is set to 0."
                )
        else:
            breakpoint()
            help_ = True
            break

    for argument in args:
        if "=" in argument:
            argument = argument.split("=", 1)
            headers[argument[0]] = argument[1]
        else:
            breakpoint()
            help_ = True
            break

    for presence in arguments.values():
        if presence is None:
            breakpoint()
            help_ = True
            break

    if help_:
        help()
        exit(1)

    client.port = arguments["port"]
    client.ehlo = arguments["ehlo"]
    client.from_ = arguments["from"]
    client.to = arguments["to"].split(",")
    client.message = arguments["message"]
    client.pseudo = arguments["pseudo"]
    client.debug = arguments["debug"]
    client.ssl = arguments["ssl"]
    client.username = arguments["username"]
    client.password = arguments["password"]
    client.headers = headers

    print("Enviando correo...")

    try:
        client.send_mail()
        print("Correo enviado exitosamente!")
        print(f"Estado: {client.send_status}")
        print(f"Log guardado en: {LOG_FILE}")
    except ValueError as e:
        print(f"\nError de validación: {e}")
        exit(1)
    except Exception as e:
        print(f"\nError al enviar: {e}")
        exit(1)

    print("\nDebugging : ")

    print(repr(client))
    print(client)
    print(client.responses.decode())


def help():
    print(
        """
SimpleTelnetMail (HEADERS) (OPTIONS) [ ARGUMENTS : <host> <from> <to> <message> ]

ARGUMENTS :
    --host=<smtp.server.com>            -H=<smtp.server.com>
    --from=<my.address@domain.com>      -f=<my.address@domain.com>
    --to=<receiver@domain.com>          -t=<receiver@domain.com>
    --message=<my email message>        -m=<my email message>

OPTIONS :
    --port=<port number : default=25>   -p=<port number : default=25>
    --pseudo=<pseudo : default=" ">     -P=<pseudo : default=" ">
    --debug=<debug level : default=0>   -d=<debug level : default=0>
    --username=<username>               -U=<username>
    --password=<password>               -W=<password>
    --ssl                               -s
    --ehlo=<my hostname : default=SimpleTelnetMail> -e=<my hostname : default=SimpleTelnetMail>

ADD HEADERS :
    HeaderName=<HeaderValue>
    Examples :
        Subject="My Simple Subject !"
        Sender="PSEUDO <my.adress@domain.com>"
        Date="Sat, 25 Dec 2021 05:35:23 -0000"

EXAMPLES :
    SimpleTelnetMail --host="smtp.server.com" --from="my.address@domain.com" --to="receiver@domain.com" --message="my email message"
    SimpleTelnetMail -H "smtp.server.com" -f "my.address@domain.com" -t "receiver@domain.com" -m "my email message" --username="my.address@domain.com" --password="password"
"""
    )


if __name__ == "__main__":
    main()
