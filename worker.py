from rq import Worker

from src import config
from src.queue import whatsapp_queue

if __name__ == "__main__":
    worker = Worker(queues=[whatsapp_queue], connection=config.redis_conn)

    @worker.on_startup
    def on_start(worker):
        print(f"👷 Worker {worker.name} started, listening on {worker.queue_names()}")

    @worker.on_success
    def on_success(job, result, *args, **kwargs):
        print(f"✅ Job {job.id} finished successfully with result: {result}")

    @worker.on_failure
    def on_failure(job, exc_type, exc_value, traceback):
        print(f"❌ Job {job.id} failed: {exc_value}")

    worker.work()
