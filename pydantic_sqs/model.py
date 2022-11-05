"""Module containing the model classes"""
import json
from typing import Dict

from pydantic_sqs import exceptions
from pydantic_sqs.abstract import _AbstractModel


class SQSModel(_AbstractModel):
    """
    A SQSModel is a pydantic model that can be sent to and from SQS.

    By registering a model with a SQSQueue, you can then send and receive messages of that type from that SQS queue.
    They will automatically be converted to and from JSON. You can also delete them from the queue after you've processed them.
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
            if cls._queue is None:
                raise exceptions.NotRegisteredError(
                    f"{cls.__qualname__} not registered to a queue"
                ) from None
        except AttributeError:
            raise exceptions.NotRegisteredError(
                f"{cls.__qualname__} not registered to a queue"
            ) from None
        return cls._queue

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
        session = queue.session

        send_kwargs = {}
        if wait_time_in_seconds is not None:
            if wait_time_in_seconds < 0:
                wait_time_in_seconds = 0
            if wait_time_in_seconds > 900:
                wait_time_in_seconds = 900
            send_kwargs["DelaySeconds"] = wait_time_in_seconds

        send_kwargs["QueueUrl"] = queue.queue_url
        send_kwargs["MessageBody"] = json.dumps(
            {
                "model": self.__class__.__qualname__.lower(),
                "message": self.dict(exclude_unset=True),
            }
        )
        async with session.create_client("sqs", **queue.client_kwargs) as client:
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
