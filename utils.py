import httpx

class FileUtil():
    def convert_bytes(self, bytes: int) -> str:
        file_size = 0
        pow = 1
        sizes = ["B", "KB", "MB", "GB"]

        while True:
            if bytes < 1024:
                file_size = bytes
                break
            if bytes / (1024 ** pow) < 1:
                break
            file_size = bytes / (1024 ** pow)
            pow += 1

        return f"{file_size:.2f} {sizes[pow - 1]}"

class WebhookClient():
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def get_attachment_bytes(self, message_id: int) -> bytes:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.webhook_url}/messages/{message_id}")
            data = await client.get(res.json()["attachments"][0]["url"])

            await client.aclose()

            return data.content