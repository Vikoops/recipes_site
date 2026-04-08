
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username
        if not email or not password:
            return None

        users = UserModel._default_manager.filter(Q(email__iexact=email))
        if not users.exists():
            return None
        if users.count() > 1:
            return None

        user = users.first()
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
