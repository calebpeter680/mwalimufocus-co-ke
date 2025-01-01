from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        from .tasks import send_payment_reminders, restore_item_prices, send_emails_in_batches
        if not hasattr(self, 'scheduler'):
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_job(send_payment_reminders, 'interval', minutes=5, jitter=10)
            self.scheduler.add_job(restore_item_prices, 'interval', minutes=3, jitter=15)
            self.scheduler.add_job(send_emails_in_batches, 'interval', hours=1, jitter=15)
            self.scheduler.start()
