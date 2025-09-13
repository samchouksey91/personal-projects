class OpenAIProvider:
    def __init__(self, model: str):
        self.model = model
    def generate_sql(self, question: str) -> str:
        raise NotImplementedError("Implement using OpenAI client")

class GeminiProvider:
    def __init__(self, model: str):
        self.model = model
    def generate_sql(self, question: str) -> str:
        raise NotImplementedError("Implement using Google client")

class HFLocalProvider:
    def __init__(self, model: str):
        self.model = model
    def generate_sql(self, question: str) -> str:
        raise NotImplementedError("Implement using transformers pipeline")
