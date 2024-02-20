import requests
from llama_index.callbacks import TokenCountingHandler
from llama_index.callbacks.schema import CBEventType
from unstract.sdk.constants import LogLevel, ToolEnv
from unstract.sdk.helper import SdkHelper
from unstract.sdk.tool.stream import StreamMixin


class Audit(StreamMixin):
    """The 'Audit' class is responsible for pushing usage data to the platform
    service.

    Methods:
        - push_usage_data: Pushes the usage data to the platform service.

    Attributes:
        None

    Example usage:
        audit = Audit()
        audit.push_usage_data(
            token_counter,
            workflow_id,
            execution_id,
            external_service,
            event_type)
    """

    def __init__(self, log_level: LogLevel = LogLevel.INFO) -> None:
        super().__init__(log_level)

    def push_usage_data(
        self,
        platform_api_key: str,
        token_counter: TokenCountingHandler = None,
        workflow_id: str = "",
        execution_id: str = "",
        external_service: str = "",
        event_type: CBEventType = None,
    ) -> None:
        """Pushes the usage data to the platform service.

        Args:
            token_counter (TokenCountingHandler, optional): The token counter
              object. Defaults to None.
            workflow_id (str, optional): The ID of the workflow. Defaults to "".
            execution_id (str, optional): The ID of the execution. Defaults
              to "".
            external_service (str, optional): The name of the external service.
              Defaults to "".
            event_type (CBEventType, optional): The type of the event. Defaults
              to None.

        Returns:
            None

        Raises:
            requests.RequestException: If there is an error while pushing the
            usage details.
        """
        platform_host = self.get_env_or_die(ToolEnv.PLATFORM_HOST)
        platform_port = self.get_env_or_die(ToolEnv.PLATFORM_PORT)

        base_url = SdkHelper.get_platform_base_url(
            platform_host=platform_host, platform_port=platform_port
        )
        bearer_token = platform_api_key

        data = {
            "usage_type": event_type,
            "external_service": external_service,
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "embedding_tokens": token_counter.total_embedding_token_count,
            "prompt_tokens": token_counter.prompt_llm_token_count,
            "completion_tokens": token_counter.completion_llm_token_count,
            "total_tokens": token_counter.total_llm_token_count,
        }

        url = f"{base_url}/usage"
        headers = {"Authorization": f"Bearer {bearer_token}"}

        try:
            response = requests.post(
                url, headers=headers, json=data, timeout=30
            )
            if response.status_code != 200:
                self.stream_log(
                    log=(
                        "Error while pushing usage details: "
                        f"{response.status_code} {response.reason}",
                    ),
                    level=LogLevel.ERROR,
                )
            else:
                self.stream_log("Successfully pushed usage details")

        except requests.RequestException as e:
            self.stream_log(
                log=f"Error while pushing usage details: {e}",
                level=LogLevel.ERROR,
            )
