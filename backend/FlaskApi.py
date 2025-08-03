import os
from flask import Flask, request
from flask_cors import CORS
from services.logfiles_service import LogfilesService
from services.basic_services import HealthService

class FlaskApp:
    def __init__(self, logfiles_service, health_service):
        self.app = Flask(__name__)
        CORS(self.app)
        self.logfiles_service = logfiles_service
        self.health_service = health_service
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return {"message": "NoSQL API läuft!", "status": "ok"}

        @self.app.route('/test', methods=['GET'])
        def test_db():
            if self.health_service.check_elasticsearch():
                return {"message": "Elasticsearch läuft!", "status": "ok"}
            else:
                return {"message": "Elasticsearch nicht erreichbar", "status": "error"}, 500

        @self.app.route("/upload-log", methods=["POST"])
        def upload_log():
            try:
                if 'logfile' not in request.files:
                    return {"error": "No file part"}, 400
                
                file = request.files['logfile']
                result = self.logfiles_service.save_file_to_db(file)
                return result, 200
                
            except Exception as e:
                return {"error": "Internal server error"}, 500

    def run(self, **kwargs):
        self.app.run(**kwargs)
        
        
if __name__ == "__main__":
    app = FlaskApp()
    app.run(debug=True)
