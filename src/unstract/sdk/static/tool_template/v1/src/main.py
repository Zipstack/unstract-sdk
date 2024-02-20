import sys
from typing import Any

from unstract.sdk.tool.base import BaseTool
from unstract.sdk.tool.entrypoint import ToolEntrypoint


# TODO: Rename tool's class
class ConcreteTool(BaseTool):
    # TODO: Add any checks that need to be done before running the tool
    def validate(self, input_file: str, settings: dict[str, Any]) -> None:
        pass

    def run(
        self,
        settings: dict[str, Any],
        input_file: str,
        output_dir: str,
    ) -> None:
        # -------------- TODO: Add your code here ----------------
        # 1. Read the input_file
        # 2. Process on its contents
        # 3. Write files to the output_dir which need to be copied to the
        #    destination.
        # 4. Write the tool result TEXT or JSON
        # TODO: Write tool result of dict or str
        self.write_tool_result(data={})


if __name__ == "__main__":
    args = sys.argv[1:]
    # TODO: Rename tool's class
    tool = ConcreteTool.from_tool_args(args=args)
    ToolEntrypoint.launch(tool=tool, args=args)
