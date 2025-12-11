from django.conf import settings
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """Abstract base for timestamp fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Message(TimestampedModel):
    """Email message template."""

    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
    )

    class Meta:
        ordering = ('-created_at',)
        permissions = (
            ('view_all_messages', 'Can view all messages (manager)'),
        )

    def __str__(self) -> str:
        return self.subject


class Recipient(TimestampedModel):
    """Mailing recipient."""

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
    )

    class Meta:
        ordering = ('full_name',)
        permissions = (
            ('view_all_recipients', 'Can view all recipients (manager)'),
        )

    def __str__(self) -> str:
        return f'{self.full_name} <{self.email}>'


class Mailing(TimestampedModel):
    """Mailing campaign."""

    STATUS_CREATED = 'Создана'
    STATUS_RUNNING = 'Запущена'
    STATUS_FINISHED = 'Завершена'
    STATUS_CHOICES = (
        (STATUS_CREATED, STATUS_CREATED),
        (STATUS_RUNNING, STATUS_RUNNING),
        (STATUS_FINISHED, STATUS_FINISHED),
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings')
    recipients = models.ManyToManyField(Recipient, related_name='mailings')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
    )

    class Meta:
        ordering = ('-start_time',)
        permissions = (
            ('view_all_mailings', 'Can view all mailings (manager)'),
            ('can_disable_mailings', 'Can disable foreign mailings (manager)'),
        )

    def __str__(self) -> str:
        return f'Рассылка #{self.pk}'

    @property
    def is_active(self) -> bool:
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def update_status(self, save: bool = True):
        """Recalculate status based on current time."""
        now = timezone.now()
        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_RUNNING
        else:
            new_status = self.STATUS_FINISHED

        if new_status != self.status:
            self.status = new_status
            if save:
                self.save(update_fields=['status'])

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError('Дата начала должна быть раньше даты окончания.')
        if self.start_time and self.start_time < timezone.now():
            raise ValidationError('Дата начала не может быть в прошлом.')


class MailingAttempt(models.Model):
    """Single attempt to send mailing to a recipient."""

    STATUS_SUCCESS = 'Успешно'
    STATUS_FAILED = 'Не успешно'
    STATUS_CHOICES = (
        (STATUS_SUCCESS, STATUS_SUCCESS),
        (STATUS_FAILED, STATUS_FAILED),
    )

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name='attempts',
        null=True,
        blank=True,
    )
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)

    class Meta:
        ordering = ('-attempt_time',)
        permissions = (
            ('view_all_attempts', 'Can view all mailing attempts (manager)'),
        )

    def __str__(self) -> str:
        return f'Попытка рассылки {self.mailing_id} - {self.get_status_display()}'
