from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException, status


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Incorrect authentication credentials.')
    default_code = 'authentication_failed'
