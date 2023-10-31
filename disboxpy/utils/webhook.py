import httpx

class WebhookClient():
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def get_attachment_bytes(self, message_id: int) -> bytes:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.webhook_url}/messages/{message_id}")
            data = await client.get(res.json()["attachments"][0]["url"])

            await client.aclose()

            return data.content