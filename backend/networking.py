from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database

def create_app():

    app = Flask(__name__)
    CORS(app)  # Frontend-Zugriff erlauben
    db = Database()  
    
    @app.route('/')
    def home():
        return {"message": "NoSQL API läuft!", "status": "ok"}

    @app.route('/test', methods=['GET'])
    def test_db():
        if db.test_connection():
            return {"message": "Elasticsearch läuft!", "status": "ok"}
        else:
            return {"message": "Elasticsearch nicht erreichbar", "status": "error"}, 500

    return app