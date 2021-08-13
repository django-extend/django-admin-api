from django.db.models import CharField
from .core import set_password

class PasswordField(CharField):
    def __init__(self, *args, **kwargs):
        self.method = kwargs.pop('method', set_password)
        super().__init__(*args, **kwargs)