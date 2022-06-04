from pydantic import BaseSettings


HUGGINGFACE_TASK_TAG = "task"

ENV_PREFIX_EXAMPLEPROJECT_SETTINGS = "MLSERVER_MODEL_EXAMPLEPROJECT_"
HUGGINGFACE_PARAMETERS_TAG = "huggingface_parameters"
PARAMETERS_ENV_NAME = "PREDICTIVE_UNIT_PARAMETERS"


class ExampleProjectSettings(BaseSettings):
    """
    Parameters that apply only to alibi huggingface models
    """

    class Config:
        env_prefix = ENV_PREFIX_EXAMPLEPROJECT_SETTINGS

    lambda_value: str = ""

