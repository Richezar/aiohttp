import asyncio
from aiohttp import ClientSession
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    async with ClientSession() as session:

        async with session.post(
            "http://127.0.0.1:8080/api/v1/advertisement",
            json={"title": "PS5", "description": "sell ps5", "owner": "Ivan"},

        ) as response:
            print(response.status)
            print(await response.text())

        async with session.get(
            "http://127.0.0.1:8080/api/v1/advertisement/1",
        ) as response:
            print(response.status)
            print(await response.text())

        async with session.delete(
            "http://127.0.0.1:8080/api/v1/advertisement/7",
        ) as response:
            print(response.status)
            print(await response.text())




asyncio.run(main())
