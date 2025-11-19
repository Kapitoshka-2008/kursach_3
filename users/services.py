from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django.conf import settings


def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_path = reverse('users:verify_email', kwargs={'uidb64': uid, 'token': token})
    verify_url = request.build_absolute_uri(verify_path)
    subject = 'Подтверждение регистрации'
    message = (
        'Здравствуйте!\n\n'
        'Для подтверждения регистрации перейдите по ссылке:\n'
        f'{verify_url}\n\n'
        'Если вы не создавали аккаунт, проигнорируйте это письмо.'
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

