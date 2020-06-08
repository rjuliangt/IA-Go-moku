from flask import Flask, jsonify, render_template

app = Flask(__name__)


# ROUTER OF DE PAGE WEB METHODS GET
@app.route('/', methods=['GET'])
def inicio():
    return render_template('index.html')


@app.route('/play_game', methods=['GET'])
def play_game():
    return render_template('board.html')


@app.route('/move_player', methods=['GET'])
def move_player():
    return jsonify({"Juagador": "Movida"})


@app.route('/move_entity', methods=['GET'])
def move_entity():
    return jsonify({"Juagador Ente": "Movida"})


# METHODS POST
@app.route('/player_move', methods=['GET'])
def player_move():
    return jsonify({"Juagador": ""})


# RUN SERVER FLASK
if __name__ == '__main__':
    # app.run(port = 3000, debug = True) UNA MANERA MAS DE ESTABLECER UN PUERTO ESPECIFICO
    app.run(debug=True)  # para que al hacer cambio se actualice la pag solo
