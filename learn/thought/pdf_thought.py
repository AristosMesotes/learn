import base64
from learn.thought.ithought import IThought


@IThought.thought_type("application/pdf")
class PdfThought(IThought):
    """
    Encapsulates base64-encoded PDF data with optional filename/caption metadata.
    Typically produced by a tool or brain and delivered to platforms as a document.
    """

    def __init__(self, content: bytes | str, role: str = "assistant", filename: str | None = None, **kwargs):
        """
        :param content: PDF bytes or base64-encoded string.
        :param role: Sender role (default 'assistant').
        :param filename: Preferred filename to display in clients (e.g., 'report.pdf').
        :param kwargs: Additional metadata; you can pass message_type to override, caption, etc.
        """
        # Normalize to base64 string
        if isinstance(content, bytes):
            content = base64.b64encode(content).decode("utf-8")

        # Ensure correct MIME
        kwargs.setdefault("message_type", "application/pdf")
        if filename:
            kwargs.setdefault("filename", filename)

        super().__init__(content=content, role=role, **kwargs)

    @property
    def raw_bytes(self) -> bytes:
        if not self.content:
            return b""
        try:
            return base64.b64decode(self.content)
        except Exception:
            return b""

    @property
    def filename(self) -> str:
        return self.get("filename", "document.pdf")
