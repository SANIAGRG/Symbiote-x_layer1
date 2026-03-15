from sentence_transformers import SentenceTransformer, util
import config


class TextAnalyzer:
    def __init__(self):
        print("Loading text model...")
        self.model = SentenceTransformer(config.TEXT_MODEL_NAME)
        self._prepare_keywords()

    def _prepare_keywords(self):
        """Pre-compute keyword embeddings"""
        self.threat_embeddings = {}
        for level, keywords in config.THREAT_KEYWORDS.items():
            embeddings = self.model.encode(keywords, convert_to_tensor=True)
            self.threat_embeddings[level] = embeddings

    def calculate_threat(self, text):
        """Calculate threat level from text"""
        text_embedding = self.model.encode(text, convert_to_tensor=True)

        best_score = 0
        best_level = "low"

        for level, embeddings in self.threat_embeddings.items():
            similarities = util.cos_sim(text_embedding, embeddings)
            max_sim = similarities.max().item()

            if max_sim > best_score:
                best_score = max_sim
                best_level = level

        return best_level, round(best_score, 3)

    def analyze(self, text):
        """Main analysis function"""
        print(f"Analyzing text: {text[:50]}...")

        threat_level, threat_score = self.calculate_threat(text)

        result = {
            "text": text,
            "threat_level": threat_level,
            "threat_score": threat_score,
            "confidence": 0.75
        }

        return result