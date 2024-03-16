import logging
from typing import Any, Callable, Optional, Union

import tiktoken
from llama_index.core.callbacks import (
    CallbackManager as LlamaIndexCallbackManager,
)
from llama_index.core.callbacks import TokenCountingHandler
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from llama_index.core.llms.utils import LLMType
from transformers import AutoTokenizer

from unstract.sdk.utils.usage_handler import UsageHandler

logger = logging.getLogger(__name__)


class CallbackManager:
    """Class representing the CallbackManager to manage callbacks.

    Use this over the default service context of llama index

    This class supports a tokenizer, token counter,
    usage handler, and  callback manager.

    Attributes:
        None

    Methods:
        get_callback_manager: Returns a standard callback manager

    Example:
        callback_manager = CallbackManager.
                            get_callback_manager(
                                llm="default",
                                embed_model="default")
    """

    @staticmethod
    def get_callback_manager(
        platform_api_key: str,
        workflow_id: str = "",
        execution_id: str = "",
        llm: Optional[LLMType] = None,
        embed_model: Optional[Any] = None,
        **kwargs: Any,
    ) -> LlamaIndexCallbackManager:
        """Returns the service context for UNstract Tools.

        Parameters:
            llm (Optional[LLMType]): The LLM type. Default is None.
            embed_model (Optional[Any]): The embedding model. Default is None.

        Returns:
            CallbackManager: The callback manager

        Example:
            callback_manager = UNCallbackManager.get_callback_manager(
                platform_api_key= "abc",
                llm="default",
                embed_model="default"
            )
        """
        if llm:
            tokenizer = CallbackManager.get_tokenizer(llm)
        elif embed_model:
            tokenizer = CallbackManager.get_tokenizer(embed_model)

        token_counter = TokenCountingHandler(tokenizer=tokenizer, verbose=True)
        usage_handler = UsageHandler(
            token_counter=token_counter,
            platform_api_key=platform_api_key,
            llm_model=llm,
            embed_model=embed_model,
            workflow_id=workflow_id,
            execution_id=execution_id,
        )

        callback_manager: LlamaIndexCallbackManager = LlamaIndexCallbackManager(
            handlers=[token_counter, usage_handler]
        )
        return callback_manager

    @staticmethod
    def set_callback_manager(
        platform_api_key: str,
        llm: Optional[LLM] = None,
        embedding: Optional[BaseEmbedding] = None,
        workflow_id: str = "",
        execution_id: str = "",
    ):
        """Sets the standard callback manager for the llm.

        Parameters:
            llm (LLM): The LLM type

        Returns:
            Nothing

        Example:
            UNCallbackManager.set_callback_manager(
                platform_api_key: "abc",
                llm=llm,
                embedding=embedding
            )
        """
        callback_manager = CallbackManager.get_callback_manager(
            platform_api_key=platform_api_key,
            llm=llm,
            embed_model=embedding,
            workflow_id=workflow_id,
            execution_id=execution_id,
        )
        if llm is not None:
            llm.callback_manager = callback_manager
        if embedding is not None:
            embedding.callback_manager = callback_manager

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
