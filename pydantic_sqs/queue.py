"""Module containing the queue classes."""
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from aiobotocore.session import AioSession
from aiobotocore.session import get_session
from pydantic import AnyUrl
from pydantic import conint
from pydantic import ValidationError
from pydantic_sqs import exceptions
from pydantic_sqs.abstract import _AbstractQueue
from pydantic_sqs.model import SQSModel


class SQSQueue(_AbstractQueue):
    """A SQS queue that can send/receive messages from SQS and parse them into pydantic modules."""

    models: Dict[str, type(SQSModel)] = {}
    session: AioSession = None
    # The duration (in seconds) that the received messages are hidden from subsequent retrieve
    # requests after being retrieved by a from_sqs request
    visibility_timeout: int = None

    # The duration (in seconds) for which the call waits for a message to arrive in the queue before
    # returning. If a message is available, the call returns sooner than WaitTimeSeconds .
    # If no messages are available and the wait time expires, the call returns successfully with an empty
    # list of messages.
    wait_time_seconds: conint(ge=0, le=20) = None

    # The maximum number of messages to return. Amazon SQS never returns more messages than
    # this value (however, fewer messages might be returned).
    max_messages: conint(gt=0, le=10) = None

    # Endpoint_url - a custom endpoint to use with aiobotocore. Useful for testing with localstack
    endpoint_url: AnyUrl = None

    # Whether or not to use SSL for the aws client. Useful for testing with localstack
    use_ssl: bool = True

    def __init__(
        self,
        queue_url: str,
        aws_region: str = "us-east-1",
        session: AioSession = None,
        visibility_timeout: int = None,
        wait_time_seconds: conint(ge=0, le=20) = None,  # type: ignore
        max_messages: conint(gt=0, le=10) = 1,  # type: ignore
        endpoint_url: AnyUrl = None,
        use_ssl: bool = True,
        **data: Any,
    ):
        """Args:

        queue_url (str): Url of the AWS SQS queue (or compatible) aws_region (str, optional): The AWS region for this
        queue. Defaults to "us-east-1". session (AioSession, optional): An aiobotocore session. Defaults to None. If
        none is provided, a new one will be created. visibility_timeout (int, optional): The duration (in seconds) that
        the received messages are hidden from subsequent retrieve requests after being retrieved by a from_sqs request.
        Defaults to None. wait_time_seconds (conint, optional): The duration (in seconds) for which the call waits for
        a message to arrive in the queue before returning. If a message is available, the call returns sooner than
        WaitTimeSeconds . If no messages are available and the wait time expires, the call returns successfully with an
        empty list of messages. Defaults to None. Greater than0, less than or equal to 20 max_messages (conint,
        optional):  The maximum number of messages to return. Amazon SQS never returns more messages than this value
        (however, fewer messages might be returned).. Defaults to 1. Greater than 0, less than 10 endpoint_url (AnyUrl,
        optional): a custom endpoint to use with aiobotocore. Useful for testing with localstack. Defaults to None.
        use_ssl (bool, optional): Whether or not to use SSL for the aws client. Useful for testing with localstack.
        Defaults to True.
        """
        if session is None:
            session = get_session()

        super().__init__(
            queue_url=queue_url,
            aws_region=aws_region,
            session=session,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
            max_messages=max_messages,
            endpoint_url=endpoint_url,
            use_ssl=use_ssl,
            **data,
        )

    def register_model(self, model_class: SQSModel):
        """Add a model to this SQS queue.

        A queue can handle multiple models, but only one queue per model.  Args:     model_class (SQSModel): The model
        class to register
        """
        model_name = model_class.__qualname__.lower()
        if model_name in self.models.keys():
            raise exceptions.ModelAlreadyRegisteredError(
                f"{model_class.__qualname__} is already registered to {model_class._queue.queue_url}"
            )
        model_class._queue = self
        self.models[model_class.__qualname__.lower()] = model_class

    @property
    def client_kwargs(self) -> Dict[str, Any]:
        """Returns a dict of kwargs for use with the AWS client.

        Returns:     dict[str, Any]: kwargs for constructing an aiobotocore client
        """
        kwargs = {"region_name": self.aws_region, "use_ssl": self.use_ssl}
        if self.endpoint_url is not None:
            kwargs["endpoint_url"] = self.endpoint_url

        return kwargs

    def __recv_kwargs(
        self,
        max_messages: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        __recv_kwargs - Get kwargs for recieving from sqs
        """
        recv_kwargs = {}
        recv_kwargs["MaxNumberOfMessages"] = max_messages if max_messages is not None else self.max_messages

        recv_kwargs["VisibilityTimeout"] = (
            visibility_timeout if visibility_timeout is not None else getattr(self, "visibility_timeout", None)
        )
        if recv_kwargs["VisibilityTimeout"] is None:
            del recv_kwargs["VisibilityTimeout"]

        recv_kwargs["WaitTimeSeconds"] = (
            wait_time_seconds if wait_time_seconds is not None else getattr(self, "wait_time_seconds", None)
        )
        if recv_kwargs["WaitTimeSeconds"] is None:
            del recv_kwargs["WaitTimeSeconds"]
        else:
            if recv_kwargs["WaitTimeSeconds"] > 20:
                # max wait time is 20 seconds
                recv_kwargs["WaitTimeSeconds"] = 20

        recv_kwargs["QueueUrl"] = self.queue_url
        return recv_kwargs

    async def from_sqs(
        self,
        max_messages: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: Optional[int] = None,
        ignore_empty: bool = False,
        ignore_unknown: bool = False,
    ) -> List[Optional["SQSModel"]]:
        """from_sqs - gets messages from the queue and parses them into pydantic models.

        Args:
            max_messages (int, optional): The maximum number of messages to return. Amazon SQS never returns more
                messages than this value (however, fewer messages might be returned). Defaults to None.
            visibility_timeout (int, optional): The duration (in seconds) that the received messages are hidden
                from subsequent retrieve requests after being retrieved by a from_sqs request. Defaults to None.
            wait_time_seconds (int, optional): The duration (in seconds) for which the call waits for a message to
                arrive in the queue before returning. If a message is available, the call returns sooner than
                WaitTimeSeconds . If no messages are available and the wait time expires, the call returns
                successfully with an empty list of messages. Defaults to None.
            ignore_empty (bool, optional): Whether or not to ignore an empty queue. Defaults to False. If True,
                an empty queue will return an empty list and not raise a MsgNotFoundError
            ignore_unknown (bool, optional): Whether or not to ignore unknown messages. Defaults to False.
                If true, unknown messages will not raise an InvalidMessageInQueueError and will simply return to the
                queue after their visibility timeout
        Raises:
            exceptions.MsgNotFoundError: If no messages are found in the queue
            exceptions.InvalidMessageInQueueError: If an unknown message is found in the queue.

        Returns:
            list[SQSModel]: A list of SQSModels from the queue
        """
        recv_kwargs = self.__recv_kwargs(
            max_messages=max_messages,
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds,
        )

        to_return = []

        try:
            messages = await self._get_messages(recv_kwargs)
        except exceptions.MsgNotFoundError as exc:
            if ignore_empty:
                messages = []
            else:
                raise exc

        for msg in messages:
            try:
                this_object = json.loads(msg["Body"])
                to_return.append(
                    self.__message_to_object(
                        message=this_object,
                        message_id=msg["MessageId"],
                        receipt_handle=msg["ReceiptHandle"],
                        attributes=msg.get("Attributes", None),
                    )
                )
            except json.JSONDecodeError as exc:
                if ignore_unknown:
                    continue
                raise exceptions.InvalidMessageInQueueError(f"Message {msg['MessageId']} is not valid JSON") from exc
            except exceptions.InvalidMessageInQueueError as exc:
                if ignore_unknown:
                    continue
                raise exc

        return to_return

    def __message_to_object(
        self,
        message: Dict[str, Any],
        message_id: str,
        receipt_handle: str,
        attributes: Dict[str, str],
    ) -> "SQSModel":
        """
        Converts a SQS object to the pydantic model that represents it.

        Args:
            message (dict[str, Any]): _description_

        Raises:
            exceptions.InvalidMessageInQueueError: _description_

        Returns:
            SQSModel: _description_
        """
        try:
            model = self.models[message["model"]]
        except KeyError:
            raise exceptions.InvalidMessageInQueueError(
                f"No model registered to queue {self.queue_url} for model "
                + f"type {message['model']} from {message_id}"
            ) from None

        try:
            return model(
                message_id=message_id,
                receipt_handle=receipt_handle,
                attributes=attributes,
                **message["message"],
            )
        except ValidationError as exc:
            raise exceptions.InvalidMessageInQueueError(
                f"Invalid message {message_id} from queue {self.queue_url}"
            ) from exc

    async def _get_messages(
        self,
        recv_kwargs: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Get messages from SQS queue

        Args:
            recv_kwargs (dict[str, Any]): _description_

        Raises:
            exceptions.MsgNotFoundError: _description_

        Returns:
            _type_: _description_
        """
        async with self.session.create_client("sqs", **self.client_kwargs) as client:
            response = await client.receive_message(**recv_kwargs)

        messages = response.get("Messages", [response.get("Message", None)])
        if messages[0] is None:
            raise exceptions.MsgNotFoundError(f"{self.queue_url} is empty")

        return messages
