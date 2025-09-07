import re
import json
import tempfile
import os


class LogfilesService:
    def __init__(self, database):
        self.db = database
        self.index = "test"

    def delete_all_logs(self):
        """
        Löscht alle Logs aus der Datenbank.

        Returns:
            bool: True wenn erfolgreich, sonst False.

        Raises:
            RuntimeError: Bei Fehlern beim Löschen.
        """
        try:
            return self.db.delete_all_logs(self.index)
        except Exception as e:
            print(f"[delete_all_logs] Fehler: {e}")
            return False

    def prepare_bulk_payload_from_log(self, file_path: str):
        """
        Bereitet einen Bulk-Payload aus einer Logdatei für Elasticsearch vor.

        Args:
            file_path (str): Pfad zur Logdatei.

        Returns:
            str: Bulk-Payload als NDJSON-String.

        Raises:
            RuntimeError: Bei Fehlern beim Verarbeiten der Logdatei.
        """
        try:
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

            return "\n".join(bulk_lines) + "\n" if bulk_lines else ""
        except Exception as e:
            print(f"[prepare_bulk_payload_from_log] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Verarbeiten der Logdatei: {e}")

    def prepare_bulk_payload_from_json(self, file_path: str):
        """
        Bereitet einen Bulk-Payload aus einer JSON-Datei für Elasticsearch vor.

        Args:
            file_path (str): Pfad zur JSON-Datei.

        Returns:
            str: Bulk-Payload als NDJSON-String.

        Raises:
            RuntimeError: Bei Fehlern beim Verarbeiten der JSON-Datei.
        """
        bulk_lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        json.loads(line)
                        bulk_lines.append(json.dumps({"index": {"_index": "test"}}))
                        bulk_lines.append(line)
                    except json.JSONDecodeError:
                        continue
            return "\n".join(bulk_lines) + "\n" if bulk_lines else ""
        except Exception as e:
            print(f"[prepare_bulk_payload_from_json] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Verarbeiten der JSON-Datei: {e}")

    def save_file_to_db(self, uploaded_file):
        """
        Speichert eine hochgeladene Datei in der Datenbank (Elasticsearch).

        Args:
            uploaded_file: Die hochgeladene Datei.

        Returns:
            dict: Ergebnis des Bulk-Uploads.

        Raises:
            RuntimeError: Bei Fehlern beim Verarbeiten oder Speichern der Datei.
        """
        try:
            _, ext = os.path.splitext(uploaded_file.filename)
            suffix = ".json" if ext.lower() == ".json" else ".log"

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                uploaded_file.save(tmp)
                tmp_path = tmp.name

            if suffix == ".json":
                payload = self.prepare_bulk_payload_from_json(tmp_path)
            else:
                payload = self.prepare_bulk_payload_from_log(tmp_path)

            os.remove(tmp_path)

            if not payload.strip():
                raise ValueError("Datei enthält keine gültigen Zeilen.")

            self.db.bulk(payload)
            return {"success": True, "message": "Bulk-Upload erfolgreich."}

        except Exception as e:
            print(f"[save_file_to_db] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Verarbeiten der Datei: {e}")

    def query_logs(self, level=None, component=None, query=None, size=50):
        """
        Fragt Logs aus der Datenbank mit optionalen Filtern ab.

        Args:
            level (str, optional): Log-Level-Filter.
            component (str, optional): Komponenten-Filter.
            query (str, optional): Suchbegriff für die Nachricht.
            size (int, optional): Anzahl der Ergebnisse.

        Returns:
            list: Liste der gefundenen Log-Einträge.

        Raises:
            RuntimeError: Bei Fehlern bei der Abfrage.
        """
        try:
            body = {
                "query": {
                    "bool": {"must": [], "filter": []}
                },
                "sort": [{"timestamp": "desc"}],
                "size": size
            }

            if query:
                body["query"]["bool"]["must"].append({"match": {"message": query}})
            if level:
                body["query"]["bool"]["filter"].append({"term": {"level.keyword": level}})
            if component:
                body["query"]["bool"]["filter"].append({"term": {"component.keyword": component}})

            res = self.db.search("test", body)
            return [h["_source"] for h in res["hits"]["hits"]]
        except Exception as e:
            print(f"[query_logs] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Log-Abfrage: {e}")
