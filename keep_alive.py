from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Le bot BAF tourne !"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
