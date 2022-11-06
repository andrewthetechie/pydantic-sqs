import json

import pytest
import pytest_asyncio
from aiobotocore.session import get_session
from pydantic import conint
from pydantic_sqs import exceptions
from pydantic_sqs import SQSModel
from pydantic_sqs import SQSQueue


@pytest.mark.asyncio
async def test_queue_not_registered(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    test = ThisModel(test="test")
    with pytest.raises(exceptions.NotRegisteredError):
        await test.to_sqs()


@pytest.mark.asyncio
async def test_queue_deletion_errors(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    test = ThisModel(test="test")
    with pytest.raises(exceptions.MessageNotInQueueError):
        await test.delete_from_queue()
    localstack_queue[0].register_model(ThisModel)
    await test.to_sqs()
    from_sqs = await localstack_queue[0].from_sqs()
    await from_sqs[0].delete_from_queue()
    with pytest.raises(exceptions.MessageNotInQueueError):
        await from_sqs[0].delete_from_queue()


@pytest.mark.asyncio
async def test_queue_wont_reregister_model(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    localstack_queue[0].register_model(ThisModel)
    with pytest.raises(exceptions.ModelAlreadyRegisteredError):
        localstack_queue[0].register_model(ThisModel)


@pytest.mark.asyncio
async def test_init_queue():
    queue_url = "http://testurl"
    aws_region = "us-test-1"
    visibility_timeout = 45
    wait_time_seconds = 20
    max_messages = 5
    endpoint_url = "http://localhost"
    use_ssl = True
    queue = SQSQueue(
        queue_url=queue_url,
        aws_region=aws_region,
        visibility_timeout=visibility_timeout,
        wait_time_seconds=wait_time_seconds,
        max_messages=max_messages,
        endpoint_url=endpoint_url,
        use_ssl=use_ssl,
    )

    assert queue.queue_url == queue_url
    assert queue.aws_region == aws_region
    assert queue.visibility_timeout == visibility_timeout
    assert queue.wait_time_seconds == wait_time_seconds
    assert queue.max_messages == max_messages
    assert endpoint_url == endpoint_url
    assert use_ssl


@pytest.mark.asyncio
async def test_queue_client_kwargs():
    queue_url = "http://testurl"
    aws_region = "us-test-1"
    visibility_timeout = 45
    wait_time_seconds = 20
    max_messages = 5
    endpoint_url = "http://localhost"
    use_ssl = True
    queue = SQSQueue(
        queue_url=queue_url,
        aws_region=aws_region,
        visibility_timeout=visibility_timeout,
        wait_time_seconds=wait_time_seconds,
        max_messages=max_messages,
        endpoint_url=endpoint_url,
        use_ssl=use_ssl,
    )
    kwargs = queue.client_kwargs
    assert kwargs["region_name"] == aws_region
    assert kwargs["use_ssl"] == use_ssl
    assert kwargs["endpoint_url"] == endpoint_url


@pytest.mark.asyncio
async def test_queue_invalid_message(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    localstack_queue[0].register_model(ThisModel)
    test_model = ThisModel(test="test")
    await test_model.to_sqs()

    localstack_queue[0].models = {}

    with pytest.raises(exceptions.InvaidMessageInQueueError):
        await localstack_queue[0].from_sqs()


@pytest.mark.asyncio
async def test_queue_invalid_message_ignored(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    localstack_queue[0].register_model(ThisModel)
    test_model = ThisModel(test="test")
    await test_model.to_sqs()

    empty_list = await localstack_queue[0].from_sqs(ignore_unknown=True)
    len(empty_list) == 0


parameters = [
    (
        pytest.lazy_fixture("localstack_queue"),
        json.dumps({"test": "test", "constrained": 5}),
        exceptions.InvaidMessageInQueueError,
    ),
    (
        pytest.lazy_fixture("localstack_queue"),
        "{Im invalid json:",
        exceptions.InvaidMessageInQueueError,
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("ls_queue, message, exception", parameters)
async def test_invalid_message_in_queue(ls_queue, message, exception):
    class ThisModel(SQSModel):
        test: str
        constrained: conint(gt=3)

    queue = ls_queue[0]
    session = ls_queue[1]
    client_kwargs = ls_queue[2]
    queue.register_model(ThisModel)
    send_kwargs = {
        "QueueUrl": queue.queue_url,
        "MessageBody": json.dumps(
            {
                "model": "thismodel",
                "message": message,
            }
        ),
    }

    async with session.create_client("sqs", **client_kwargs) as client:
        response = await client.send_message(**send_kwargs)
    with pytest.raises(exception):
        await queue.from_sqs()
