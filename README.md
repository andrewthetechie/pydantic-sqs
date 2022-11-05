# pydantic-sqs

Convert your pydantic models to and from AWS SQS messages.

<p align="center">
    <a href="https://github.com/andrewthetechie/pydantic-sqs" target="_blank">
        <img src="https://img.shields.io/github/last-commit/andrewthetechie/pydantic-sqs" alt="Latest Commit">
    </a>
    <img src="https://img.shields.io/badge/license-MIT-green">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/andrewthetechie/pydantic-sqs?label=Latest%20Release">
    <br />
    <a href="https://github.com/andrewthetechie/pydantic-sqs/issues"><img src="https://img.shields.io/github/issues/andrewthetechie/pydantic-sqs" /></a>
    <img alt="GitHub Workflow Status Test and Lint (branch)" src="https://img.shields.io/github/workflow/status/andrewthetechie/pydantic-sqs/Tests/main?label=Tests">
    <br />
    <a href="https://pypi.org/project/pydantic-sqs" target="_blank">
        <img src="https://img.shields.io/pypi/v/pydantic-sqs" alt="Package version">
    </a>
    <img src="https://img.shields.io/pypi/pyversions/pydantic-sqs">
</p>

## Main Dependencies

- [Python +3.7](https://www.python.org)
- [pydantic](https://github.com/samuelcolvin/pydantic/)
- [aiobotocore](https://github.com/aio-libs/aiobotocore)

## Getting Started

```python
from pydantic_sqs import SQSModel, SQSQueue
from pydantic import Field
import asyncio
from pprint import pprint
import os


class ThisModel(SQSModel):
    foo: str = Field(..., description="Foo")


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

    this_thing = ThisModel(foo="1234")
    that_thing = ThatModel(bar="5678")
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
```

### Examples

Examples are in the [examples/](./examples) directory of this repo.

### Installation

Install the package

    pip install pydantic-sqs

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide](./CONTRIBUTING.rst)

## License

Licensed under the [MIT License](./LICENSE)
