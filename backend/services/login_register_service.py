import json

class LoginRegisterService:
    def __init__(self, database):
        self.db = database
        self.index = "user"

    def register(self, username, password):
        body = {
            "query": {
                "term": {"username": username}
            }
        }
        res = self.db.search(self.index, body)
        if res["hits"]["total"]["value"] > 0:
            return {"success": False, "error": "Benutzer existiert bereits"}

        doc = {"username": username, "password": password}
        action = {"index": {"_index": self.index}}
        payload = f"{json.dumps(action)}\n{json.dumps(doc)}\n"
        es_url = f"{self.db.base_url}/_bulk"
        resp = self.db.session.post(es_url, data=payload, headers={'Content-Type': 'application/x-ndjson'})
        if resp.status_code in [200, 201]:
            return {"success": True, "message": "Registrierung erfolgreich"}
        else:
            return {"success": False, "error": "Fehler bei der Registrierung"}

    def login(self, username, password):
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"username": username}},
                        {"term": {"password": password}}
                    ]
                }
            }
        }
        res = self.db.search(self.index, body)
        if res["hits"]["total"]["value"] > 0:
            return {"success": True, "message": "Login erfolgreich"}
        else:
            return {"success": False, "error": "Login fehlgeschlagen"}