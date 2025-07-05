import argparse
import asyncio
from agent import WebBrowserQueryAgent

def format_results(result):
    if result['status'] == 'invalid':
        return f"❌ {result['message']}\nReason: {result['reason']}"
    elif result['status'] == 'error':
        return f"💥 Error: {result['message']}"
    elif result['status'] == 'cached':
        out = f"📋 Cached Result (from {result['timestamp'][:10]})\n"
        out += f"Original query: '{result['original_query']}'\n\n"
        out += f"{result['results']}\n\nSources:\n" + '\n'.join(result['source_urls'])
        return out
    elif result['status'] == 'success':
        out = "🌐 Fresh Result\n\n" + result['results'] + "\n\nSources:\n" + '\n'.join(result['source_urls'])
        return out
    return "Unknown result status"

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', help='OpenAI API Key')
    parser.add_argument('--query', help='Query to search')
    args = parser.parse_args()

    agent = WebBrowserQueryAgent(args.api_key)
    if args.query:
        result = await agent.process_query(args.query)
        print(format_results(result))
    else:
        print("Welcome to Web Query Agent. Type 'exit' to quit.")
        while True:
            query = input("Query: ").strip()
            if query.lower() == 'exit': break
            result = await agent.process_query(query)
            print(format_results(result))

if __name__ == '__main__':
    asyncio.run(main())

# === File: agent.py ===
from query_validator import QueryValidator
from similarity_engine import QuerySimilarityEngine
from cache_manager import CacheManager
from web_scraper import WebScraper
from content_summarizer import ContentSummarizer
from datetime import datetime

class WebBrowserQueryAgent:
    def __init__(self, api_key=None):
        self.validator = QueryValidator()
        self.similarity_engine = QuerySimilarityEngine()
        self.cache_manager = CacheManager()
        self.scraper = WebScraper()
        self.summarizer = ContentSummarizer(api_key)

    async def process_query(self, query):
        is_valid, reason = self.validator.validate_query(query)
        if not is_valid:
            return {'status': 'invalid', 'message': 'Query not suitable.', 'reason': reason}

        similar = self.similarity_engine.find_similar_query(query, self.cache_manager.cache_data)
        if similar:
            return {
                'status': 'cached',
                'results': similar['results'],
                'source_urls': similar['source_urls'],
                'timestamp': similar['timestamp'],
                'original_query': similar['original_query']
            }

        content_list, urls = await self.scraper.search_and_scrape(query)
        if not content_list:
            return {'status': 'error', 'message': 'Failed to fetch content.'}

        summary = await self.summarizer.summarize_content(query, content_list)
        embedding = self.similarity_engine.get_embedding(query)
        self.cache_manager.add_query_result(query, embedding, summary, urls)

        return {
            'status': 'success',
            'results': summary,
            'source_urls': urls,
            'timestamp': datetime.now().isoformat()
        }
