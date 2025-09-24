import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DicoEvent.settings")

app = Celery("DicoEvent")
app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
app.autodiscover_tasks()
