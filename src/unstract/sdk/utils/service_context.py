import logging
from typing import Any, Callable, Optional, Union

import tiktoken
from llama_index import ServiceContext as LlamaIndexServiceContext
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.core.embeddings.base import BaseEmbedding
from llama_index.llms import LLM
from llama_index.llms.utils import LLMType
from transformers import AutoTokenizer
from unstract.sdk.utils.usage_handler import UsageHandler

logger = logging.getLogger(__name__)


class ServiceContext:
    """Class representing the UNServiceContext.

    Use this over the default service context of llama index

    This class provides a static method to get the service context for
    UNstract Tools. The service context includes a tokenizer, token counter,
    usage handler, and  callback manager.

    Attributes:
        None

    Methods:
        get_service_context: Returns the service context for UNstract Tools.

    Example:
        service_context = UNServiceContext.
                            get_service_context(
                                workflow_id="123",
                                execution_id="456",
                                llm="default",
                                embed_model="default")
    """

    @staticmethod
    def get_service_context(
        platform_api_key: str,
        workflow_id: str = "",
        execution_id: str = "",
        llm: Optional[LLMType] = None,
        embed_model: Optional[Any] = None,
        **kwargs: Any,
    ) -> LlamaIndexServiceContext:
        """Returns the service context for UNstract Tools.

        Parameters:
            workflow_id (str): The workflow ID. Default is an empty string.
            execution_id (str): The execution ID. Default is an empty string.
            llm (Optional[LLMType]): The LLM type. Default is None.
            embed_model (Optional[Any]): The embedding model. Default is None.

        Returns:
            ServiceContext: The service context for UNstract Tools.

        Example:
            service_context = UNServiceContext.get_service_context(
                workflow_id="123",
                execution_id="456",
                llm="default",
                embed_model="default"
            )
        """
        if llm:
            tokenizer = ServiceContext.get_tokenizer(llm)
        elif embed_model:
            tokenizer = ServiceContext.get_tokenizer(embed_model)

        token_counter = TokenCountingHandler(tokenizer=tokenizer, verbose=True)
        usage_handler = UsageHandler(
            token_counter=token_counter,
            platform_api_key=platform_api_key,
            llm_model=llm,
            embed_model=embed_model,
            workflow_id=workflow_id,
            execution_id=execution_id,
        )

        callback_manager = CallbackManager(
            handlers=[token_counter, usage_handler]
        )
        return LlamaIndexServiceContext.from_defaults(
            llm=llm,
            embed_model=embed_model,
            callback_manager=callback_manager,
            **kwargs,
        )

    @staticmethod
    def get_tokenizer(
        model: Optional[Union[LLM, BaseEmbedding, None]],
        fallback_tokenizer: Callable[[str], list] = tiktoken.encoding_for_model(
            "gpt-3.5-turbo"
        ).encode,
    ) -> Callable[[str], list]:
        """Returns a tokenizer function based on the provided model.

        Args:
            model (Optional[Union[LLM, BaseEmbedding]]): The model to use for
            tokenization.

        Returns:
            Callable[[str], List]: The tokenizer function.

        Raises:
            OSError: If an error occurs while loading the tokenizer.
        """

        try:
            if isinstance(model, LLM):
                model_name: str = model.metadata.model_name
            elif isinstance(model, BaseEmbedding):
                model_name = model.model_name

            tokenizer: Callable[[str], list] = AutoTokenizer.from_pretrained(
                model_name
            ).encode
            return tokenizer
        except OSError as e:
            logger.warning(str(e))
            return fallback_tokenizer
