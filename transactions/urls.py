from django.urls import path

from transactions import views

app_name = "transactions"

urlpatterns = [
    path("transactions/", views.TransactionListView.as_view(), name="list"),
    path("transactions/create/", views.TransactionCreateView.as_view(), name="create"),
    path("transactions/<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="edit"),
    path("transactions/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
    path("transactions/api/categories/", views.categories_by_type, name="categories_by_type"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
]
