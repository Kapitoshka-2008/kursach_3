from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt


def send_mailing(mailing: Mailing) -> tuple[int, str | None]:
    """
    Send mailing messages to all recipients.

    Returns (sent_count, error_message).
    """
    sent_count = 0
    now = timezone.now()

    if now < mailing.start_time:
        return sent_count, 'Рассылка еще не началась'
    if mailing.end_time < now:
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save(update_fields=['status'])
        return sent_count, 'Срок действия рассылки истек'

    mailing.status = Mailing.STATUS_RUNNING
    mailing.save(update_fields=['status'])

    recipients = mailing.recipients.all()
    for recipient in recipients:
        try:
            result = send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            status = MailingAttempt.STATUS_SUCCESS if result else MailingAttempt.STATUS_FAILED
            if result:
                sent_count += 1
            server_response = 'Sent' if result else 'No emails were sent'
        except Exception as exc:  # noqa: BLE001
            status = MailingAttempt.STATUS_FAILED
            server_response = str(exc)

        MailingAttempt.objects.create(
            mailing=mailing,
            recipient=recipient,
            status=status,
            server_response=server_response,
        )

    if timezone.now() > mailing.end_time:
        mailing.status = Mailing.STATUS_FINISHED
        mailing.save(update_fields=['status'])

    return sent_count, None
