from django.urls import path

from mailing.apps import MailingConfig
from .views import MailingCreateView, MailingDetailView, MessageCreateView, ClientListView, MailingListView, HomeView, \
    DeliveryReportView, MailingDeleteView, ClientCreateView, MailingUpdateView

from django.views.decorators.cache import cache_page
app_name = MailingConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('mailing/', MailingListView.as_view(), name='mailing'),
    path('create_mailing/', MailingCreateView.as_view(), name='create_mailing'),
    path('mailing/delete/<int:pk>/', MailingDeleteView.as_view(), name='delete_mailing'),
    path('mailing/update/<int:pk>/', MailingUpdateView.as_view(), name='update_mailing'),
    path('mailing/<int:pk>/', cache_page(60)(MailingDetailView.as_view()), name='mailing_detail'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='create_client'),
    path('mailing/<int:mailing_pk>/create_message/', MessageCreateView.as_view(), name='create_message'),
    path('delivery_report/', cache_page(60)(DeliveryReportView.as_view()), name='delivery_report'),
]