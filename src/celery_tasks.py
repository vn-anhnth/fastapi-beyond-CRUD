from celery import Celery
from asgiref.sync import async_to_sync
from src.mail import create_message, mail
from src.config import Config

c_app = Celery('tasks')
# c_app.config_from_object("src.config")
c_app.conf.update(
    # Redis connection settings
    broker_url=Config.REDIS_URL,  # URL for Redis broker (where tasks are queued)
    result_backend=Config.REDIS_URL,  # URL for storing task results
    broker_connection_retry_on_startup=True,  # Retry connecting to broker on startup

    # Serialization settings
    task_serializer='json',  # How to serialize tasks
    accept_content=['json'],  # What content types to accept
    result_serializer='json',  # How to serialize results

    # Timezone settings
    timezone='UTC',  # Set timezone to UTC
    enable_utc=True,  # Enable UTC timezone

    # Task event settings
    worker_send_task_events=True,  # Enable worker to send task events
    task_send_sent_event=True,  # Send event when task is sent
    task_track_started=True,  # Track when task starts

    # Task execution limits
    task_time_limit=30,  # Hard time limit for tasks (seconds)
    task_soft_time_limit=20,  # Soft time limit for tasks (seconds)

    # Worker settings
    worker_prefetch_multiplier=1,  # Number of tasks to prefetch per worker
    worker_max_tasks_per_child=200,  # Max tasks before worker process is replaced

    # Task result settings
    task_ignore_result=False,  # Don't ignore task results
    task_store_errors_even_if_ignored=True,  # Store errors even if results are ignored
    task_always_eager=False,  # Don't execute tasks synchronously

    # Redis connection settings
    redis_socket_timeout=30,  # Socket timeout for Redis operations
    redis_socket_connect_timeout=30,  # Connection timeout for Redis
    redis_retry_on_timeout=True,  # Retry on Redis timeout
    redis_max_connections=20,  # Max Redis connections per worker
)

@c_app.task()
def send_email(recipients: list[str], subject: str, body: str) -> None:
    message = create_message(recipients, subject, body)
    async_to_sync(mail.send_message)(message)
    print('Email sent!')
