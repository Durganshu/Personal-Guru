from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VectorDB:
    """A lightweight in-memory vector database using TF-IDF for text similarity."""

    def __init__(self):
        """Initialize the TF-IDF VectorDB."""
        self.documents = []
        self.metadata = []
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None
        self.is_fitted = False

    def add_documents(self, documents, metadata=None):
        """
        Add documents to the vector database.

        Args:
            documents (list): List of strings representing the text.
            metadata (list): List of dicts representing metadata for each document.
        """
        if not documents:
            return

        if metadata is None:
            metadata = [{} for _ in documents]

        self.documents.extend(documents)
        self.metadata.extend(metadata)

        # Re-fit the model
        if len(self.documents) > 0:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
            self.is_fitted = True

    def search(self, query, top_k=5):
        """
        Search for documents similar to query.

        Args:
            query (str): The search query.
            top_k (int): Number of top results to return.

        Returns:
            list: List of dicts containing the matched document, metadata, and score.
        """
        if not self.is_fitted or not query.strip():
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Get top_k indices
        top_indices = similarities.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05: # Minimum similarity threshold
                results.append({
                    "content": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "score": float(similarities[idx])
                })

        return results
