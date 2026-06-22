import math
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
import jieba


class BM25Retriever:
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        
        self.documents: List[Dict[str, str]] = []
        self.doc_tokens: List[List[str]] = []
        self.doc_freqs: Dict[str, int] = defaultdict(int)
        self.idf: Dict[str, float] = {}
        self.avgdl: float = 0.0
    
    def _tokenize(self, text: str) -> List[str]:
        return list(jieba.cut(text))
    
    def add_documents(self, documents: List[Dict[str, str]]):
        self.documents = documents
        self.doc_tokens = []
        
        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            self.doc_tokens.append(tokens)
        
        self._calculate_idf()
    
    def _calculate_idf(self):
        N = len(self.documents)
        if N == 0:
            return
        
        self.doc_freqs.clear()
        for tokens in self.doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_freqs[token] += 1
        
        self.idf.clear()
        for token, freq in self.doc_freqs.items():
            self.idf[token] = math.log((N - freq + 0.5) / (freq + 0.5) + 1.0)
        
        total_len = sum(len(tokens) for tokens in self.doc_tokens)
        self.avgdl = total_len / N if N > 0 else 0.0
    
    def _bm25_score(self, query_tokens: List[str], doc_idx: int) -> float:
        score = 0.0
        doc_tokens = self.doc_tokens[doc_idx]
        doc_len = len(doc_tokens)
        token_freqs = Counter(doc_tokens)
        
        for token in query_tokens:
            if token not in self.idf:
                continue
            
            tf = token_freqs.get(token, 0)
            idf = self.idf[token]
            
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            
            score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        if not self.documents:
            return []
        
        query_tokens = self._tokenize(query)
        
        scores = []
        for idx in range(len(self.documents)):
            score = self._bm25_score(query_tokens, idx)
            scores.append((idx, score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, score in scores[:top_k]:
            if score > 0:
                results.append((self.documents[idx], score))
        
        return results
