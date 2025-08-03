import requests
import json
import config
from logger import create_logger
import logging
import re



class Database:
    
    def __init__(self):

        self.base_url = config.ELASTICSEARCH_URL  
        self.logger = create_logger('ElasticsearchDB', logging.INFO)
        
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        self.logger.info(f"Verbinde zu Elasticsearch: {self.base_url}")
    
    def test_connection(self):
        
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                self.logger.info("Elasticsearch ist erreichbar!")
                return True
            else:
                self.logger.error("Elasticsearch antwortet nicht")
                return False
        except Exception as e:
            self.logger.error(f"Fehler: {e}")
            return False





