import asyncio
import os

from models import AsyncTask


async def main():
    poll_seconds = float(os.environ.get("WORKER_POLL", "1"))
    sleep_time = float(os.environ.get("WORKER_SLEEP", "10"))
    messages_per_cycle = int(os.environ.get("WORKER_MAX_MESSAGES", "2"))
    while True:
        incoming_tasks = await AsyncTask.from_sqs(
            max_messages=messages_per_cycle, wait_time_seconds=5
        )
        if len(incoming_tasks) > 0:
            for task in incoming_tasks:
                print(f"Deleting task: {task}")
                await task.delete_from_queue()
            print(f"Sleeping for {sleep_time} seconds to simulate long running work")
            await asyncio.sleep(sleep_time)
        else:
            print(f"No tasks found, sleeping {poll_seconds} before polling again")
            await asyncio.sleep(poll_seconds)


if __name__ == "__main__":
    asyncio.run(main())
