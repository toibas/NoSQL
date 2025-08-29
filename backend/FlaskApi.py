import os
from flask import Flask, request
from flask_cors import CORS
from services.login_register_service import LoginRegisterService

class FlaskApp:
    def __init__(self, logfiles_service, health_service, analytics_service, login_register_service):
        self.app = Flask(__name__)
        CORS(self.app)
        self.logfiles_service = logfiles_service
        self.health_service = health_service
        self.analytics_service = analytics_service
        self.login_register_service = login_register_service
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
                print(f"Fehler beim Hochladen der Datei: {e}")
                return {"error": "Internal server error"}, 500
        
        @self.app.route("/logs", methods=["GET"])
        def get_logs():
            try:
                level = request.args.get("level")
                component = request.args.get("component")
                query = request.args.get("q")
                logs = self.logfiles_service.query_logs(level, component, query)
                return {"logs": logs}
            except Exception as e:
                print("Fehler beim Abrufen:", e)
                return {"error": "Fehler beim Abrufen"}, 500

        @self.app.route("/search", methods=["GET"])
        def search():
            query = request.args.get("q")
            level = request.args.get("level")
            component = request.args.get("component")
            from_time = request.args.get("from_time")  
            size = request.args.get("size", default=50, type=int)

            try:
                results = self.analytics_service.search_logs(
                    query=query,
                    level=level,
                    component=component,
                    from_time=from_time,
                    size=size
                )
                return {"logs": results}
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/stats/levels", methods=["GET"])
        def stats_levels():
            try:
                counts = self.analytics_service.count_by_level()
                return {"levels": counts}
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/register", methods=["POST"])
        def register():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            result = self.login_register_service.register(username, password)
            return result, 200 if result.get("success") else 400

        @self.app.route("/login", methods=["POST"])
        def login():
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")
            result = self.login_register_service.login(username, password)
            return result, 200 if result.get("success") else 401

    def run(self, **kwargs):
        self.app.run(**kwargs)


if __name__ == "__main__":
    app = FlaskApp()
    app.run(debug=True)
