import logging
from typing import Any
from unstract.sdk.adapters.x2text.llm_whisperer.src.constants import (
    Modes,
    OutputModes,
    WhispererConfig,
    WhispererDefaults,
)
from unstract.sdk.adapters.x2text.llm_whisperer.src.dto import WhispererRequestParams

logger = logging.getLogger(__name__)


class LLMWhispererHelper:

    @staticmethod
    def get_whisperer_params(
        config: dict[str, Any], extra_params: WhispererRequestParams
    ) -> dict[str, Any]:
        """Gets query params meant for /whisper endpoint.

        The params is filled based on the configuration passed.

        Returns:
            dict[str, Any]: Query params
        """
        params = {
            WhispererConfig.MODE: config.get(WhispererConfig.MODE, Modes.FORM.value),
            WhispererConfig.OUTPUT_MODE: config.get(
                WhispererConfig.OUTPUT_MODE, OutputModes.LAYOUT_PRESERVING.value
            ),
            WhispererConfig.LINE_SPLITTER_TOLERANCE: config.get(
                WhispererConfig.LINE_SPLITTER_TOLERANCE,
                WhispererDefaults.LINE_SPLITTER_TOLERANCE,
            ),
            WhispererConfig.LINE_SPLITTER_STRATEGY: config.get(
                WhispererConfig.LINE_SPLITTER_STRATEGY,
                WhispererDefaults.LINE_SPLITTER_STRATEGY,
            ),
            WhispererConfig.HORIZONTAL_STRETCH_FACTOR: config.get(
                WhispererConfig.HORIZONTAL_STRETCH_FACTOR,
                WhispererDefaults.HORIZONTAL_STRETCH_FACTOR,
            ),
            WhispererConfig.PAGES_TO_EXTRACT: config.get(
                WhispererConfig.PAGES_TO_EXTRACT,
                WhispererDefaults.PAGES_TO_EXTRACT,
            ),
            WhispererConfig.MARK_VERTICAL_LINES: config.get(
                WhispererConfig.MARK_VERTICAL_LINES,
                WhispererDefaults.MARK_VERTICAL_LINES,
            ),
            WhispererConfig.MARK_HORIZONTAL_LINES: config.get(
                WhispererConfig.MARK_HORIZONTAL_LINES,
                WhispererDefaults.MARK_HORIZONTAL_LINES,
            ),
            WhispererConfig.PAGE_SEPARATOR: config.get(
                WhispererConfig.PAGE_SEPARATOR,
                WhispererDefaults.PAGE_SEPARATOR,
            ),
            # Not providing default value to maintain legacy compatablity
            # these are optional params and identifiers for audit
            WhispererConfig.TAG: extra_params.tag
            or config.get(
                WhispererConfig.TAG,
                WhispererDefaults.TAG,
            ),
            WhispererConfig.USE_WEBHOOK: config.get(WhispererConfig.USE_WEBHOOK),
            WhispererConfig.WEBHOOK_METADATA: config.get(
                WhispererConfig.WEBHOOK_METADATA
            ),
            WhispererConfig.WAIT_TIMEOUT: config.get(
                WhispererConfig.WAIT_TIMEOUT,
                WhispererDefaults.WAIT_TIMEOUT,
            ),
            WhispererConfig.WAIT_FOR_COMPLETION: WhispererDefaults.WAIT_FOR_COMPLETION,
        }
        if params[WhispererConfig.MODE] == Modes.LOW_COST.value:
            params.update(
                {
                    WhispererConfig.MEDIAN_FILTER_SIZE: config.get(
                        WhispererConfig.MEDIAN_FILTER_SIZE,
                        WhispererDefaults.MEDIAN_FILTER_SIZE,
                    ),
                    WhispererConfig.GAUSSIAN_BLUR_RADIUS: config.get(
                        WhispererConfig.GAUSSIAN_BLUR_RADIUS,
                        WhispererDefaults.GAUSSIAN_BLUR_RADIUS,
                    ),
                }
            )
        return params
