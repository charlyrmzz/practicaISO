from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Ruta principal (Página de inicio)
@app.route('/')
def index():
    return render_template('index.html')

# Página para cambiar la dirección IP (ÚNICA DEFINICIÓN)
@app.route('/cambiar-ip', methods=['GET', 'POST'])
def cambiar_ip():
    if request.method == 'POST':
        nueva_ip = request.form['ip']
        mascara = request.form['mascara']
        puerta = request.form['puerta']
        dns = request.form['dns']

        # Simulación del cambio de IP (requiere permisos de administrador)
        comando = f"sudo ifconfig eth0 {nueva_ip} netmask {mascara}"
        os.system(comando)

        comando_puerta = f"sudo route add default gw {puerta}"
        os.system(comando_puerta)

        comando_dns = f"echo 'nameserver {dns}' | sudo tee /etc/resolv.conf"
        os.system(comando_dns)

        return redirect(url_for('index'))

    return render_template('cambiar_ip.html')

# Página para conectar por SSH
@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        server_ip = request.form['server_ip']
        username = request.form['username']
        password = request.form['password']

        # Simulación de conexión SSH
        comando_ssh = f"sshpass -p '{password}' ssh {username}@{server_ip}"
        os.system(comando_ssh)

        return redirect(url_for('index'))

    return render_template('ssh.html')

# Ejecutar el servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
