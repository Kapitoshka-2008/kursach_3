from django.urls import path

from mailings import views

urlpatterns = [
    path('', views.MailingListView.as_view(), name='mailing_list'),
    path('create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('<int:pk>/edit/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('<int:pk>/send/', views.MailingSendView.as_view(), name='mailing_send'),

    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path(
        'messages/<int:pk>/edit/',
        views.MessageUpdateView.as_view(),
        name='message_update',
    ),
    path(
        'messages/<int:pk>/delete/',
        views.MessageDeleteView.as_view(),
        name='message_delete',
    ),

    path('recipients/', views.RecipientListView.as_view(), name='recipient_list'),
    path('recipients/create/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipients/<int:pk>/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    path(
        'recipients/<int:pk>/edit/',
        views.RecipientUpdateView.as_view(),
        name='recipient_update',
    ),
    path(
        'recipients/<int:pk>/delete/',
        views.RecipientDeleteView.as_view(),
        name='recipient_delete',
    ),

    path('attempts/', views.AttemptListView.as_view(), name='attempt_list'),
    path('report/', views.ReportView.as_view(), name='report'),
]
