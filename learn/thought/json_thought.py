import json

from learn.thought.ithought import IThought


@IThought.thought_type("application/json")
class JsonThought(IThought):
    """
    Message wrapper for structured JSON content.
    Frequently produced or consumed by LLM methods expecting typed data.
    Enables Node AI tools and storage layers to handle structured responses.
    """

    def __init__(self, content: dict, role: str = "user", **kwargs):
        if isinstance(content, str):
            content = json.loads(content)
        super().__init__(content, role, **kwargs)
