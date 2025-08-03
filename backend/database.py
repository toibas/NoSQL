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

    def prepare_bulk_payload_from_log(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            log_text = file.read()

        log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
            r'(?P<level>[A-Z]+) - '
            r'(?P<component>[a-zA-Z0-9_.]+) - '
            r'(?P<message>.+)'
        )

        bulk_lines = []

        for line in log_text.splitlines():
            match = log_pattern.match(line)
            if not match:
                continue

            action = {"index": {"_index": "test"}}
            document = {
                "timestamp": match.group("timestamp"),
                "level": match.group("level"),
                "component": match.group("component"),
                "message": match.group("message")
            }

            bulk_lines.append(json.dumps(action))       # Action-Zeile
            bulk_lines.append(json.dumps(document))     # Dokument-Zeile


        # NDJSON-Format: jede Zeile ein JSON
        payload = "\n".join(bulk_lines) + "\n"
        return payload


    def send_bulk_to_elasticsearch(self, payload):
        headers = {'Content-Type': 'application/x-ndjson'}
        es_url = 'http://localhost:9200/_bulk'
        response = requests.post(es_url, data=payload, headers=headers)

        if response.status_code not in [200, 201]:
            self.logger.error(f"Fehler beim Senden: {response.status_code} - {response.text}")
        else:
            result = response.json()
            if result.get("errors"):
                self.logger.warning("Einige Einträge konnten nicht gespeichert werden.")
            else:
                self.logger.info("Bulk-Upload erfolgreich.")

if __name__ == "__main__":
    db = Database()
    log_file = "test.log"
    payload = db.prepare_bulk_payload_from_log(log_file)
    db.send_bulk_to_elasticsearch(payload)


