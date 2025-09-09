class HealthService:
    def __init__(self, database):
        self.db = database
    
    def check_elasticsearch(self):
        """Überprüfe die Verbindung zu Elasticsearch.

        Returns:
            bool: True wenn die Verbindung erfolgreich ist, sonst False.
        """
        if self.db.test_connection():
            return True
        else:
            return False