"""Module containing the model classes"""
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from pydantic_sqs import exceptions
from pydantic_sqs.abstract import _AbstractModel


class SQSModel(_AbstractModel):
    """
    A SQSModel is a pydantic model that can be sent to and from SQS.

    By registering a model with a SQSQueue, you can then send and receive messages of that type from that SQS queue.
    They will automatically be converted to and from JSON. You can also delete them from the queue after you've
    processed them.
    """

    message_id: str = None  # type: ignore
    receipt_handle: str = None  # type: ignore
    attributes: Dict[str, str] = None  # type: ignore
    deleted: bool = False

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @classmethod
    def __get_queue(cls) -> _AbstractModel:
        """
        Get the queue that this model is registered to

        Raises:
            NotRegisteredError: Raised if this model is not registered to a queue

        Returns:
            SQSQueue: The queue this model is registered with
        """
        try:
            return cls._queue
        except AttributeError:
            raise exceptions.NotRegisteredError(
                f"{cls.__qualname__} not registered to a queue"
            ) from None

    @classmethod
    async def from_sqs(
        cls,
        max_messages: Optional[int] = None,
        visibility_timeout: Optional[int] = None,
        wait_time_seconds: Optional[int] = None,
        ignore_empty: bool = True,
    ) -> List[Optional["SQSModel"]]:
        """from_sqs - gets this model from the queue

        Args:
            max_messages (int, optional): The maximum number of messages to return. Amazon SQS never returns more
                messages than this value (however, fewer messages might be returned). Defaults to None.
            visibility_timeout (int, optional): The duration (in seconds) that the received messages are hidden
                from subsequent retrieve requests after being retrieved by a from_sqs request. Defaults to None.
            wait_time_seconds (int, optional): The duration (in seconds) for which the call waits for a message to
                arrive in the queue before returning. If a message is available, the call returns sooner than
                WaitTimeSeconds . If no messages are available and the wait time expires, the call returns
                successfully with an empty list of messages. Defaults to None.
            ignore_empty (bool, optional): Whether or not to ignore an empty queue. Defaults to True. If True,
                an empty queue will return an empty list and not raise a MsgNotFoundError
        Raises:
            exceptions.MsgNotFoundError: If no messages are found in the queue and ignore_empty is set to False

        Returns:
            list[SQSModel]: A list of SQSModels from the queue
        """
        queue = cls.__get_queue()
        results = await queue.from_sqs(
            max_messages,
            visibility_timeout,
            wait_time_seconds,
            ignore_empty,
            ignore_unknown=True,
        )
        return [result for result in results if isinstance(result, cls)]

    def __send_kwargs(
        self, queue_url: str, wait_time_in_seconds: int = None
    ) -> Dict[str, Any]:
        """
        Create the send kwargs

        Args:
            wait_time_in_seconds (int, optional): The length of time, in seconds, for which to delay a specific message.
                Valid values: 0 to 900. Maximum: 15 minutes. Messages with a positive DelaySeconds value become
                available for processing after the delay period is finished. If you don't specify a value, the
                default value for the queue applies. Defaults to None. Greater than 0, less than or equal to 900

        Returns:
            Dict[str, Any]: send kwargs
        """
        send_kwargs = {}
        if wait_time_in_seconds is not None:
            if wait_time_in_seconds < 0:
                wait_time_in_seconds = 0
            if wait_time_in_seconds > 900:
                wait_time_in_seconds = 900
            send_kwargs["DelaySeconds"] = wait_time_in_seconds

        send_kwargs["QueueUrl"] = queue_url
        send_kwargs["MessageBody"] = json.dumps(
            {
                "model": self.__class__.__qualname__.lower(),
                "message": self.dict(exclude_unset=True),
            }
        )
        return send_kwargs

    async def to_sqs(self, wait_time_in_seconds: int = None) -> None:
        """
        Send this object to SQS.
        Well set this object's message_id to the message id rom SQS

        Args:
            wait_time_in_seconds (int, optional): The length of time, in seconds, for which to delay a specific message.
                Valid values: 0 to 900. Maximum: 15 minutes. Messages with a positive DelaySeconds value become
                available for processing after the delay period is finished. If you don't specify a value, the
                default value for the queue applies. Defaults to None. Greater than 0, less than or equal to 900
        """
        queue = self.__get_queue()

        send_kwargs = self.__send_kwargs(
            queue_url=queue.queue_url, wait_time_in_seconds=wait_time_in_seconds
        )
        async with queue.session.create_client("sqs", **queue.client_kwargs) as client:
            response = await client.send_message(**send_kwargs)

        self.message_id = response["MessageId"]

    async def delete_from_queue(self):
        """
        Delete this object from SQS.
        This is good to do after you've confirmed a message in your worker, or SQS will re-deliver
        the message after the visibility timeout

        Sets this object's deleted attribute to True
        Raises:
            MessageNotInQueueError: Raised when the message is not in the queue or has already been deleted
        """
        if self.receipt_handle is None:
            raise exceptions.MessageNotInQueueError(
                f"{str(self)} does not have a receipt_handle so it was not pulled from SQS and cannot be deleted"
            )
        if self.deleted:
            raise exceptions.MessageNotInQueueError(
                f"{str(self)} has already been deleted"
            )
        queue = self.__get_queue()
        session = queue.session
        async with session.create_client("sqs", **queue.client_kwargs) as client:
            await client.delete_message(
                QueueUrl=queue.queue_url, ReceiptHandle=self.receipt_handle
            )
        self.deleted = True
