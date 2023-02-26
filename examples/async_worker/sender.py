import asyncio
import os
from uuid import uuid4

from models import AsyncTask


async def main():
    sleep_time = float(os.environ.get("SENDER_SLEEP", "5"))
    counter = 0
    while True:
        new_task = AsyncTask(uuid=str(uuid4()), message=f"This is message {counter}")
        print(new_task)
        await new_task.to_sqs()
        counter += 1
        print(f"Sleeping {sleep_time} seconds")
        await asyncio.sleep(sleep_time)


if __name__ == "__main__":
    asyncio.run(main())
