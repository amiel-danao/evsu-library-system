from django.utils.html import strip_tags
from django.core.mail import get_connection, EmailMultiAlternatives
from smtplib import SMTPAuthenticationError, SMTPDataError
from django.core.management.base import BaseCommand
from django.db.models import Count
from datetime import timedelta, datetime
from django.utils.timezone import utc
from django.utils import timezone
import pytz
from system.models import OutgoingTransaction, Penalty
from django.conf import settings
from django.core.mail import send_mass_mail
import logging
from django.template.loader import render_to_string


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = timezone.now().replace(tzinfo=pytz.timezone(settings.TIME_ZONE))

        today = now.date()

        all_borrowed = OutgoingTransaction.objects.filter(paid=False)

        messages = []

        for borrowed in all_borrowed:
            day_difference = today - borrowed.return_date
            if day_difference.days > 0:
                penalty, _ = Penalty.objects.get_or_create(transaction=borrowed)
                total_penalty = borrowed.book.overtime_fine * day_difference.days
                penalty.unpaid_penalty = total_penalty
                penalty.save()

                context = {
                    'borrowed': borrowed,
                    'penalty': penalty
                }
                body_html = render_to_string(template_name='email/notify_penalty.html', context=context)
                body_text = strip_tags(body_html)
                messages.append((settings.EMAIL_PENALTY_SUBJECT, body_text, body_html, settings.DEFAULT_FROM_EMAIL, [borrowed.borrower.email,]))
            else:
                pass     # Still edible

        #send email batch
        try:
            # send_mass_mail(messages, fail_silently=False)
            self.send_mass_html_mail(messages)
            pass
        except SMTPDataError as error:
            logging.error(error)
        except SMTPAuthenticationError as error:
            logging.error(error)
        
    def send_mass_html_mail(self, datatuple, fail_silently=False, user=None, password=None, 
                        connection=None):
        """
        Given a datatuple of (subject, text_content, html_content, from_email,
        recipient_list), sends each message to each recipient list. Returns the
        number of emails sent.

        If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
        If auth_user and auth_password are set, they're used to log in.
        If auth_user is None, the EMAIL_HOST_USER setting is used.
        If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

        """
        connection = connection or get_connection(
            username=user, password=password, fail_silently=fail_silently)
        messages = []
        for subject, text, html, from_email, recipient in datatuple:
            message = EmailMultiAlternatives(subject, text, from_email, recipient)
            message.attach_alternative(html, 'text/html')
            messages.append(message)
        return connection.send_messages(messages)