import json

import pytest
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


def test_queue_client_kwargs():
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


def test_queue_client_kwargs_no_endpoint():
    queue_url = "http://testurl"
    aws_region = "us-test-1"
    visibility_timeout = 45
    wait_time_seconds = 20
    max_messages = 5
    use_ssl = False
    queue = SQSQueue(
        queue_url=queue_url,
        aws_region=aws_region,
        visibility_timeout=visibility_timeout,
        wait_time_seconds=wait_time_seconds,
        max_messages=max_messages,
        use_ssl=use_ssl,
    )
    kwargs = queue.client_kwargs
    assert kwargs["region_name"] == aws_region
    assert kwargs["use_ssl"] == use_ssl
    assert kwargs.get("endpoint_url") is None


def test_queue_gets_session_if_none(mocker):
    from pydantic_sqs import queue as sqs_queue
    from aiobotocore.session import get_session

    session = get_session()

    mocker.patch("pydantic_sqs.queue.get_session")
    queue_url = "http://testurl"
    aws_region = "us-test-1"
    visibility_timeout = 45
    wait_time_seconds = 20
    max_messages = 5
    use_ssl = False
    sqs_queue.get_session.return_value = session
    _ = SQSQueue(
        queue_url=queue_url,
        aws_region=aws_region,
        visibility_timeout=visibility_timeout,
        wait_time_seconds=wait_time_seconds,
        max_messages=max_messages,
        use_ssl=use_ssl,
    )
    assert sqs_queue.get_session.called


def test_queue_session_passed(mocker):
    from pydantic_sqs import queue as sqs_queue
    from aiobotocore.session import get_session

    session = get_session()

    mocker.patch("pydantic_sqs.queue.get_session")
    queue_url = "http://testurl"
    aws_region = "us-test-1"
    visibility_timeout = 45
    wait_time_seconds = 20
    max_messages = 5
    use_ssl = False
    _ = SQSQueue(
        queue_url=queue_url,
        aws_region=aws_region,
        visibility_timeout=visibility_timeout,
        wait_time_seconds=wait_time_seconds,
        max_messages=max_messages,
        use_ssl=use_ssl,
        session=session,
    )
    assert not sqs_queue.get_session.called


@pytest.mark.asyncio
async def test_queue_invalid_message(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    localstack_queue[0].register_model(ThisModel)
    test_model = ThisModel(test="test")
    await test_model.to_sqs()

    localstack_queue[0].models = {}

    with pytest.raises(exceptions.InvalidMessageInQueueError):
        await localstack_queue[0].from_sqs()


@pytest.mark.asyncio
async def test_queue_invalid_message_ignored(localstack_queue):
    class ThisModel(SQSModel):
        test: str

    localstack_queue[0].register_model(ThisModel)
    test_model = ThisModel(test="test")
    await test_model.to_sqs()

    empty_list = await localstack_queue[0].from_sqs(ignore_unknown=True)
    assert len(empty_list) == 0


parameters = [
    (
        pytest.lazy_fixture("localstack_queue"),
        json.dumps({"test": "test", "constrained": 5}),
        exceptions.InvalidMessageInQueueError,
    ),
    (
        pytest.lazy_fixture("localstack_queue"),
        "{Im invalid json:",
        exceptions.InvalidMessageInQueueError,
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
        _ = await client.send_message(**send_kwargs)
    with pytest.raises(exception):
        await queue.from_sqs()


@pytest.mark.asyncio
async def test_get_messages_msg_not_found(localstack_queue):
    from pydantic_sqs.exceptions import MsgNotFoundError

    queue = localstack_queue[0]
    recv_kwargs = queue._SQSQueue__recv_kwargs(
        max_messages=1, visibility_timeout=1, wait_time_seconds=0
    )
    with pytest.raises(MsgNotFoundError):
        await queue._get_messages(recv_kwargs=recv_kwargs)


@pytest.mark.asyncio
async def test_get_messages_msg_found(localstack_queue):
    import json

    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)

    test_model = ThisModel(test="test")
    await test_model.to_sqs()

    recv_kwargs = queue._SQSQueue__recv_kwargs(
        max_messages=1, visibility_timeout=1, wait_time_seconds=0
    )

    response = await queue._get_messages(recv_kwargs=recv_kwargs)

    assert len(response) == 1
    response_data = json.loads(response[0]["Body"])
    assert response_data["message"]["test"] == "test"


@pytest.mark.asyncio
async def test_get_messages_msgs_found(localstack_queue):
    """Tests if there are multiple messages in the queue"""
    import json

    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)

    words = ["this", "that", "theother"]
    for word in words:
        await ThisModel(test=word).to_sqs()

    recv_kwargs = queue._SQSQueue__recv_kwargs(
        max_messages=3, visibility_timeout=1, wait_time_seconds=0
    )
    responses = await queue._get_messages(recv_kwargs=recv_kwargs)

    assert len(responses) == 3
    for response in responses:
        response_data = json.loads(response["Body"])
        assert response_data["message"]["test"] in words


def test__message_to_object_validation_error(localstack_queue):
    from pydantic_sqs.exceptions import InvalidMessageInQueueError

    class ThisModel(SQSModel):
        test: int

    queue = localstack_queue[0]

    queue.register_model(ThisModel)
    with pytest.raises(InvalidMessageInQueueError):
        queue._SQSQueue__message_to_object(
            message={
                "model": ThisModel.__qualname__.lower(),
                "message": {"test": "abc"},
            },
            message_id="test",
            receipt_handle="test",
            attributes={"test": "test"},
        )


@pytest.mark.asyncio
async def test_from_sqs_bad_json(localstack_queue, mocker):
    """Tests that we get an InvalidMessageInQueueError when there is bad json"""
    from pydantic_sqs.exceptions import InvalidMessageInQueueError
    import json

    class ThisModel(SQSModel):
        test: int

    queue = localstack_queue[0]
    queue.register_model(ThisModel)

    await ThisModel(test=1).to_sqs()

    with mocker.patch(
        "json.loads", side_effect=json.JSONDecodeError(msg="Test", doc="Test", pos=2)
    ):
        with pytest.raises(InvalidMessageInQueueError):
            await queue.from_sqs()


@pytest.mark.asyncio
async def test_from_sqs_bad_json_ignore_unknown(localstack_queue, mocker):
    """Tests that we get an InvalidMessageInQueueError when there is bad json"""
    import json

    class ThisModel(SQSModel):
        test: int

    queue = localstack_queue[0]
    queue.register_model(ThisModel)

    await ThisModel(test=1).to_sqs()

    with mocker.patch(
        "json.loads", side_effect=json.JSONDecodeError(msg="Test", doc="Test", pos=2)
    ):
        # test ignore_unknown works
        empty_list = await queue.from_sqs(ignore_unknown=True)
        assert len(empty_list) == 0


@pytest.mark.asyncio
async def test_from_sqs_msg_not_found(localstack_queue, mocker):
    """Tests we handle MsgNotFoundError"""
    from pydantic_sqs.exceptions import MsgNotFoundError

    queue = localstack_queue[0]
    messages = await queue.from_sqs(ignore_empty=True)
    assert len(messages) == 0

    with pytest.raises(MsgNotFoundError):
        await queue.from_sqs(ignore_empty=False)


def test_recv_kwargs(localstack_queue):
    queue = localstack_queue[0]
    recv_kwargs = queue._SQSQueue__recv_kwargs()
    assert recv_kwargs["MaxNumberOfMessages"] == 1
    assert "WaitTimeSeconds" not in recv_kwargs

    recv_kwargs = queue._SQSQueue__recv_kwargs(wait_time_seconds=21)
    assert recv_kwargs["WaitTimeSeconds"] == 20


@pytest.mark.asyncio
async def test_from_sqs_invalid_message_in_queue(localstack_queue):
    from pydantic_sqs.exceptions import InvalidMessageInQueueError
    from datetime import datetime

    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)
    await ThisModel(test="test").to_sqs()

    queue.models = {}

    class ThisModel(SQSModel):
        test: datetime

    queue.register_model(ThisModel)

    with pytest.raises(InvalidMessageInQueueError):
        await queue.from_sqs()


@pytest.mark.asyncio
async def test_from_sqs_invalid_message_in_queue_ignore_unknown(localstack_queue):
    from datetime import datetime

    class ThisModel(SQSModel):
        test: str

    queue = localstack_queue[0]
    queue.register_model(ThisModel)
    await ThisModel(test="test").to_sqs()

    queue.models = {}

    class ThisModel(SQSModel):
        test: datetime

    queue.register_model(ThisModel)

    messages = await queue.from_sqs(ignore_unknown=True)
    assert len(messages) == 0
