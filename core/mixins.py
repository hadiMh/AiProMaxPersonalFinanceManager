from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404


class UserOwnedMixin(LoginRequiredMixin):
    user_field = "user"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.user_field: self.request.user})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if getattr(obj, self.user_field) != self.request.user:
            raise Http404
        return obj
