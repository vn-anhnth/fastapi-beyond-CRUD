from celery import Celery
from asgiref.sync import async_to_sync
from src.mail import create_message, mail
from src.config import Config

c_app = Celery('tasks')
# c_app.config_from_object("src.config")
c_app.conf.update(
    broker_url=Config.REDIS_URL,
    result_backend=Config.REDIS_URL,
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_track_started=True,
    task_time_limit=30,
    task_soft_time_limit=20,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=200,
    # Persist task results and events
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    task_always_eager=False,
    # Redis result backend settings
    redis_socket_timeout=30,
    redis_socket_connect_timeout=30,
    redis_retry_on_timeout=True,
    redis_max_connections=20,
    # Flower settings
    flower_persistent=True,
    flower_db=Config.REDIS_URL,
    flower_port=5555,
    flower_basic_auth=['admin:admin'],  # Optional: Add basic auth
    flower_url_prefix='flower',  # Optional: Add URL prefix
)

@c_app.task()
def send_email(recipients: list[str], subject: str, body: str) -> None:
    message = create_message(recipients, subject, body)
    async_to_sync(mail.send_message)(message)
    print('Email sent!')
