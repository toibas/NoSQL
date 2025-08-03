import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database

def create_app():

    app = Flask(__name__)
    CORS(app)  # Frontend-Zugriff erlauben
    db = Database()  
    UPLOAD_FOLDER = './logcache_test'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    @app.route('/')
    def home():
        return {"message": "NoSQL API läuft!", "status": "ok"}

    @app.route('/test', methods=['GET'])
    def test_db():
        if db.test_connection():
            return {"message": "Elasticsearch läuft!", "status": "ok"}
        else:
            return {"message": "Elasticsearch nicht erreichbar", "status": "error"}, 500

    @app.route("/upload-log", methods=["POST"])
    def upload_log():
        if 'logfile' not in request.files:
            return {"error": "No file part"}, 400
        
        file = request.files['logfile']
        
        if file.filename == '':
            return {"error": "No selected file"}, 400
        
        if not file.filename.endswith('.log'):
            return {"error": "Only .log files allowed"}, 400
        
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)
        
        return {"message": "File uploaded successfully"}, 200



    return app