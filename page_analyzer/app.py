from flask import Flask


def app(environ, start_response):
    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Welcome to Flask'

    # data = 'Hello. World!'
    #
    # start_response("200 OK", [
    #     ("Content-Type", "text/plain"),
    #     ("Content-Length", str(len(data)))
    # ])
    return app.run()

if __name__ == '__main__':
    app()
