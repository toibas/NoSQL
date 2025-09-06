class LoginRegisterService:
    def __init__(self, database):
        self.db = database
        self.index = "user"

    def register(self, username: str, password: str):
        """
        Registriert einen neuen Benutzer.

        Args:
            username (str): Benutzername.
            password (str): Passwort.

        Returns:
            dict: Ergebnis der Registrierung.

        Raises:
            RuntimeError: Bei Fehlern oder wenn der Benutzer bereits existiert.
        """
        try:
            body = {"query": {"term": {"username": username}}}
            res = self.db.search(self.index, body)
            if res["hits"]["total"]["value"] > 0:
                raise ValueError("Benutzer existiert bereits")

            doc = {"username": username, "password": password}
            self.db.insert(self.index, doc)
            return {"success": True, "message": "Registrierung erfolgreich"}
        except Exception as e:
            print(f"[register] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Registrierung: {e}")

    def login(self, username: str, password: str):
        """
        Loggt einen Benutzer ein.

        Args:
            username (str): Benutzername.
            password (str): Passwort.

        Returns:
            dict: Ergebnis des Logins.

        Raises:
            RuntimeError: Bei Fehlern oder ungültigen Zugangsdaten.
        """
        try:
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
            raise ValueError("Login fehlgeschlagen")
        except Exception as e:
            print(f"[login] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Login: {e}")
