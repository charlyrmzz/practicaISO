from flask import Flask, render_template, request, redirect, url_for
import os
import paramiko

app = Flask(__name__)

# Ruta principal (Página de inicio)
@app.route('/')
def index():
    return render_template('index.html')

# Página para cambiar la dirección IP
@app.route('/cambiar-ip', methods=['GET', 'POST'])
def cambiar_ip():
    if request.method == 'POST':
        nueva_ip = request.form['ip']
        mascara = request.form['mascara']
        puerta = request.form['puerta']
        dns = request.form['dns']
        
        # Ruta del archivo Netplan
        netplan_config = "/etc/netplan/01-netcfg.yaml"
        
        # Contenido actualizado del archivo Netplan
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

# Página para conectar por SSH
@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        server_ip = request.form['server_ip']
        username = request.form['username']
        password = request.form['password']

        try:
            # Establecer conexión SSH usando paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(server_ip, username=username, password=password)
            
            # Ejecutar un comando de prueba
            stdin, stdout, stderr = client.exec_command("echo 'Conexión SSH exitosa'")
            output = stdout.read().decode()
            
            client.close()
            return f"Conectado a {server_ip}: {output}"
        except Exception as e:
            return f"Error en la conexión SSH: {e}"

    return render_template('ssh.html')

# Ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
