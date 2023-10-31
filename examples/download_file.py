import asyncio
from disboxpy import DisBox

client = DisBox("webhook_url")

async def main():
    await client.download_file(10704, "test folder", "simple folder")
    await client.download_folder("test folder", True)

if __name__ == "__main__":
    asyncio.run(main())