class AnalyticsService:
    def __init__(self, database):
        self.db = database
        self.index = "test"

    def search_logs(self, query=None, level=None, component=None, from_time=None, size=50):
        """Logs durchsuchen, optional mit Suchkriterien.

        Args:
            query (str, optional): Suchbegriff. Defaults to None.
            level (str, optional): Log-Level-Filter. Defaults to None.
            component (str, optional): Komponenten-Filter. Defaults to None.
            from_time (str, optional): Startzeit-Filter im ISO-Format. Defaults to None.
            size (int, optional): Anzahl der zurückzugebenden Ergebnisse. Defaults to 50.

        Raises:
            RuntimeError: Wenn ein Fehler bei der Log-Suche auftritt.

        Returns:
            list: Liste der übereinstimmenden Log-Einträge.
        """
        try:
            body = {
                "query": {"bool": {"must": [], "filter": []}},
                "sort": [{"timestamp": "desc"}],
                "size": size
            }

            if query:
                body["query"]["bool"]["must"].append({
                    "query_string": {
                        "query": query,
                        "default_field": "*"
                    }
                })
            if level:
                body["query"]["bool"]["filter"].append({"term": {"level": level}})
            if component:
                body["query"]["bool"]["filter"].append({"term": {"component": component}})
            if from_time:
                body["query"]["bool"]["filter"].append({"range": {"timestamp": {"gte": from_time}}})

            result = self.db.search(self.index, body)
            # print (f"[search_logs] Suchergebnis: {result}")
            # Beispiel result: Ergebnis: {'took': 1, 'timed_out': False, '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
            #                              'hits': {'total': {'value': 1, 'relation': 'eq'}, 'max_score': None, 
            #                              'hits': [{'_index': 'test', '_id': 'KNVXJJkBirDOErcA5Gy5', '_score': None, '_source': 
            #                              {'timestamp': '2025-09-07 15:00:23,054', 'level': 'INFO', 'component': 'auth', 'message': 'Login erfolgreich'}, 'sort': [1757257223054]}]}}
             
            hits = result.get("hits", {}).get("hits", [])
            logs = [hit.get("_source", {}) for hit in hits]
            return logs
        except Exception as e:
            print(f"[search_logs] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Log-Suche: {e}")

    def count_by_level(self):
        """Logs pro Level zählen   .

        Raises:
            RuntimeError: Wenn ein Fehler bei der Log-Zählung auftritt.

        Returns:
            dict: Ein Dictionary mit den Log-Levels als Schlüsseln und deren Zählungen als Werten.
        """
        try:
            body = {"size": 0, "aggs": {"levels": {"terms": {"field": "level"}}}}
            result = self.db.search(self.index, body)
            buckets = result.get("aggregations", {}).get("levels", {}).get("buckets", [])
            
            # print(f"[count_by_level] Ergebnis: {result}")
            # Beispiel Ergebnis: {'took': 1, 'timed_out': False, '_shards': {'total': 1, 'successful': 1, 'skipped': 0, 'failed': 0},
            #                     'hits': {'total': {'value': 6, 'relation': 'eq'}, 'max_score': None, 'hits': []},
            #                     'aggregations': {'levels': {'doc_count_error_upper_bound': 0, 'sum_other_doc_count': 0, 
            #                     'buckets': [{'key': 'ERROR', 'doc_count': 2}, {'key': 'INFO', 'doc_count': 2}, {'key': 'WARN', 'doc_count': 2}]}}}
            
            level_counts = {}
            for bucket in buckets:
                level = bucket.get("key")
                count = bucket.get("doc_count", 0)
                level_counts[level] = count
            return level_counts
        except Exception as e:
            print(f"[count_by_level] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Level-Zählung: {e}")

    def logs_over_time(self):
        """Logs pro Stunde.

        Raises:
            RuntimeError: Wenn ein Fehler bei der Log-Abfrage auftritt.

        Returns:
            dict: Ein Dictionary mit Zeitstempeln als Schlüsseln und deren Log-Zählungen als Werten.
        """
        try:
            body = {
                "size": 0,
                "aggs": {
                    "logs_over_time": {
                        "date_histogram": {"field": "timestamp", "calendar_interval": "hour"},
                        "aggs": {"levels": {"terms": {"field": "level"}}}
                    }
                }
            }
            return self.db.search(self.index, body).get("aggregations", {})
        
        except Exception as e:
            print(f"[logs_over_time] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Zeit-Analyse: {e}")

    def top_error_components(self):
        """Holt die Komponenten mit den meisten Fehlern.

        Raises:
            RuntimeError: Wenn ein Fehler bei der Log-Abfrage auftritt.

        Returns:
            dict: Ein Dictionary mit den Komponenten-Namen als Schlüsseln und deren Fehler-Zählungen als Werten.
        """
        try:
            body = {
                "size": 0,
                "query": {"term": {"level": "ERROR"}},
                "aggs": {"top_components": {"terms": {"field": "component", "size": 10}}}
            }
            return self.db.search(self.index, body).get("aggregations", {})
        except Exception as e:
            print(f"[top_error_components] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Fehler-Komponenten-Analyse: {e}")

