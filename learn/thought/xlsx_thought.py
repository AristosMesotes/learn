import base64
from learn.thought.ithought import IThought

# Register BOTH modern XLSX and legacy XLS to the same class.
@IThought.thought_type("application/vnd.ms-excel")  # .xls (legacy)
@IThought.thought_type("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # .xlsx (modern)
class XlsxThought(IThought):
    """
    Encapsulates base64-encoded Excel data (XLSX or XLS) with optional filename/caption metadata.
    """

    def __init__(
        self,
        content: bytes | str,
        role: str = "assistant",
        filename: str | None = None,
        *,
        mime_type: str | None = None,
        **kwargs,
    ):
        """
        :param content: Excel bytes or base64-encoded string.
        :param role: Sender role (default 'assistant').
        :param filename: e.g., 'workbook.xlsx' or 'workbook.xls'
        :param mime_type: Explicit MIME if you need to force .xls vs .xlsx.
                          Defaults to the modern XLSX MIME.
        :param kwargs: Additional metadata (e.g., caption).
        """
        if isinstance(content, bytes):
            content = base64.b64encode(content).decode("utf-8")

        if mime_type is None:
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # default XLSX
        kwargs.setdefault("message_type", mime_type)

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
        # Choose default extension based on message_type
        mt = self.mime_type
        if mt == "application/vnd.ms-excel":
            return self.get("filename", "workbook.xls")
        return self.get("filename", "workbook.xlsx")
