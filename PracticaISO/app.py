from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Página para cambiar la IP
@app.route('/cambiar_ip', methods=['GET', 'POST'])
def cambiar_ip():
    if request.method == 'POST':
        ip = request.form.get('ip')
        mascara = request.form.get('mascara')
        puerta = request.form.get('puerta')
        dns = request.form.get('dns')
        print(f"Nueva IP: {ip}, Máscara: {mascara}, Puerta: {puerta}, DNS: {dns}")
    return render_template('cambiar_ip.html')

# Página de gestión de usuarios
@app.route('/gestionar_usuarios')
def gestionar_usuarios():
    return render_template('gestionar_usuarios.html')

# Página de gestión de grupos
@app.route('/gestionar_grupos')
def gestionar_grupos():
    return render_template('gestionar_grupos.html')

# Página de SSH
@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        server_ip = request.form.get('server_ip')
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Conectando a: {server_ip} como {username}")
    return render_template('ssh.html')

# Página de listado de usuarios
@app.route('/usuarios')
def usuarios():
    return render_template('usuarios.html')

# Página de listado de grupos
@app.route('/grupos')
def grupos():
    return render_template('grupos.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
