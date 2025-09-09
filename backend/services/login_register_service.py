class LoginRegisterService:
    def __init__(self, database):
        self.db = database
        self.index = "user"

    def register(self, username: str, password: str):
        """Registriert einen neuen Benutzer.

        Args:
            username (str): Der Benutzername des neuen Benutzers.
            password (str): Das Passwort des neuen Benutzers.

        Raises:
            ValueError: Wenn der Benutzer bereits existiert.
            RuntimeError: Wenn ein Fehler bei der Registrierung auftritt.

        Returns:
            dict: Ein Dictionary mit dem Ergebnis der Registrierung.
        """
        try:
            body = {"query": {"term": {"username": username}}}
            result = self.db.search(self.index, body)
            
            total = result.get("hits", {}).get("total", {})
            total_value = 0
            if isinstance(total, dict):
                total_value = total.get("value", 0)
            else:
                total_value = 0
            if total_value > 0:
                raise ValueError("Benutzer existiert bereits")

            body = {"username": username, "password": password}
            insert = self.db.insert(self.index, body)
            items = insert.get("items", [])
            new_id = None
            if items:
                index_info = items[0].get("index", {})
                new_id = index_info.get("_id")
            
            return {"success": True, "message": "Registrierung erfolgreich", "id": new_id, "username": username}
        except Exception as e:
            print(f"[register] Fehler: {e}")
            raise RuntimeError(f"Fehler bei Registrierung: {e}")

    def login(self, username: str, password: str):
        """Loggt einen Benutzer ein.

        Args:
            username (str): Der Benutzername.
            password (str): Das Passwort.

        Raises:
            ValueError: Wenn die Anmeldedaten ungültig sind.
            RuntimeError: Wenn ein Fehler bei der Anmeldung auftritt.

        Returns:
            dict: Ein Dictionary mit dem Ergebnis der Anmeldung.
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
        """Aktualisiert die Benutzerdaten.

        Args:
            user_id (str): Die doc_id des Benutzers.
            new_username (str): Der neue Benutzername.

        Raises:
            RuntimeError: Wenn ein Fehler bei der Aktualisierung auftritt.

        Returns:
            dict: Ein Dictionary mit dem Ergebnis der Aktualisierung.
        """
        try:
            fields = {}
            if new_username:
                fields["username"] = new_username

            self.db.update(self.index, user_id, fields, refresh=True)
            new_data = self.db.get(self.index, user_id)
            
            #print (f"[update_user] new_data: {new_data}")
            # {'_index': 'user', '_id': '3fbK9ZgBXZGO1HUkZvE6', '_version': 3, '_seq_no': 4, '_primary_term': 4, 'found': True, '_source': {'username': 'test', 'password': 'test'}}
            source = {}
            if isinstance(new_data, dict):
                source = new_data.get("_source", {})
            return {
                "success": True,
                "message": "Benutzer aktualisiert",
                "id": user_id,
                "username": source.get("username", new_username),
            }
        except Exception as e:
            print(f"[update_user] Fehler: {e}")
            raise RuntimeError(f"Fehler beim Aktualisieren des Benutzers: {e}")
