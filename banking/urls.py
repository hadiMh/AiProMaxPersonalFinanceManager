from django.urls import path

from banking import views

app_name = "banking"

urlpatterns = [
    path("cards/", views.BankCardListView.as_view(), name="card_list"),
    path("cards/create/", views.BankCardCreateView.as_view(), name="card_create"),
    path("cards/<int:pk>/", views.BankCardDetailView.as_view(), name="card_detail"),
    path("cards/<int:pk>/edit/", views.BankCardUpdateView.as_view(), name="card_edit"),
]
