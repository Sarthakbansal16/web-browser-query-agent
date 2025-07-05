import json
import os
import hashlib
from datetime import datetime

class CacheManager:
    def __init__(self, cache_file='query_cache.json'):
        self.cache_file = cache_file
        self.cache_data = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
        return []

    def save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def add_query_result(self, query, embedding, results, source_urls):
        entry = {
            'query_id': hashlib.md5(query.encode()).hexdigest(),
            'original_query': query,
            'embedding': embedding.tolist(),
            'results': results,
            'source_urls': source_urls,
            'timestamp': datetime.now().isoformat()
        }
        self.cache_data.append(entry)
        self.save_cache()
