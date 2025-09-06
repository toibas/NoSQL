class HealthService:
    def __init__(self, database):
        self.db = database
    
    def check_elasticsearch(self):
        """Check the connection to Elasticsearch.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        if self.db.test_connection():
            return True
        else:
            return False