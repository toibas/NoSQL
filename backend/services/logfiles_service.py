import re
import json
import tempfile
import os
from logger import create_logger
import logging

class LogfilesService:
    def __init__(self, database):
        self.db = database
        self.logger = create_logger('LogfilesService', logging.INFO)
    
# working upload mit .log file 
#     def prepare_bulk_payload_from_log(self, file_path):
#         with open(file_path, 'r', encoding='utf-8') as file:
#             log_text = file.read()

#         log_pattern = re.compile(
#             r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - '
#             r'(?P<level>[A-Z]+) - '
#             r'(?P<component>[a-zA-Z0-9_.]+) - '
#             r'(?P<message>.+)'
#         )

#         bulk_lines = []

#         for line in log_text.splitlines():
#             match = log_pattern.match(line)
#             if not match:
#                 continue

#             action = {"index": {"_index": "test"}}
#             document = {
#                 "timestamp": match.group("timestamp"),
#                 "level": match.group("level"),
#                 "component": match.group("component"),
#                 "message": match.group("message")
#             }

#             bulk_lines.append(json.dumps(action))       # Action-Zeile
#             bulk_lines.append(json.dumps(document))     # Dokument-Zeile


#         # NDJSON-Format: jede Zeile ein JSON
#         payload = "\n".join(bulk_lines) + "\n"
#         return payload


#     def send_bulk_to_elasticsearch(self, payload):
#         headers = {'Content-Type': 'application/x-ndjson'}
#         es_url = 'http://localhost:9200/_bulk'
#         response = requests.post(es_url, data=payload, headers=headers)

#         if response.status_code not in [200, 201]:
#             self.logger.error(f"Fehler beim Senden: {response.status_code} - {response.text}")
#         else:
#             result = response.json()
#             if result.get("errors"):
#                 self.logger.warning("Einige Einträge konnten nicht gespeichert werden.")
#             else:
#                 self.logger.info("Bulk-Upload erfolgreich.")