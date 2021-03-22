from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main(): # main это название файла с ботом
    return "Бот успешно запустился"



def run():
    app.run(host="0.0.0.0", port = 8080)

def keep_alive():
    server = Thread(target=run)
    server.start()