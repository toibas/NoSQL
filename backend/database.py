import requests
import json
import config


class Database:
    def __init__(self):
        self.base_url = config.ELASTICSEARCH_URL
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def test_connection(self):
        """
        Testet die Verbindung zu Elasticsearch.

        Returns:
            bool: True, wenn die Verbindung erfolgreich ist.

        Raises:
            RuntimeError: Bei Fehlern bei der Verbindung.
        """
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[test_connection] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Verbindung zu Elasticsearch: {e}")

    def delete_all_logs(self, index: str):
        """
        Löscht alle Logs aus dem angegebenen Index.

        Args:
            index (str): Name des Index.

        Returns:
            bool: True, wenn erfolgreich.

        Raises:
            RuntimeError: Bei Fehlern beim Löschen.
        """
        try:
            response = self.session.post(f"{self.base_url}/{index}/_delete_by_query", json={"query": {"match_all": {}}})
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"[delete_all_logs] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Löschen aller Logs: {e}")

    def search(self, index: str, body: dict):
        """
        Führt eine Suche im angegebenen Index aus.

        Args:
            index (str): Name des Index.
            body (dict): Such-Query.

        Returns:
            dict: Ergebnis der Suche.

        Raises:
            RuntimeError: Bei Fehlern bei der Suche.
        """
        try:
            response = self.session.post(f"{self.base_url}/{index}/_search", json=body)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[search] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Suche in Elasticsearch: {e}")

    def bulk(self, payload: str):
        """
        Führt einen Bulk-Insert in Elasticsearch aus.

        Args:
            payload (str): NDJSON-Payload.

        Returns:
            dict: Ergebnis des Bulk-Inserts.

        Raises:
            RuntimeError: Bei Fehlern beim Bulk-Insert.
        """
        headers = {'Content-Type': 'application/x-ndjson'}
        try:
            response = self.session.post(f"{self.base_url}/_bulk", data=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            if result.get("errors"):
                print(f"[bulk] Fehler: Einige Einträge konnten nicht gespeichert werden.")
                raise RuntimeError("Einige Einträge konnten nicht gespeichert werden.")
            return result
        except Exception as e:
            print(f"[bulk] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Bulk-Insert in Elasticsearch: {e}")

    def insert(self, index: str, doc: dict):
        """
        Fügt ein einzelnes Dokument in den angegebenen Index ein.

        Args:
            index (str): Name des Index.
            doc (dict): Dokumentdaten.

        Returns:
            dict: Ergebnis des Inserts.

        Raises:
            RuntimeError: Bei Fehlern beim Einfügen.
        """
        action = {"index": {"_index": index}}
        payload = f"{json.dumps(action)}\n{json.dumps(doc)}\n"
        try:
            return self.bulk(payload)
        except Exception as e:
            print(f"[insert] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Einfügen des Dokuments in Elasticsearch: {e}")
