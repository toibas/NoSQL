import requests
import json
import config
import logging
import re



class Database:
    
    def __init__(self):

        self.base_url = config.ELASTICSEARCH_URL  
        
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        print(f"Verbinde zu Elasticsearch: {self.base_url}")

    def test_connection(self):
        
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200:
                print("Elasticsearch ist erreichbar!")
                return True
            else:
                print("Elasticsearch antwortet nicht")
                return False
        except Exception as e:
            print(f"Fehler: {e}")
            return False

    def search(self, index, body):
        res = self.session.post(f"{self.base_url}/{index}/_search", json=body)
        res.raise_for_status()
        return res.json()

    def aggregate(self, index, body):
        res = self.session.post(f"{self.base_url}/{index}/_search", json=body)
        res.raise_for_status()
        return res.json()





