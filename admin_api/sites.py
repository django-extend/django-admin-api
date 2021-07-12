from .viewsets import GeneralViewSet, GeneralListSerializer, GeneralSerializer
from . import auth
from .core import parse_model, has_model_attr, ModelInfo
from rest_framework.routers import SimpleRouter
from rest_framework import serializers
from django.urls.conf import path
from rest_framework.decorators import MethodMapper
from dataclasses import field
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields.reverse_related import ManyToOneRel

class DefaultSite():
    router: SimpleRouter
    actions = {}
    def __init__(self, name='admin-api'):
        self._registry = {} # ModelAdmin内部get_fieldset会使用
        self.name = name
        self.router = SimpleRouter(trailing_slash=True)
        
    @property
    def urls(self):
        urlpatterns =  self.router.urls
        urlpatterns += (
            path('auth/login/', auth.login),
            path('auth/logout/', auth.logout),
            path('auth/userinfo/', auth.user_info),
        )
        return urlpatterns, 'admin-api', self.name
    
    def _patch_password_fields(self, admin, args):
        for name, _ in admin.passwords:
            if admin.fields and name not in admin.fields:
                continue
            field = admin.model._meta.get_field(name)
            args[name] = serializers.CharField(write_only=True, label=field.verbose_name)

    def _gen_admin_class(self, model, admin_class):
        from django.contrib.auth.models import User
        admin_class = type('',(admin_class,), {})
        if model == User:
            # 官方的新增写法不标准（password1, password2），按drf协议修正一下
            admin_class.add_fieldsets = ((None, {'fields': ('username', 'password')}),)
            # 官方UserAdmin为了显示新增页面覆盖了get_fieldsets， 这里需要修正一下
            admin_class.get_fieldsets = eval('lambda self, request: self.fieldsets')
            # 实现一下生成密码的方法
            def set_password(_, rawPassword):
                from django.contrib.auth.hashers import make_password
                return make_password(rawPassword)
            admin_class.passwords = (('password',set_password),)
        for name in ('add_fieldsets', 'passwords'):
            if hasattr(admin_class, name):
                continue
            setattr(admin_class, name, ())
        return admin_class(model, self)
    
    def _build_list_serialize_class(self, admin):
        args = {
            'pk': serializers.CharField(),
        }
        if not isinstance(admin.list_display, str):
            for attr_name in admin.list_display:
                if attr_name.startswith('__'):
                    continue
                if has_model_attr(admin, attr_name) or hasattr(admin, attr_name):
                    args[attr_name] = serializers.SerializerMethodField()
                    args[f'get_{attr_name}'] = eval(f'lambda self, obj: self._get_admin_attr_value("{attr_name}", obj)')
        serializer_class = type('', (GeneralListSerializer, ), args)
        serializer_class._admin = admin
        serializer_class.Meta = type('', (), {})
        serializer_class.Meta.model = admin.model
        if admin.list_display == '__all__':
            serializer_class.Meta.fields = '__all__'
        else:
            serializer_class.Meta.fields = ['pk']
            serializer_class.Meta.fields.extend(admin.list_display)
        return serializer_class
    
    def _build_autocomplete_serialize_class(self, admin):
        args = {
            'key': serializers.CharField(source='pk'),
            'label': serializers.CharField(source='__str__')
        }
        serializer_class = type('', (GeneralListSerializer, ), args)
        serializer_class.Meta = type('', (), {})
        serializer_class.Meta.model = admin.model
        serializer_class.Meta.fields = ('key', 'label')
        return serializer_class
    
    def _build_view_serialize_class(self, admin):
        args = {
        }
        self._patch_password_fields(admin, args)
        for field in admin.opts.get_fields():
            t = type(field)
            if t in (ManyToManyField, ManyToOneRel):
                args[field.name] = serializers.StringRelatedField(many=True)
            elif t in (ForeignKey,):
                args[field.name] = serializers.StringRelatedField(many=False)
        serializer_class: serializers.ModelSerializer = type('', (GeneralSerializer, ), args)
        serializer_class._admin = admin
        serializer_class.Meta = type('', (), {})
        serializer_class.Meta.model = admin.model
        serializer_class.Meta.fields = admin.fields if admin.fields else '__all__'
        return serializer_class
        
    
    def _build_serialize_class(self, admin):
        args = {
        }
        self._patch_password_fields(admin, args)
        serializer_class: serializers.ModelSerializer = type('', (GeneralSerializer, ), args)
        serializer_class._admin = admin
        serializer_class.Meta = type('', (), {})
        serializer_class.Meta.model = admin.model
        serializer_class.Meta.fields = admin.fields if admin.fields else '__all__'
        return serializer_class
    
    
    def _build_actions(self, viewset_class):
        def insert_bulk_action(name):
            def innerfunc(self: GeneralViewSet, request):
                return self._call_admin_action(name, request)
            innerfunc.__name__ = f'action_{name}'
            innerfunc.mapping = MethodMapper(innerfunc, methods=('post',))
            innerfunc.detail = False
            innerfunc.url_path = innerfunc.__name__
            innerfunc.url_name = innerfunc.__name__.replace('_', '-')
            innerfunc.kwargs = {}
            setattr(viewset_class, innerfunc.__name__, innerfunc)
        actions = viewset_class._admin.actions
        if actions is None:
            return
        insert_bulk_action('delete')
        for name in actions:
            insert_bulk_action(name)
    
    def perms(self, request):
        def perm_list(admin):
            actions = []
            for action, perm in admin.get_model_perms(request).items():
                if perm:
                    actions.append(action)
            return actions 
        rs = {}
        for model, admin in self._registry.items():
            info: ModelInfo = parse_model(model)
            if not request.user.has_module_perms(info.app_name):
                continue
            actions = perm_list(admin)
            if len(actions) == 0:
                continue
            if info.app_name not in rs:
                rs[info.app_name] = {
                    'label': info.app_label,
                    'models': []
                }
            rs[info.app_name]['models'].append((model, actions))
        return rs

    def register(self, models, admin_class):
        if not isinstance(models, list) and not isinstance(models, tuple):
            models = [models]
                    
        for model in models:
            admin = self._gen_admin_class(model, admin_class)
            info: ModelInfo = parse_model(model)
            viewset_classname = f'{info.model_name}ViewSet'
            viewset_class: GeneralViewSet = type(viewset_classname, (GeneralViewSet,), {})
            viewset_class.queryset = model.objects.all()
            viewset_class.search_fields = admin.search_fields
            viewset_class.filterset_fields = admin.list_filter
            viewset_class._admin = admin
            viewset_class.list_serializer_class = self._build_list_serialize_class(admin)
            viewset_class.autocomplete_serializer_class = self._build_autocomplete_serialize_class(admin)
            viewset_class.serializer_class = self._build_serialize_class(admin)
            viewset_class.view_serializer_class = self._build_view_serialize_class(admin)
            self._build_actions(viewset_class)
            self._registry[model] = admin
            self.router.register(info.prefix, viewset_class)

site = DefaultSite()