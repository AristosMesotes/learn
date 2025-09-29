from learn.thought.ithought import IThought


@IThought.thought_type("plain/txt")
class TextThought(IThought):
    """
    Simple textual message derived from IThought.
    Used widely whenever text is exchanged or converted for LLM calls.
    Forms the core message type throughout Node AI's processing pipeline.
    """
    pass