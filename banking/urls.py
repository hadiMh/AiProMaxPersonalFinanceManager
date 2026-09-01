from django.urls import path

from banking import transfer_views, views

app_name = "banking"

urlpatterns = [
    path("cards/", views.BankCardListView.as_view(), name="card_list"),
    path("cards/create/", views.BankCardCreateView.as_view(), name="card_create"),
    path("cards/<int:pk>/", views.BankCardDetailView.as_view(), name="card_detail"),
    path("cards/<int:pk>/edit/", views.BankCardUpdateView.as_view(), name="card_edit"),
    path("transfers/", transfer_views.TransferListView.as_view(), name="transfer_list"),
    path("transfers/create/", transfer_views.TransferCreateView.as_view(), name="transfer_create"),
    path("transfers/<int:pk>/edit/", transfer_views.TransferUpdateView.as_view(), name="transfer_edit"),
    path("transfers/<int:pk>/delete/", transfer_views.TransferDeleteView.as_view(), name="transfer_delete"),
]
