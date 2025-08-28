import re
import json
import tempfile
import os
import logging
import requests

class LogfilesService:
    def __init__(self, database):
        self.db = database

    def prepare_bulk_payload_from_log(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            log_text = file.read()

        log_pattern = re.compile(
            r'\d+ms at (?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) -> '
            r'(?P<component>[a-zA-Z0-9_.]+):(?P<level>[A-Z]+):\s+(?P<message>.+)'
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

            bulk_lines.append(json.dumps(action))
            bulk_lines.append(json.dumps(document))

        payload = "\n".join(bulk_lines) + "\n"
        return payload

    def prepare_bulk_payload_from_json(self, file_path):
        bulk_lines = []

        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    json.loads(line)  
                    print(f"Verarbeite JSON-Zeile: {line}")
                    bulk_lines.append(json.dumps({"index": {"_index": "test"}}))
                    bulk_lines.append(line)
                except json.JSONDecodeError:
                    print(f"Ungültige JSON-Zeile ignoriert: {line}")
                    continue

        payload = "\n".join(bulk_lines) + "\n"
        return payload

    def send_bulk_to_elasticsearch(self, payload):
        headers = {'Content-Type': 'application/x-ndjson'}
        es_url = 'http://localhost:9200/_bulk'
        response = requests.post(es_url, data=payload, headers=headers)

        if response.status_code not in [200, 201]:
            print(f"Fehler beim Senden: {response.status_code} - {response.text}")
            return {"success": False, "error": response.text}
        else:
            result = response.json()
            if result.get("errors"):
                return {"success": False, "error": "Einige Einträge konnten nicht gespeichert werden."}
            else:
                return {"success": True, "message": "Bulk-Upload erfolgreich."}

    def save_file_to_db(self, uploaded_file):
        try:
            _, ext = os.path.splitext(uploaded_file.filename)
            suffix = ".json" if ext.lower() == ".json" else ".log"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                uploaded_file.save(tmp)
                tmp_path = tmp.name

            print(f"Temporäre Datei gespeichert: {tmp_path}")

            if suffix == ".json":
                payload = self.prepare_bulk_payload_from_json(tmp_path)
            else:
                payload = self.prepare_bulk_payload_from_log(tmp_path)

            if not payload.strip():
                os.remove(tmp_path)
                return {"error": "Datei enthält keine gültigen Zeilen."}

            result = self.send_bulk_to_elasticsearch(payload)
            os.remove(tmp_path)

            return result if result.get("success") else {"error": result.get("error", "Unbekannter Fehler")}

        except Exception as e:
            logging.error(f"Fehler beim Verarbeiten der Datei: {e}")
            return {"error": "Fehler beim Verarbeiten der Datei"}

    def query_logs(self, level=None, component=None, query=None, size=50):
        body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [{"timestamp": "desc"}],
            "size": size
        }

        if query:
            body["query"]["bool"]["must"].append({
                "match": {"message": query}
            })

        if level:
            body["query"]["bool"]["filter"].append({
                "term": {"level.keyword": level}
            })

        if component:
            body["query"]["bool"]["filter"].append({
                "term": {"component.keyword": component}
            })

        res = self.db.session.post(f"{self.db.base_url}/test/_search", json=body)
        hits = res.json()["hits"]["hits"]
        return [h["_source"] for h in hits]
