import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from pydantic_sqs import exceptions
from pydantic_sqs import SQSModel
from pydantic_sqs import SQSQueue


@pytest.mark.asyncio
async def test_send_to_queue(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    session = localstack_queue[1]
    client_kwargs = localstack_queue[2]
    queue.register_model(ThisModel)
    test = ThisModel(test="test")
    await test.to_sqs()
    assert test.message_id is not None
    async with session.create_client("sqs", **client_kwargs) as client:
        response = await client.get_queue_attributes(
            QueueUrl=queue.queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )
    assert int(response["Attributes"]["ApproximateNumberOfMessages"]) > 0


@pytest.mark.asyncio
async def test_from_queue(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)
    test = ThisModel(test="test")
    await test.to_sqs()
    assert test.message_id is not None

    from_sqs = await queue.from_sqs()
    assert len(from_sqs) == 1
    assert from_sqs[0].test == "test"
    assert from_sqs[0].message_id == test.message_id
    assert from_sqs[0].receipt_handle is not None
    assert from_sqs[0].deleted is False


@pytest.mark.asyncio
async def test_from_queue_empty(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)

    with pytest.raises(exceptions.MsgNotFoundError):
        await queue.from_sqs()

    empty_list = await queue.from_sqs(ignore_empty=True)
    assert len(empty_list) == 0


@pytest.mark.asyncio
async def test_delete(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    session = localstack_queue[1]
    client_kwargs = localstack_queue[2]
    queue.register_model(ThisModel)
    test = ThisModel(test="test")
    await test.to_sqs()
    assert test.message_id is not None

    from_sqs = await queue.from_sqs()
    await from_sqs[0].delete_from_queue()
    assert from_sqs[0].deleted is True

    async with session.create_client("sqs", **client_kwargs) as client:
        response = await client.get_queue_attributes(
            QueueUrl=queue.queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )
    assert int(response["Attributes"]["ApproximateNumberOfMessages"]) == 0


@pytest.mark.asyncio
async def test_multiple_models_in_queue(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    class ThatModel(SQSModel):
        foo: str

    queue = localstack_queue[0]
    session = localstack_queue[1]
    client_kwargs = localstack_queue[2]
    queue.register_model(ThisModel)
    queue.register_model(ThatModel)
    test = ThisModel(test="test")
    test2 = ThatModel(foo="bar")
    await test.to_sqs()
    await test2.to_sqs()
    assert test.message_id is not None
    assert test2.message_id is not None
    async with session.create_client("sqs", **client_kwargs) as client:
        response = await client.get_queue_attributes(
            QueueUrl=queue.queue_url, AttributeNames=["ApproximateNumberOfMessages"]
        )
    assert int(response["Attributes"]["ApproximateNumberOfMessages"]) == 2

    from_sqs = await queue.from_sqs(max_messages=5)
    assert len(from_sqs) == 2
