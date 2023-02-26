import os

from pydantic import Field
from pydantic import UUID4
from pydantic_sqs import SQSModel
from pydantic_sqs import SQSQueue


class AsyncTask(SQSModel):
    uuid: str = Field(..., description="This task's uuid")
    message: str = Field(..., description="The message to print")


queue_kwargs = {
    "queue_url": os.environ.get("SQS_QUEUE_URL"),
    "endpoint_url": os.environ.get("SQS_ENDPOINT_URL", None),
    "use_ssl": os.environ.get("SQS_USE_SSL", "true").lower() == "true",
}
if queue_kwargs["endpoint_url"] is None:
    del queue_kwargs["endpoint_url"]

QUEUE = SQSQueue(**queue_kwargs)
QUEUE.register_model(AsyncTask)
