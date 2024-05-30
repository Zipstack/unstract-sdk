import logging
from typing import Callable, Optional, Union

import tiktoken
from llama_index.core.callbacks import CallbackManager as LlamaIndexCallbackManager
from llama_index.core.callbacks import TokenCountingHandler
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import LLM
from transformers import AutoTokenizer
from typing_extensions import deprecated

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
        set_callback_manager: Returns a standard callback manager

    Example:
        callback_manager = CallbackManager.
                            set_callback_manager(
                                llm="default",
                                embedding="default")
    """

    @staticmethod
    def set_callback(
        platform_api_key: str,
        model: Union[LLM, BaseEmbedding],
        kwargs,
    ) -> None:
        """Sets the standard callback manager for the llm. This is to be called
        explicitly whenever there is a need for the callback handling defined
        here as handlers is to be invoked.

        Parameters:
            llm (LLM): The LLM type

        Returns:
            CallbackManager type of llama index

        Example:
            UNCallbackManager.set_callback_manager(
                platform_api_key: "abc",
                llm=llm,
                embedding=embedding
            )
        """

        # Nothing to do if callback manager is already set for the instance
        if (
            model
            and model.callback_manager
            and len(model.callback_manager.handlers) > 0
        ):
            return

        model.callback_manager = CallbackManager.get_callback_manager(
            model, platform_api_key, kwargs
        )

    @staticmethod
    def get_callback_manager(
        model: Union[LLM, BaseEmbedding],
        platform_api_key: str,
        kwargs,
    ) -> LlamaIndexCallbackManager:
        tokenizer = CallbackManager.get_tokenizer(model)
        token_counter = TokenCountingHandler(tokenizer=tokenizer, verbose=True)
        llm = None
        embedding = None
        if isinstance(model, LLM):
            llm = model
        elif isinstance(model, BaseEmbedding):
            embedding = model
        usage_handler = UsageHandler(
            token_counter=token_counter,
            platform_api_key=platform_api_key,
            llm_model=llm,
            embed_model=embedding,
            kwargs=kwargs,
        )

        callback_manager: LlamaIndexCallbackManager = LlamaIndexCallbackManager(
            handlers=[token_counter, usage_handler]
        )
        return callback_manager

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

    @staticmethod
    @deprecated("Deprecated method. Use the latest set_callback instead")
    def set_callback_manager(
        platform_api_key: str,
        llm: Optional[LLM] = None,
        embedding: Optional[BaseEmbedding] = None,
        **kwargs,
    ) -> LlamaIndexCallbackManager:
        callback_manager: LlamaIndexCallbackManager = LlamaIndexCallbackManager()
        if llm:
            CallbackManager.set_callback(platform_api_key, model=llm, **kwargs)
            callback_manager = llm.callback_manager
        if embedding:
            CallbackManager.set_callback_manager(
                platform_api_key, model=embedding, **kwargs
            )
            callback_manager = embedding.callback_manager
        return callback_manager
