import numpy as np
from mlserver.model import MLModel
from mlserver.settings import ModelSettings
from fastapi import status
from mlserver.utils import get_model_uri
from mlserver.errors import InvalidModelURI, MLServerError
from mlserver.types import (
    InferenceRequest,
    InferenceResponse,
)
from mlserver.codecs import NumpyCodec, NumpyRequestCodec
from example_project.common import ExampleProjectSettings


class ExampleProject(MLModel):
    """Runtime class for specific Huggingface models"""

    def __init__(self, settings: ModelSettings):

        self._extra_settings = ExampleProjectSettings(**settings.parameters.extra)  # type: ignore

        super().__init__(settings)

    async def load(self) -> bool:
        # Simple showcase reading a lambda as string either from file or 
        try:
            model_uri = await get_model_uri(self._settings)
            with open(model_uri, "r") as f:
                self._model = eval(f.read())
        except (InvalidModelURI, IsADirectoryError):
            self._model = eval(self._extra_settings.lambda_value)

        if not callable(self._model):
            raise MLServerError("Invalid lambda value provided", status.HTTP_500_INTERNAL_SERVER_ERROR)

        self.ready = True
        return self.ready

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        """
        Prediction request
        """
        # For more advanced request decoding see MLServer codecs documentation
        model_input = NumpyRequestCodec.decode(payload)

        model_output = self._model(model_input)
        model_output_np = np.array(model_output)

        encoded_output = NumpyCodec.encode("predict", model_output_np)

        return InferenceResponse(
            model_name=self.name,
            model_version=self.version,
            outputs=[encoded_output],
        )
