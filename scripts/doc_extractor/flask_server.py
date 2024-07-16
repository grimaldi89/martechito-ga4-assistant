from flask import Flask
from url_extractor import url_extractor_bp
from vectorizer import vectorizer_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(url_extractor_bp, url_prefix='')
    app.register_blueprint(vectorizer_bp, url_prefix='')

    return app

app = create_app()
app.run(host='0.0.0.0', port=8080)