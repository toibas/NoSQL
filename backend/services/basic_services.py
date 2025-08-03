class HealthService:
    def __init__(self, database):
        self.db = database
    
    def check_elasticsearch(self):
        if self.db.test_connection():
            return True
        else:
            return False