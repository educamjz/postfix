#!/usr/bin/python3

############################################################################################################
#
# Descripción: script para extraer las entregas de correo hechas por postix a partir de la información
#              de "maillog", depositando el resultado en un fichero CSV seprado por ";"
#
############################################################################################################
import re
import sys

#  Control de parametros pasados
if len(sys.argv) != 3:
    print("\n[!] Error, se deben pasar dos argumentos al script.\n\n\tUso: " + sys.argv[0] + " <path fichero maillog> <IP>\n")
    sys.exit(1)

# Obtenemos el nombre del fichero y la dirección IP del servidor de Backend
fichero = sys.argv[1]

# Patrón para comprobar si la dirección IP es válida
ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

# Comprobamos si la dirección IP es válida
if not ip_pattern.match(sys.argv[2]):
    print("\n[!] Error: la dirección IP introducida no es válida\n")
    sys.exit(1)
else:
    ip_servidor_destino = sys.argv[2]

# Dicccionario con las entradas de cada envío usando como clave el ticket
lista_correos = {}

# Abrimos el fichero en modo lectura
try:
  with open(fichero, "r") as f:
    # Iteramos sobre cada línea del fichero
    for line in f:
      # Utilizamos una expresión regular para buscar la fecha y la hora
      match = re.search(r"([A-Za-z]{3})\s(\d{2})\s(\d{2}:\d{2}:\d{2})", line)

      # Si hemos encontrado una coincidencia, obtenemos los valores de la fecha y la hora
      if match:
        mes = match.group(1)
        dia = match.group(2)
        hora = match.group(3)
        fecha = dia + "-" + mes + ";" + hora

      # Utilizamos expresiones regulares para buscar el ticket y el email de origen
      match = re.search(r"([0-9A-Fa-f]{13}): from=<(.*)>", line)
      if match:
        ticket = match.group(1)
        email_origen = match.group(2)

        # Vamos nutriendo el diccionario con la fecha y hora y los datos de origen
        if ticket in lista_correos:
          lista_correos[ticket].extend([fecha, email_origen])
        else:
          lista_correos[ticket] = [fecha, email_origen]
      
      # Utilizamos expresiones regulares para buscar el email de destino
      match = re.search(r"([0-9A-Fa-f]{13}): to=<(.*)>, relay=" + ip_servidor_destino, line)
      if match:
        ticket = match.group(1)
        email_destino = match.group(2)
        
        # Vamos nutriendo el diccionario con la fecha y hora y los datos de destino
        if ticket in lista_correos:
          lista_correos[ticket].extend([email_destino])
        else:
          lista_correos[ticket] = [email_destino]
except OSError:
    # Si se produce un error al abrir el fichero, mostramos un mensaje de error y terminamos el script
    print("\n[!] Error: no se puede abrir el fichero '" + fichero + "' o la ruta es incorrecta\n")
    sys.exit(1)

# Abrimos el fichero en modo escritura
try:
  with open("entregas.csv", "w") as f:
    # Imprimimos cabecera CSV
    f.write("Ticket;Día;Hora;De;Para\n")

    # Recorremos el diccionario y escribimos los valores para cada clave (ticket) en el fichero
    for ticket, correos in lista_correos.items():
      if len(correos) == 3:
        f.write(f"{ticket};{';'.join(correos)}\n")
except OSError:
  # Si se produce un error al abrir el fichero, mostramos un mensaje de error y terminamos el script
    print("\n[!] Error: no se puede abrir el fichero de salida CSV\n")
    sys.exit(1)
