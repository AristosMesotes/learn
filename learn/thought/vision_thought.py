import base64

from learn.thought.ithought import IThought


@IThought.thought_type("image/jpeg")
class VisionThought(IThought):
    """
    Represents an image message stored as base64 JPEG with optional query text.
    Used by vision-related brain clients to send or receive pictures.
    Enables Node AI to route visual information through LLM pipelines.
    """

    def __init__(self, content: bytes, role: str = "user", **kwargs):
        if isinstance(content, bytes):
            content = base64.b64encode(content).decode("utf-8")
        super().__init__(role=role, content=content, **kwargs)

    @property
    def query(self) -> str:
        """
        Retrieve the 'query' string from metadata, if present.
        """
        return self.get("query", "")

