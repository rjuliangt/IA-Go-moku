from flask import Flask, jsonify

app =  Flask(__name__)

@app.route('/', methods = ['GET'])
def inicio():
    return jsonify({"Si dio xd":"xdede"})

if __name__ == '__main__':
    app.run()