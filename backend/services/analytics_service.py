# services/analytics_service.py

class AnalyticsService:
    def __init__(self, database):
        self.db = database
        self.index = "test"  # oder dynamisch übergeben, wenn du mehrere verwendest

    def search_logs(self, query=None, level=None, component=None, from_time=None, size=50):
        body = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "sort": [{"timestamp": "desc"}],
            "size": size
        }

        if query:
            body["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["message^3", "component", "level"]
                }
            })

        if level:
            body["query"]["bool"]["filter"].append({
                "term": { "level.keyword": level }
            })

        if component:
            body["query"]["bool"]["filter"].append({
                "term": { "component.keyword": component }
            })

        if from_time:
            body["query"]["bool"]["filter"].append({
                "range": {
                    "timestamp": {
                        "gte": from_time
                    }
                }
            })

        res = self.db.session.post(f"{self.db.base_url}/{self.index}/_search", json=body)
        res.raise_for_status()
        hits = res.json()["hits"]["hits"]
        return [h["_source"] for h in hits]

    def count_by_level(self):
        body = {
            "size": 0,
            "aggs": {
                "levels": {
                    "terms": {
                        "field": "level.keyword"
                    }
                }
            }
        }

        res = self.db.session.post(f"{self.db.base_url}/{self.index}/_search", json=body)
        res.raise_for_status()
        buckets = res.json().get("aggregations", {}).get("levels", {}).get("buckets", [])
        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}
