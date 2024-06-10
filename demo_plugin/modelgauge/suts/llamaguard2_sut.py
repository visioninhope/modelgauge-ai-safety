import os
from modelgauge.prompt import ChatPrompt, TextPrompt
from modelgauge.sut import PromptResponseSUT, SUTCompletion, SUTResponse
from modelgauge.sut_capabilities import AcceptsChatPrompt, AcceptsTextPrompt
from modelgauge.sut_decorator import modelgauge_sut
from modelgauge.sut_registry import SUTS
from modelgauge.annotators.llama_guard_annotator import (
    LlamaGuardAnnotator,
    LlamaGuardAnnotation
)
from modelgauge.suts.together_client import (
    TogetherApiKey,
    TogetherCompletionsResponse,
    TogetherCompletionsRequest,
)
from pydantic import BaseModel


@modelgauge_sut(capabilities=[AcceptsTextPrompt, AcceptsChatPrompt])
class LlamaGuard2SUT(PromptResponseSUT[TogetherCompletionsRequest, TogetherCompletionsResponse]):
    """This SUT demonstrates the bare minimum behavior of a SUT: Use the input Prompt to determine the response."""

    def __init__(
        self,
        uid: str,
        together_api_key: TogetherApiKey
    ):
        super().__init__(uid)
        self.llama_guard_client = LlamaGuardAnnotator(together_api_key)

    def translate_text_prompt(self, prompt: TextPrompt) -> TogetherCompletionsRequest:
        return self.llama_guard_client.translate_request(prompt=None, completion=SUTCompletion(text=prompt.text))

    def translate_chat_prompt(self, prompt: ChatPrompt) -> TogetherCompletionsRequest:
        raise NotImplementedError()

    def evaluate(self, request: TogetherCompletionsRequest) -> TogetherCompletionsResponse:
        # Return Yes if the input is an even number of words
        return self.llama_guard_client.annotate(request)

    def translate_response(
        self, request: TogetherCompletionsRequest, response: TogetherCompletionsResponse 
    ) -> SUTResponse:
        return SUTResponse(completions=[SUTCompletion(text=response.choices[0].text)])


# TODO move the os env var into a constant
SUTS.register(LlamaGuard2SUT, "lg2", together_api_key= TogetherApiKey(os.getenv("TOGETHER_API_KEY")))
