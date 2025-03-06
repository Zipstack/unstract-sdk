from typing import Optional

from unstract.sdk.tool.stream import StreamMixin


class Extract:
    def __init__(
        self,
        tool: StreamMixin,
        run_id: Optional[str] = None,
        capture_metrics: bool = False,
    ):
        # TODO: Inherit from StreamMixin and avoid using BaseTool
        self.tool = tool
        self._run_id = run_id
        self._capture_metrics = capture_metrics
        self._metrics = {}

    def extract(self):
        pass
