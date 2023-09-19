from flask import Flask, redirect, url_for


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Welcome to Flask'

if __name__ == "__main__":
    app.run(debug=True)
