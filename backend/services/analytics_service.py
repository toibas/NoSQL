# services/analytics_service.py

class AnalyticsService:
    def __init__(self, database):
        self.db = database
        self.index = "test"  

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
                    "fields": ["message", "component", "level", "service"]
                }
            })

        if level:
            body["query"]["bool"]["filter"].append({"term": {"level": level}})

        if component:
            body["query"]["bool"]["filter"].append({"term": {"component": component}})

        if from_time:
            body["query"]["bool"]["filter"].append({
                "range": {"timestamp": {"gte": from_time}}
            })

        res_json = self.db.search(self.index, body)
        hits = res_json["hits"]["hits"]
        return [h["_source"] for h in hits]

    def count_by_level(self):
        body = {
            "size": 0,
            "aggs": {
                "levels": {
                    "terms": {"field": "level"}
                }
            }
        }
        res_json = self.db.aggregate(self.index, body)
        buckets = res_json.get("aggregations", {}).get("levels", {}).get("buckets", [])
        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}

    def logs_over_time(self):
        body = {
            "size": 0,
            "aggs": {
                "logs_over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": "hour"
                    },
                    "aggs": {
                        "levels": {
                            "terms": { "field": "level.keyword" }
                        }
                    }
                }
            }
        }
        res = self.db.aggregate(self.index, body)
        return res.get("aggregations", {})


    def top_error_components(self):
        body = {
            "size": 0,
            "query": {
                "term": { "level.keyword": "ERROR" }
            },
            "aggs": {
                "top_components": {
                    "terms": { "field": "component.keyword", "size": 10 }
                }
            }
        }
        res = self.db.aggregate(self.index, body)
        return res.get("aggregations", {})


    def frequent_message_terms(self):
        body = {
            "size": 0,
            "aggs": {
                "common_terms": {
                    "terms": {
                        "field": "message.keyword",
                        "size": 10
                    }
                }
            }
        }
        res = self.db.aggregate(self.index, body)
        return res.get("aggregations", {})
