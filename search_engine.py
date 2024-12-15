from collections import defaultdict
import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from tqdm import tqdm  # Fortschrittsbalken

@dataclass
class SearchResult:
    doc_id: int
    file_path: str
    module: Optional[str]
    topic: Optional[str]
    instructor: Optional[str]
    relevance_score: float

class SearchEngine:
    def __init__(self):
        self.index: Dict[str, List[int]] = defaultdict(list)
        self.documents: List[Dict] = []
    
    def add_document(self, doc: Dict) -> None:
        """Add a document to the search index"""
        doc_id = len(self.documents)
        self.documents.append(doc)
        
        # Index words with basic text normalization
        text = f"{doc['content']} {doc.get('module', '')} {doc.get('topic', '')} {doc.get('instructor', '')}"
        words = self._tokenize(text)
        
        for word in words:
            self.index[word].append(doc_id)
    
    def add_documents(self, docs: List[Dict]) -> None:
        """Add multiple documents to the search index with progress bar"""
        for doc in tqdm(docs, desc="Indexing Documents", unit="doc"):
            self.add_document(doc)
    
    def _tokenize(self, text: str) -> Set[str]:
        """Tokenize and normalize text"""
        if not text:
            return set()
        # Convert to lowercase and split into words
        words = re.findall(r'\w+', text.lower())
        # Remove common stop words and short terms
        stop_words = {'aber', 'alle', 'allem', 'allen', 'aller', 'alles', 'als', 'also', 'am', 'an', 'ander', 'andere', 'anderem', 'anderen', 'anderer', 'anderes', 'anderm', 'andern', 'anderr', 'anders', 'auch', 'auf', 'aus', 'bei', 'bin', 'bis', 'bist', 'da', 'damit', 'dann', 'den', 'des', 'dem', 'die', 'das', 'dass', 'dein', 'deine', 'deren', 'derer', 'dergleichen', 'desgleichen', 'desto', 'dich', 'dieb', 'dies', 'diese', 'diesem', 'diesen', 'dieser', 'dieses', 'dir', 'doch', 'dort', 'du', 'durch', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'enig', 'einige', 'einigem', 'einigen', 'einiger', 'einiges', 'einmal', 'er', 'ihm', 'ihn', 'ihr', 'ihre', 'ihrem', 'ihren', 'ihrer', 'ihres', 'im', 'in', 'indem', 'ins', 'ist', 'jede', 'jedem', 'jeden', 'jeder', 'jedes', 'jene', 'jenem', 'jenen', 'jener', 'jenes', 'jetzt', 'kann', 'kein', 'keine', 'keinem', 'keinen', 'keiner', 'keines', 'können', 'könnte', 'machen', 'man', 'manche', 'manchem', 'manchen', 'mancher', 'manches', 'mein', 'meine', 'meinem', 'meinen', 'meiner', 'meines', 'mich', 'mit', 'muss', 'musste', 'nach', 'nicht', 'nichts', 'noch', 'nun', 'nur', 'ob', 'oder', 'ohne', 'sehr', 'sein', 'seine', 'seinem', 'seinen', 'seiner', 'seines', 'selbst', 'sich', 'sie', 'sind', 'so', 'solche', 'solchem', 'solchen', 'solcher', 'solches', 'soll', 'sollte', 'sondern', 'sonst', 'über', 'um', 'und', 'uns', 'unse', 'unsen', 'unser', 'unsere', 'unsers', 'unter', 'viel', 'viele', 'vielem', 'vielen', 'vieler', 'vieles', 'vom', 'von', 'vor', 'während', 'war', 'waren', 'warst', 'was', 'weg', 'weil', 'weiter', 'welche', 'welchem', 'welchen', 'welcher', 'welches', 'wenn', 'werde', 'werden', 'werdet', 'wir', 'wird', 'wirst', 'wo', 'wollen', 'wollte', 'würde', 'würden', 'zu', 'zum', 'zur', 'zwar', 'zwischen'}

        stop_words = {'der', 'die', 'das', 'und', 'in', 'im', 'für', 'von', 'mit'}
        return {w for w in words if len(w) > 2 and w not in stop_words}
    
    def search_with_progress(self, query: str, field: Optional[str] = None) -> List[SearchResult]:
        """Search for documents matching the query with progress bar"""
        query_words = self._tokenize(query)
        results = []
        
        if field:
            # Field-specific search
            for doc_id, doc in tqdm(enumerate(self.documents), desc="Searching Documents", unit="doc"):
                if field in doc and doc[field]:
                    field_content = self._tokenize(str(doc[field]))
                    if query_words & field_content:  # Use set intersection
                        score = len(query_words & field_content) / len(query_words)
                        results.append(self._create_search_result(doc_id, score))
        else:
            # Full text search using inverted index
            candidate_docs = self._find_candidate_documents(query_words)
            for doc_id in tqdm(candidate_docs, desc="Calculating Scores", unit="doc"):
                score = self._calculate_relevance_score(doc_id, query_words)
                results.append(self._create_search_result(doc_id, score))
        
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
    
    def _find_candidate_documents(self, query_words: Set[str]) -> Set[int]:
        """Find candidate documents containing query words"""
        candidate_docs = set()
        for word in query_words:
            if word in self.index:
                if not candidate_docs:
                    candidate_docs = set(self.index[word])
                else:
                    candidate_docs &= set(self.index[word])
        return candidate_docs
    
    def _calculate_relevance_score(self, doc_id: int, query_words: Set[str]) -> float:
        """Calculate relevance score for a document"""
        doc_text = self._tokenize(self.documents[doc_id]['content'])
        matching_words = query_words & doc_text
        return len(matching_words) / len(query_words)
    
    def _create_search_result(self, doc_id: int, score: float) -> SearchResult:
        """Create a SearchResult object from a document"""
        doc = self.documents[doc_id]
        return SearchResult(
            doc_id=doc_id,
            file_path=doc['file_path'],
            module=doc.get('module'),
            topic=doc.get('topic'),
            instructor=doc.get('instructor'),
            relevance_score=score
        )
