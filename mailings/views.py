from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from django.conf import settings

from mailings.forms import MailingForm, MessageForm, RecipientForm
from mailings.models import Mailing, MailingAttempt, Message, Recipient
from mailings.services import send_mailing


class ManagerMixin:
    """Helper to detect manager role."""

    def is_manager(self) -> bool:
        user = getattr(self, 'request', None).user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()
        )


class OwnerQuerySetMixin(ManagerMixin):
    """Filter QuerySet by owner unless manager."""

    def get_queryset(self):
        qs = super().get_queryset()
        if self.is_manager():
            return qs
        return qs.filter(owner=self.request.user)


class OwnerOnlyQuerySetMixin:
    """Restrict QuerySet strictly to current owner."""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerFormMixin:
    """Assign owner on form save."""

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


@method_decorator(cache_page(60), name='get')
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        total_mailings = Mailing.objects.count()
        active_mailings = Mailing.objects.filter(
            status=Mailing.STATUS_RUNNING,
            start_time__lte=now,
            end_time__gte=now,
        ).count()
        unique_recipients = Recipient.objects.values('email').distinct().count()
        context['stats'] = {
            'total_mailings': total_mailings,
            'active_mailings': active_mailings,
            'unique_recipients': unique_recipients,
        }
        return context


class MessageListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(LoginRequiredMixin, OwnerQuerySetMixin, DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin, OwnerFormMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')


class MessageUpdateView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')


class MessageDeleteView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')


class RecipientListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'


class RecipientDetailView(LoginRequiredMixin, OwnerQuerySetMixin, DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, OwnerFormMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')


class RecipientUpdateView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')


class RecipientDeleteView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')


class MailingListView(LoginRequiredMixin, OwnerQuerySetMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


class MailingDetailView(LoginRequiredMixin, OwnerQuerySetMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, OwnerFormMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingUpdateView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class MailingDeleteView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')


class MailingSendView(LoginRequiredMixin, OwnerOnlyQuerySetMixin, View):
    """Trigger mailing send manually."""

    def post(self, request, pk):
        mailing = get_object_or_404(self.get_queryset(), pk=pk)
        sent, error = send_mailing(mailing)
        if error:
            messages.error(request, error)
        elif sent:
            messages.success(request, f'Рассылка отправлена, писем: {sent}')
        else:
            messages.warning(request, 'Рассылка не отправлена или истекла.')
        return redirect(reverse('mailings:mailing_detail', args=[pk]))


class AttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailings/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        qs = super().get_queryset().select_related('mailing', 'recipient')
        if self.request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists():
            return qs
        return qs.filter(mailing__owner=self.request.user)


@method_decorator(cache_page(60), name='get')
class ReportView(LoginRequiredMixin, TemplateView):
    template_name = 'mailings/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_filter = Q()
        if not self.request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists():
            base_filter &= Q(mailing__owner=self.request.user)

        attempts = MailingAttempt.objects.filter(base_filter)
        stats = attempts.aggregate(
            total=Count('id'),
            success=Count('id', filter=Q(status=MailingAttempt.STATUS_SUCCESS)),
            failed=Count('id', filter=Q(status=MailingAttempt.STATUS_FAILED)),
        )
        context['stats'] = stats
        context['attempts'] = attempts.select_related('mailing', 'recipient')[:100]
        return context
