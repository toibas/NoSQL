class LoginRegisterService:
    def __init__(self, database):
        self.db = database
        self.index = "user"

    def register(self, username: str, password: str):
        """
        Registriert einen neuen Benutzer.
        """
        try:
            body = {"query": {"term": {"username": username}}}
            res = self.db.search(self.index, body)
            total = res.get("hits", {}).get("total", {})
            total_value = total.get("value", 0) if isinstance(total, dict) else (total or 0)
            if total_value > 0:
                raise ValueError("Benutzer existiert bereits")

            doc = {"username": username, "password": password}
            ins = self.db.insert(self.index, doc)
            items = ins.get("items", [])
            new_id = items[0].get("index", {}).get("_id") if items else None
            return {"success": True, "message": "Registrierung erfolgreich", "id": new_id, "username": username}
        except Exception as e:
            print(f"[register] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Registrierung: {e}")

    def login(self, username: str, password: str):
        """
        Loggt einen Benutzer ein und gibt bei Erfolg _id und username zurück.
        """
        try:
            body = {
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"username": username}},
                            {"term": {"password": password}}
                        ]
                    }
                },
                "_source": ["username"]
            }
            res = self.db.search(index=self.index, body=body)
            hits = res.get("hits", {}).get("hits", [])
            if hits:
                doc = hits[0]
                return {
                    "success": True,
                    "message": "Login erfolgreich",
                    "id": doc.get("_id"),
                    "username": doc.get("_source", {}).get("username"),
                }
            raise ValueError("Login fehlgeschlagen")
        except Exception as e:
            print(f"[login] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Login: {e}")

    def update_user(self, user_id: str, new_username: str):
        """
        Aktualisiert Benutzerdaten. Aktuell werden Benutzername und/oder Passwort unterstützt.
        """
        try:
            fields = {}
            if new_username:
                fields["username"] = new_username

            self.db.update(self.index, user_id, fields, refresh=True)
            g = self.db.get(self.index, user_id)
            source = g.get("_source", {}) if isinstance(g, dict) else {}
            return {
                "success": True,
                "message": "Benutzer aktualisiert",
                "id": user_id,
                "username": source.get("username", new_username),
            }
        except Exception as e:
            print(f"[update_user] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Aktualisieren des Benutzers: {e}")
