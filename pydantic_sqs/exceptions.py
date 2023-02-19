class PydanticSQSError(Exception):
    pass


class MsgNotFoundError(PydanticSQSError):
    pass


class NotRegisteredError(PydanticSQSError):
    pass


class MessageNotInQueueError(PydanticSQSError):
    pass


class InvalidMessageInQueueError(PydanticSQSError):
    pass


class ModelAlreadyRegisteredError(PydanticSQSError):
    pass
