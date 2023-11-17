import datetime

from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta, datetime
from mailing.models import Mailing, Log


def send_mailings():
    current_datetime = datetime.now()
    for mailing in Mailing.objects.filter(status='created'):
        is_mailing = False
        emails = [client.email for client in mailing.recipients.all()]
        month_start = mailing.start_time.month
        day_start = mailing.start_time.day
        hour_start = mailing.start_time.hour
        min_start = mailing.start_time.minute
        attempt_status = 'success'
        server_response = 'Email sent successfully'
        messages = mailing.message_set.all()

        if mailing.frequency == 'daily' and day_start == current_datetime.day \
                and current_datetime.hour == hour_start and current_datetime.minute == min_start:
            mailing.start_time = mailing.start_time + timedelta(days=1)
            is_mailing = True

        elif mailing.frequency == 'weekly' and day_start == current_datetime.day \
                and current_datetime.hour == hour_start and current_datetime.minute == min_start:
            mailing.start_time = mailing.start_time + timedelta(days=7)
            is_mailing = True

        elif mailing.frequency == 'monthly' and month_start == current_datetime.month \
                and day_start == current_datetime.day \
                and current_datetime.hour == hour_start and current_datetime.minute == min_start:
            mailing.start_time = mailing.start_time + timedelta(days=30)
            is_mailing = True

        if is_mailing:
            mailing.save()
            for message in messages:
                try:

                    send_mail(
                        subject=message.subject,
                        message=message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=emails
                    )

                except Exception as e:

                    attempt_status = 'error'
                    server_response = str(e)

                finally:

                    Log.objects.create(message=message,
                                       status=attempt_status,
                                       response=server_response)
