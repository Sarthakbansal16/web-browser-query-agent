import openai
import re

class ContentSummarizer:
    def __init__(self, api_key=None):
        self.client = None
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                print(f"OpenAI init failed: {e}")

    async def summarize_content(self, query, content_list):
        combined = "\n\n".join(content_list)
        if self.client:
            try:
                res = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You summarize web data."},
                        {"role": "user", "content": f"Query: {query}\nContent:\n{combined[:4000]}"}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return res.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM failed: {e}")
        return self.fallback_summary(query, combined)

    def fallback_summary(self, query, content):
        sents = re.split(r'[.!?]', content)
        sents = [s.strip() for s in sents if len(s.strip()) > 20]
        query_terms = set(query.lower().split())
        scored = [(sum(1 for t in query_terms if t in s.lower()), s) for s in sents]
        scored = sorted([s for s in scored if s[0] > 0], reverse=True)
        return '. '.join(s for _, s in scored[:5]) + '.' if scored else content[:500] + '...'
