from learn.thought.ithought import IThought
from learn.thought.vision_thought import VisionThought


@IThought.thought_type("image/png")
class VisionPngMessage(VisionThought):
    """
    Subclass of VisionThought for PNG-encoded images instead of JPEG.
    Used interchangeably when PNG data flows through the vision pipeline.
    Keeps Node AI flexible with different image formats.
    """

    def __init__(self, content: bytes, role: str = "user", **kwargs):
        super().__init__(role=role, content=content, **kwargs)
