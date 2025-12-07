import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        print("--- Requesting London ---")
        try:
            resp = await client.post("http://127.0.0.1:8000/chat", json={"message": "London"})
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
        except Exception as e:
            print(f"London Request Failed: {e}")

        print("\n--- Requesting Invalid City ---")
        try:
            resp = await client.post("http://127.0.0.1:8000/chat", json={"message": "ThisIsNotACityX123"})
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.json()}")
        except Exception as e:
            print(f"Invalid City Request Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
