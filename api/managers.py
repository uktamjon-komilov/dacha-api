from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **kwargs):
        if not phone or not password:
            raise ValueError(_("Phone and password fields are required"))

        user = self.model(phone=phone, **kwargs)
        user.set_password(password)
        user.save()

        return user
    

    def create_superuser(self, phone, password):
        user = self.create_user(phone, password)
        user.is_admin = True
        user.is_superuser = True
        user.save()

        return user