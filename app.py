from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

# Bandera para controlar el procesamiento
procesamiento_activo = True
detener_flag = False  # Bandera para detener el procesamiento

# Ruta para la página principal
@app.route('/')
def index():
    filepath = 'mapeo.png'
    mapa_disponible = os.path.exists(filepath)
    return render_template('index_realtime.html', mapa_disponible=mapa_disponible, now=datetime.now())

# Ruta para recibir datos
@app.route('/recibir_datos', methods=['POST'])
def recibir_datos():
    global procesamiento_activo

    # Verificar si el procesamiento está activo
    if not procesamiento_activo:
        return jsonify({"message": "El procesamiento está detenido.", "status": "stopped"}), 200

    try:
        # Leer el JSON recibido
        datos_recibidos = request.get_json()

        # Validar el formato del JSON
        if not datos_recibidos or 'mejor_ruta' not in datos_recibidos or 'datos' not in datos_recibidos:
            return jsonify({"message": "Formato de datos inválido.", "status": "error"}), 400

        mejor_ruta = datos_recibidos['mejor_ruta']
        datos = datos_recibidos['datos']

        # Imprimir los datos recibidos para verificar
        print(f"Mejor ruta: {mejor_ruta}")
        print("Datos recibidos:")
        for dato in datos:
            print(f"Ángulo: {dato['angulo']}, Distancia: {dato['distancia']} mm")

        # Procesar y generar el mapa
        procesar_mapa_radar(datos)

        # Responder con éxito
        return jsonify({"message": "Datos procesados correctamente.", "status": "success"}), 200

    except Exception as e:
        print(f"Error al procesar los datos: {e}")
        return jsonify({"message": "Error interno del servidor.", "status": "error"}), 500

# Ruta para detener el procesamiento
@app.route('/detener', methods=['POST'])
def detener():
    global procesamiento_activo
    procesamiento_activo = False
    print("Procesamiento detenido.")
    socketio.emit('detener_procesamiento', {'status': 'stopped'})
    return jsonify({'status': 'success', 'message': 'Procesamiento detenido.'}), 200

# Ruta para reiniciar el procesamiento
@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    global procesamiento_activo
    procesamiento_activo = True
    print("Procesamiento reiniciado.")
    socketio.emit('reiniciar_procesamiento', {'status': 'resumed'})
    return jsonify({'status': 'success', 'message': 'Procesamiento reiniciado.'}), 200

# Ruta para servir el mapa generado
@app.route('/mapeo')
def ver_mapeo():
    filepath = 'mapeo.png'
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    else:
        return 'No se ha generado ningún mapa aún.', 404

# Procesar los datos y generar el mapa tipo radar
def procesar_mapa_radar(datos):
    try:
        # Extraer ángulos y distancias de los datos
        angulos = [dato['angulo'] for dato in datos if 'angulo' in dato and 'distancia' in dato]
        distancias = [dato['distancia'] for dato in datos if 'angulo' in dato and 'distancia' in dato]

        # Asegurar que el gráfico es cerrado
        if len(angulos) > 0 and len(distancias) > 0:
            angulos.append(angulos[0])
            distancias.append(distancias[0])

            plt.figure()
            ax = plt.subplot(111, polar=True)
            ax.fill([a * (3.14159 / 180) for a in angulos], distancias, alpha=0.4)
            ax.plot([a * (3.14159 / 180) for a in angulos], distancias, marker='o')
            ax.set_title('Mapa tipo Radar')
            plt.savefig('mapeo.png')
            plt.close()

            print("Mapa generado correctamente.")
            # Emitir evento para actualizar el mapa en el cliente
            socketio.emit('nuevo_mapa', {'message': 'Mapa actualizado'})
        else:
            print("Datos insuficientes para generar el mapa.")
    except Exception as e:
        print(f"Error procesando mapa radar: {e}")



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
