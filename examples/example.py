import asyncio
import os
from pprint import pprint

from pydantic import Field
from pydantic_sqs import SQSModel
from pydantic_sqs import SQSQueue


class ThisModel(SQSModel):
    foo: int = Field(..., description="Foo")


class ThatModel(SQSModel):
    bar: str = Field(..., description="bar")


async def main():
    queue_kwargs = {
        "queue_url": os.environ.get("SQS_QUEUE_URL"),
        "endpoint_url": os.environ.get("SQS_ENDPOINT_URL", None),
        "use_ssl": os.environ.get("SQS_USE_SSL", "true").lower() == "true",
    }
    if queue_kwargs["endpoint_url"] is None:
        del queue_kwargs["endpoint_url"]

    queue = SQSQueue(**queue_kwargs)

    queue.register_model(ThisModel)
    queue.register_model(ThatModel)

    this_thing = ThisModel(foo=1234)
    that_thing = ThatModel(bar="baz")
    await this_thing.to_sqs()
    await that_thing.to_sqs()

    new_things = await queue.from_sqs(max_messages=10, wait_time_seconds=90)
    pprint(new_things)
    for thing in new_things:
        await thing.delete_from_queue()

    print("deleted all the messages we got from the queue")
    pprint(new_things)


if __name__ == "__main__":
    asyncio.run(main())
