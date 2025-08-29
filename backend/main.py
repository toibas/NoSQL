from FlaskApi import FlaskApp
from database import Database
from services.logfiles_service import LogfilesService
from services.basic_services import HealthService
from services.analytics_service import AnalyticsService
from services.login_register_service import LoginRegisterService
import logging

def main():
    print("Starting NoSQL API Server...")
    db = Database()
    logfiles_service = LogfilesService(db)
    health_service = HealthService(db)
    analytics_service = AnalyticsService(db)
    login_register_service = LoginRegisterService(db)

    app = FlaskApp(logfiles_service, health_service, analytics_service, login_register_service)

    print("Server startet auf http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()

