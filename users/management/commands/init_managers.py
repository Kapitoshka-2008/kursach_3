from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from django.conf import settings
from mailings.models import Mailing, MailingAttempt, Message, Recipient


class Command(BaseCommand):
    help = 'Создать группу менеджеров и назначить права'

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name=settings.MANAGER_GROUP_NAME)

        models_with_perms = [Mailing, MailingAttempt, Message, Recipient]
        perm_codenames = [
            'view_all_mailings',
            'can_disable_mailings',
            'view_all_attempts',
            'view_all_messages',
            'view_all_recipients',
        ]

        assigned = 0
        for model in models_with_perms:
            content_type = ContentType.objects.get_for_model(model)
            for codename in perm_codenames:
                perm = Permission.objects.filter(content_type=content_type, codename=codename).first()
                if perm:
                    group.permissions.add(perm)
                    assigned += 1

        self.stdout.write(self.style.SUCCESS(f'Группа "{group.name}" готова, назначено прав: {assigned}'))



