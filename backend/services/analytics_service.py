class AnalyticsService:
    def __init__(self, database):
        self.db = database
        self.index = "test"

    def search_logs(self, query=None, level=None, component=None, from_time=None, size=50):
        """Search logs with optional filters.

        Args:
            query (str, optional): Search query string. Defaults to None.
            level (str, optional): Log level filter. Defaults to None.
            component (str, optional): Log component filter. Defaults to None.
            from_time (str, optional): Start time filter in ISO format. Defaults to None.
            size (int, optional): Number of results to return. Defaults to 50.

        Raises:
            RuntimeError: If an error occurs during log search.

        Returns:
            list: List of matching log entries.
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

            res = self.db.search(self.index, body)
            return [h["_source"] for h in res["hits"]["hits"]]
        except Exception as e:
            print(f"[search_logs] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Log-Suche: {e}")

    def count_by_level(self):
        """Count logs by log level.

        Raises:
            RuntimeError: If an error occurs during log counting.

        Returns:
            dict: A dictionary with log levels as keys and their counts as values.
        """
        try:
            body = {"size": 0, "aggs": {"levels": {"terms": {"field": "level"}}}}
            res = self.db.search(self.index, body)
            buckets = res.get("aggregations", {}).get("levels", {}).get("buckets", [])
            return {bucket["key"]: bucket["doc_count"] for bucket in buckets}
        except Exception as e:
            print(f"[count_by_level] Fehler: {e}")
            raise RuntimeError(f"Fehler bei der Level-Zählung: {e}")

    def logs_over_time(self):
        """Retrieve log counts over time.

        Raises:
            RuntimeError: If an error occurs during log retrieval.

        Returns:
            dict: A dictionary with timestamps as keys and their log counts as values.
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
        """Retrieve the top error components.

        Raises:
            RuntimeError: If an error occurs during log retrieval.

        Returns:
            dict: A dictionary with component names as keys and their error counts as values.
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

