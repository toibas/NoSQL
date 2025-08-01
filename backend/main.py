from networking import create_app
from logger import create_logger
import logging

def main():

    logger = create_logger('MainServer', logging.INFO)
    logger.info("Starting NoSQL API Server...")
    
    app = create_app()
    logger.info("Server startet auf http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)



if __name__ == '__main__':
    main()