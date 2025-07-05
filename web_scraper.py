import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import re

class WebScraper:
    def __init__(self):
        self.max_results = 5
        self.timeout = 30000
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

    async def search_and_scrape(self, query):
        try:
            return await self._playwright_search(query)
        except:
            return await self._requests_fallback(query)

    async def _playwright_search(self, query):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_extra_http_headers({'User-Agent': self.user_agent})
            await page.goto(f"https://duckduckgo.com/?q={query}", timeout=self.timeout)
            await page.wait_for_timeout(3000)
            urls = await page.evaluate("""
                () => [...new Set(Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h.startsWith('http')))]
            """)
            results = []
            for url in urls[:self.max_results]:
                try:
                    subpage = await browser.new_page()
                    await subpage.goto(url, timeout=self.timeout)
                    text = await subpage.inner_text('body')
                    cleaned = self.clean(text)
                    if cleaned:
                        results.append(cleaned[:2000])
                    await subpage.close()
                except:
                    continue
            await browser.close()
            return results, urls[:self.max_results]

    async def _requests_fallback(self, query):
        headers = {'User-Agent': self.user_agent}
        html = requests.get(f"https://duckduckgo.com/html/?q={query}", headers=headers).text
        soup = BeautifulSoup(html, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_='result__a') if a['href'].startswith('http')]
        results = []
        for url in links[:self.max_results]:
            try:
                page = requests.get(url, headers=headers, timeout=10)
                parsed = BeautifulSoup(page.text, 'html.parser')
                [tag.decompose() for tag in parsed(['script', 'style'])]
                cleaned = self.clean(parsed.get_text())
                if cleaned:
                    results.append(cleaned[:2000])
            except:
                continue
        return results, links[:self.max_results]

    def clean(self, content):
        content = re.sub(r'\s+', ' ', content)
        return content.strip()
