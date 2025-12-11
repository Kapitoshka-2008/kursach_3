from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing
from mailings.services import send_mailing


class Command(BaseCommand):
    help = 'Отправить рассылки вручную'

    def add_arguments(self, parser):
        parser.add_argument('--mailing-id', type=int, help='ID конкретной рассылки')

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')
        qs = Mailing.objects.all()
        if mailing_id:
            qs = qs.filter(pk=mailing_id)
        else:
            now = timezone.now()
            qs = qs.filter(
                start_time__lte=now,
                end_time__gte=now,
            ).exclude(status=Mailing.STATUS_FINISHED)

        for mailing in qs:
            sent, error = send_mailing(mailing)
            if error:
                self.stdout.write(self.style.WARNING(f'Рассылка #{mailing.pk}: {error}'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Рассылка #{mailing.pk}: отправлено {sent} писем')
                )
