import os
import random
import string

import docker
import pytest_asyncio
from aiobotocore.session import get_session
from pydantic_sqs import SQSQueue


@pytest_asyncio.fixture(scope="session", name="localstack_container")
def create_localstack_container(unused_tcp_port_factory):
    """Runs a localstack container for use with testing"""
    port1 = unused_tcp_port_factory()
    port2 = unused_tcp_port_factory()
    try:
        client = docker.from_env()
        container = client.containers.run(
            f"localstack/localstack:{os.environ.get('LOCALSTACK_IMAGE_TAG', 'latest')}",
            ports={"4566/tcp": port1, "4571/tcp": port2},
            detach=True,
        )
        yield f"http://localhost:{port1}/", port2
    finally:
        container.remove(force=True)


@pytest_asyncio.fixture(name="localstack_sqs_client_args")
async def create_localstack_sqs_client(localstack_container):
    endpoint_url = localstack_container[0]
    session = get_session()
    client_kwargs = {
        "region_name": "us-east-1",
        "use_ssl": False,
        "endpoint_url": endpoint_url,
    }
    yield session, client_kwargs


@pytest_asyncio.fixture(name="localstack_queue")
async def create_localstack_queue(localstack_sqs_client_args):
    """Creates a queue in localstack for use with testing"""
    session = localstack_sqs_client_args[0]
    client_kwargs = localstack_sqs_client_args[1]
    queue_name = "".join(
        random.choices(string.ascii_uppercase + string.ascii_lowercase, k=8)
    )
    async with session.create_client("sqs", **client_kwargs) as client:
        response = await client.create_queue(QueueName=queue_name)
        queue = SQSQueue(
            response["QueueUrl"],
            endpoint_url=client_kwargs["endpoint_url"],
            use_ssl=False,
        )
        yield queue, session, client_kwargs
