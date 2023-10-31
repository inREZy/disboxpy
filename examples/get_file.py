import asyncio
from disboxpy import DisBox

client = DisBox("webhook_url")

async def main():
    print(await client.get_file_info(10611))
    print(await client.get_all_files("test folder"))
    print(await client.get_random_file())

if __name__ == "__main__":
    asyncio.run(main())