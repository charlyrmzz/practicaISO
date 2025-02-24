import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import paramiko
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# Mantenemos un diccionario de conexiones activas
active_connections = {}

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Página para cambiar la IP
@app.route('/cambiar-ip', methods=['GET', 'POST'])
def cambiar_ip():
    if request.method == 'POST':
        nueva_ip = request.form['ip']
        mascara = request.form['mascara']
        puerta = request.form['puerta']
        dns = request.form['dns']

        # Ruta del archivo de configuración de red (ejemplo para Ubuntu con Netplan)
        netplan_config = "/etc/netplan/01-network-manager-all.yaml"

        # Contenido actualizado del archivo de configuración
        config_content = f"""
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:
      addresses:
        - {nueva_ip}/{mascara}
      gateway4: {puerta}
      nameservers:
        addresses:
          - {dns}
        """

        try:
            # Escribir la nueva configuración en el archivo
            with open(netplan_config, 'w') as file:
                file.write(config_content)

            # Aplicar la nueva configuración de red
            os.system("sudo netplan apply")

        except Exception as e:
            return f"Error al modificar la configuración: {e}"

        return redirect(url_for('index'))

    return render_template('cambiar_ip.html')

# Función para manejar la conexión SSH y la ejecución de comandos
def ssh_connection_thread(client_id, server_ip, username, password):
    try:
        # Crear el cliente SSH
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(server_ip, username=username, password=password)

        # Invocar el canal para ejecutar comandos
        channel = ssh_client.invoke_shell()

        # Guardar el canal en el diccionario de conexiones activas
        active_connections[client_id] = channel

        # Función para manejar la salida del canal
        def handle_channel():
            while True:
                output = channel.recv(1024)
                if output:
                    socketio.emit('output', {'client_id': client_id, 'output': output.decode()})

                # Verificar si el canal está cerrado o no se recibe más salida
                if channel.exit_status_ready():
                    break

        # Ejecutar la función de manejar el canal en un hilo separado
        threading.Thread(target=handle_channel, daemon=True).start()

    except Exception as e:
        print(f"Error en la conexión SSH: {e}")
        socketio.emit('output', {'client_id': client_id, 'output': f"Error: {e}\n"})

# Ruta para recibir los comandos desde el cliente
@socketio.on('command')
def handle_command(data):
    client_id = data['client_id']
    command = data['command']

    # Verificar si existe una conexión activa para este cliente
    channel = active_connections.get(client_id)

    if channel:
        # Enviar el comando al canal SSH
        channel.send(command + '\n')
    else:
        socketio.emit('output', {'client_id': client_id, 'output': "No hay conexión SSH activa.\n"})

# Manejo de la conexión SSH desde el frontend
@socketio.on('connect_ssh')
def connect_ssh(data):
    server_ip = data['server_ip']
    username = data['username']
    password = data['password']

    client_id = request.sid  # Obtener el ID de la sesión de SocketIO
    socketio.start_background_task(ssh_connection_thread, client_id, server_ip, username, password)

# Página gestionar usuarios
@app.route('/gestionar_usuarios')
def gestionar_usuarios():
    return render_template('gestionar_usuarios.html')

# Página gestionar grupos
@app.route('/gestionar_grupos')
def gestionar_grupos():
    return render_template('gestionar_grupos.html')

# Página de listado de usuarios
@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

# Página de listado de grupos
@app.route('/grupos')
def grupos():
    return render_template('grupos.html')

# Ruta de conexión SSH
@app.route('/ssh')
def ssh():
    return render_template('ssh.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    socketio.run(app, debug=True)
