from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('mymap.html')

@app.route('/save', methods=['POST'])
def save_to_db():
    data = request.data
    print (data)
    return (data)

@app.route('/delete', methods=['DELETE'])
def delete_from_db():
    data = request.data
    print (data)
    return (data)

if __name__ == '__main__':
    host = os.getenv("HOST", "127.0.0.1")
    port = os.getenv("PORT", "5000")

    app.run(host=host, port=port)
