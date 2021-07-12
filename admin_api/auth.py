from rest_framework.decorators import authentication_classes, permission_classes,\
    api_view
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.response import Response
import traceback
from .exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import jwt
from rest_framework.authentication import BaseAuthentication,\
    get_authorization_header
from django.utils.translation import gettext as _
from rest_framework import HTTP_HEADER_ENCODING


def create_token(user, **payload):
    salt = settings.SECRET_KEY
    headers = {
        "typ": "jwt_",
        "alg": "HS256",
    }
    payload['user_id'] = user.id
    payload['username'] = user.username
    payload['exp'] = timezone.now() + timedelta(days=1)
    return jwt.encode(payload=payload, key=salt, headers=headers)

def parse_token(source):
    from django.contrib.auth.models import User
    token = jwt.decode(source, settings.SECRET_KEY, algorithms=["HS256"])
    user = User.objects.get(id=token['user_id'])
    return (user, token)

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        from django.contrib.auth.models import User
        user = request.user
        return bool(user and
                    isinstance(user, User) and
                    user.is_staff and user.is_active)

class Authentication(BaseAuthentication):
    keyword = 'bearer'

    def authenticate(self, request):
        auth_header = get_authorization_header(request)
        auth_header = auth_header.decode(HTTP_HEADER_ENCODING)
        auth = auth_header.split()
        if not auth or auth[0].lower() != self.keyword:
            raise AuthenticationFailed()
        token = auth[1]
        try:
            user, token = parse_token(token)
            return (user, token)
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationFailed(detail='签名失效')
        except jwt.exceptions.DecodeError:
            raise AuthenticationFailed(detail='验证失败')
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed(detail='非法token')

    def authenticate_header(self, _):
        return self.keyword

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    try:
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if not user:
            raise Exception('验证失败')
        result = {
            'token': create_token(user)
        }
        return Response({'result': result})
    except Exception as e:
        traceback.print_exc()
        raise AuthenticationFailed(detail=str(e))

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def logout(request):
    return Response({})

@api_view(['GET'])
@authentication_classes([Authentication])
@permission_classes([IsAdminUser])
def user_info(request):
    def format_permission_id(model):
        meta = model._meta
        return f'{meta.app_label}-{meta.model_name}'
    from .sites import site
    user = request.user
    perms = site.perms(request)
    permissions = [
        {
            'permissionId': 'dashboard'
        }
    ]
    for app, app_info in perms.items():
        for model, actions in app_info['models']:
            if len(actions) == 0:
                continue
            permission = {
                'permissionId': format_permission_id(model),
                'actionList': actions,
            }
            permissions.append(permission)
    menus = [
        {
            'name': 'dashboard',
            'key': 'dashboard',
            'component': '/views/Dashboard',
            'meta': {
                'icon': 'dashboard',
                'title': _('Site administration'),
            }
        }
    ]
    for app, app_info in perms.items():
        nav = {
            'name': app,
            'key': app,
            'component': 'RouteView',
            'meta': {
                'title': app_info['label']
            },
            'children': [],
        }
        for model, actions in app_info['models']:
            if len(actions) == 0:
                continue
            nav['children'].append({
                'name': model._meta.label.lower(),
                'key': model._meta.model_name.lower(),
                'component': '/components/Django',
                'meta': {
                    'title': model._meta.verbose_name,
                    'permission': format_permission_id(model),
                }
            })
        menus.append(nav)
    result = {
        'id': user.id,
        'username': user.username,
        'role': {
            'permissions': permissions
        },
        'menus': menus
    }
    return Response({'result': result})
