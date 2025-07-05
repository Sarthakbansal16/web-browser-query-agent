import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class QueryValidator:
    def __init__(self):
        self.valid_patterns = [r'\b(what|how|where|why|who|which)\b']
        self.invalid_patterns = [r'\b(remind|call|text|turn off)\b']
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except:
            nltk.download('punkt')
            nltk.download('stopwords')

    def validate_query(self, query):
        if not query or len(query.strip()) < 3:
            return False, "Too short"
        q = query.lower()
        for pat in self.invalid_patterns:
            if re.search(pat, q):
                return False, "Command-like query"
        for pat in self.valid_patterns:
            if re.search(pat, q):
                return True, "Valid"
        try:
            words = word_tokenize(q)
            words = [w for w in words if w not in stopwords.words('english') and w.isalnum()]
            return (len(words) >= 2, "Has enough info" if len(words) >= 2 else "Not meaningful")
        except:
            return (len(q.split()) >= 2, "Fallback check")
