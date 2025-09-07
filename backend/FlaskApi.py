from flask import Flask, request
from flask_cors import CORS


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
            """
            Startseite der API.

            Returns:
                dict: Statusnachricht.
            """
            return {"message": "NoSQL API läuft!", "status": "ok"}

        @self.app.route('/test', methods=['GET'])
        def test_db():
            """
            Testet die Verbindung zu Elasticsearch.

            Returns:
                dict: Statusnachricht oder Fehler.
            """
            try:
                if self.health_service.check_elasticsearch():
                    return {"message": "Elasticsearch läuft!", "status": "ok"}
                return {"error": "Elasticsearch nicht erreichbar"}, 500
            except Exception as e:
                return {"error": str(e)}, 500
            
        @self.app.route('/delete-logs', methods=['DELETE'])
        def delete_logs():
            """
            Löscht alle Logs aus der Datenbank.

            Returns:
                dict: Erfolgsmeldung oder Fehler.
            """
            try:
                result = self.logfiles_service.delete_all_logs()
                if result:
                    return {"message": "Alle Logs wurden gelöscht.", "status": "ok"}
                return {"error": "Fehler beim Löschen der Logs."}, 500
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/upload-log", methods=["POST"])
        def upload_log():
            """
            Lädt eine Logdatei hoch und speichert sie in der Datenbank.

            Returns:
                dict: Ergebnis des Uploads oder Fehler.
            """
            try:
                if 'logfile' not in request.files:
                    return {"error": "No file part"}, 400
                file = request.files['logfile']
                result = self.logfiles_service.save_file_to_db(file)
                return result, 200
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/logs", methods=["GET"])
        def get_logs():
            """
            Gibt Logs mit optionalen Filtern zurück.

            Query-Parameter:
                level (str, optional): Log-Level.
                component (str, optional): Komponente.
                q (str, optional): Suchbegriff.

            Returns:
                dict: Gefundene Logs oder Fehler.
            """
            try:
                level = request.args.get("level")
                component = request.args.get("component")
                query = request.args.get("q")
                logs = self.logfiles_service.query_logs(level, component, query)
                return {"logs": logs}
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/search", methods=["GET"])
        def search():
            """
            Sucht Logs mit erweiterten Filtern.

            Query-Parameter:
                q (str, optional): Suchbegriff.
                level (str, optional): Log-Level.
                component (str, optional): Komponente.
                from_time (str, optional): Startzeitpunkt.
                size (int, optional): Anzahl der Ergebnisse.

            Returns:
                dict: Gefundene Logs oder Fehler.
            """
            try:
                query = request.args.get("q")
                level = request.args.get("level")
                component = request.args.get("component")
                from_time = request.args.get("from_time")
                size = request.args.get("size", default=50, type=int)

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
            """
            Gibt die Anzahl der Logs pro Level zurück.

            Returns:
                dict: Level-Statistiken oder Fehler.
            """
            try:
                counts = self.analytics_service.count_by_level()
                return {"levels": counts}
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/register", methods=["POST"])
        def register():
            """
            Registriert einen neuen Benutzer.

            Request-Body:
                username (str): Benutzername.
                password (str): Passwort.

            Returns:
                dict: Ergebnis der Registrierung oder Fehler.
            """
            try:
                data = request.get_json()
                username = data.get("username")
                password = data.get("password")
                result = self.login_register_service.register(username, password)
                return result, 200
            except Exception as e:
                return {"error": str(e)}, 400

        @self.app.route("/login", methods=["POST"])
        def login():
            try:
                data = request.get_json()
                username = data.get("username")
                password = data.get("password")
                result = self.login_register_service.login(username, password)
                return result, 200
            except Exception as e:
                return {"error": str(e)}, 401

        @self.app.route("/user/<user_id>", methods=["PATCH"])
        def update_user(user_id):
            try:
                data = request.get_json() or {}
                new_username = data.get("username")
                result = self.login_register_service.update_user(user_id, new_username)
                return result, 200
            except Exception as e:
                return {"error": str(e)}, 400


        @self.app.route("/stats/timeline", methods=["GET"])
        def stats_timeline():
            """
            Gibt die Loganzahl über die Zeit zurück.

            Returns:
                dict: Timeline-Daten oder Fehler.
            """
            try:
                data = self.analytics_service.logs_over_time()
                return {"timeline": data}
            except Exception as e:
                return {"error": str(e)}, 500

        @self.app.route("/stats/errors/components", methods=["GET"])
        def stats_top_errors():
            """
            Gibt die häufigsten Fehler-Komponenten zurück.

            Returns:
                dict: Fehler-Komponenten oder Fehler.
            """
            try:
                data = self.analytics_service.top_error_components()
                return {"top_error_components": data}
            except Exception as e:
                return {"error": str(e)}, 500

    def run(self, **kwargs):
        self.app.run(**kwargs)


if __name__ == "__main__":
    app = FlaskApp()
    app.run(debug=True)
