from arq.connections import RedisSettings

from src.routes.whatsapp_route import process_whatsapp_message


class WorkerSettings:
    functions = [process_whatsapp_message]
    redis_settings = RedisSettings(host="localhost", port=6379, database=0)

    @staticmethod
    async def on_startup(ctx):
        print("Worker started...")
        pass

    @staticmethod
    async def on_shutdown(ctx):
        print("Worker stopped...")
        pass
