import httpx
import asyncio

n8n_url = "http://localhost:5678/webhook-test/4b91437d-be26-434b-9910-85117640ed84"

async def send_automation_request(request_body):
    async with httpx.AsyncClient() as client:
        res = await client.post(url=n8n_url, json=request_body)
        return res
