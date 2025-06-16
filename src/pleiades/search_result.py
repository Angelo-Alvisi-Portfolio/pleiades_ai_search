class SearchResult:
    def __init__(self, title: str, link: str, snippet: str):
        self.title = title
        self.link = link
        self.snippet = snippet

    def __repr__(self):
        return f"SearchResult(title={self.title}, link={self.link}, snippet={self.snippet})"

    def __str__(self):
        return f"{self.title} ({self.link}) - {self.snippet}"