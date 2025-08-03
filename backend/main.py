from FlaskApi import FlaskApp
from database import Database
from services.logfiles_service import LogfilesService
from services.basic_services import HealthService
from logger import create_logger
import logging

def main():
    logger = create_logger('MainServer', logging.INFO)
    logger.info("Starting NoSQL API Server...")
    
    db = Database()
    logfiles_service = LogfilesService(db)
    health_service = HealthService(db)

    app = FlaskApp(logfiles_service, health_service)

    logger.info("Server startet auf http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()

