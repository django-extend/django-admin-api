from .auth import Authentication
from .pagination import PagePagination
from .core import get_passwords, ModelInfo
from .core import parse_model, get_short_description, get_field_title
from .core import has_model_attr
from . import log
from rest_framework import viewsets, serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.permissions import BasePermission
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.relations import PrimaryKeyRelatedField, ManyRelatedField
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.contrib.admin.options import ModelAdmin
from django.contrib import messages
from django.db import models
from django.db.models import fields

class GeneralMetadata(SimpleMetadata):
    _view = None
    def __init__(self):
        pass
    def _get_filters(self, view):
        admin = view._admin
        list_filter = []
        for key in admin.list_filter:
            field = admin.opts.get_field(key)
            title = field.verbose_name
            choices = field.choices
            if not choices:
                choices = []
                t = type(field)
                if t == fields.related.ManyToManyField:
                    for k, v in field.get_choices():
                        if k:
                            choices.append((k, v))
                elif t == fields.BooleanField:
                    choices = (
                        (1, '是'),
                        (0, '否'),
                    )
            list_filter.append({
                'key': key,
                'label': title,
                'choices': choices,
            })
        search_fields = []
        for key in admin.search_fields:
            field = admin.opts.get_field(key)
            title = field.verbose_name
            search_fields.append({
                'key': key,
                'label': title,
            })
        rs = {
            'listFilter': list_filter,
            'searchFields': search_fields,
        }
        return rs

    def _patch_input_type(self, field, data):
        def is_password_type(admin, fieldname):
            for name, _ in admin.passwords:
                if name == fieldname:
                    return True
            return False
        try:
            source = self._view._admin.opts.get_field(field.source)
            if source.default != fields.NOT_PROVIDED:
                default = source.default
                if callable(default):
                    default = default()
                data['default'] = default
        except:
            pass
        if is_password_type(self._view._admin, field.source):
            data['input_type'] = 'password'
        elif 'base_template' in field.style:
            if field.style['base_template'] == 'textarea.html':
                data['input_type'] = 'textarea'

    def determine_metadata(self, request, view):
        self._view = view
        data = SimpleMetadata.determine_metadata(self, request, view)
        data['fieldsets'] = view._admin.get_fieldsets(request)
        data['addFieldsets'] = view._admin.add_fieldsets
        data['filters'] = self._get_filters(view)
        data['pageSize'] = self._view._admin.list_per_page
        return data

    def get_field_info(self, field):
        data = SimpleMetadata.get_field_info(self, field)
        data['write_only'] = field.write_only
        self._patch_input_type(field, data)
        if isinstance(field, PrimaryKeyRelatedField):
            from .sites import site
            model = field.queryset.model
            info: ModelInfo = parse_model(model)
            relation = {
                'app': info.app_name,
                'model': info.model_name,
                'lazy': False, # 如果关联模型设置了search_fields则使用autocomplete懒加载，否则全部显示，阅读前端代码ForeignSelect.vue实现
            }
            admin = site._registry.get(model)
            if admin and admin.search_fields:
                relation['lazy'] = True
            data['relation'] = relation
            data['field_type'] = 'ManyToOne'
        elif isinstance(field, ManyRelatedField):
            data['choices'] = field.get_choices()
            data['field_type'] = 'ManyToMany'
        elif isinstance(field, fields.DecimalField):
            data['decimal_places'] = field.decimal_places
        return data

class GeneralPermission(BasePermission):
    perms_map = {
        'GET': 'view',
        'OPTIONS': '',
        'HEAD': '',
        'POST': 'add',
        'PUT': 'change',
        'PATCH': 'change',
        'DELETE': 'delete',
    }
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
    
    def has_permission(self, request, view):
        action = self.perms_map.get(request.method)
        if not action:
            return True
        attrname = f'has_{action}_permission'
        return getattr(view._admin, attrname)(request)

class GeneralSerializer(serializers.ModelSerializer):
    _admin: ModelAdmin = None
    @property
    def request(self):
        return self.context['request']
    
    def _del_file(self, instance):
        def filter_del_keys():
            prefix = '__del__'
            rs = []
            for key in self.initial_data.keys():
                if key.find(prefix) != 0:
                    continue
                rs.append(key[len(prefix):])
            return rs
        for key in filter_del_keys():
            # 删除文件
            field = getattr(instance, key)
            field.delete(save=False)
    def _set_password(self, validated_data):
        passwords = get_passwords(self._admin)
        for k in validated_data.keys():
            if k not in passwords:
                continue
            func = passwords[k]
            if not callable(func):
                func = getattr(self._admin, func)
            validated_data[k] = func(validated_data, validated_data[k])
    def update(self, instance, validated_data):
        def modify_fields():
            rs = []
            for k, v in validated_data.items():
                oldv = getattr(instance, k)
                if oldv != v:
                    rs.append(k)
            return rs
        self._del_file(instance)
        self._set_password(validated_data)
        fields = modify_fields()
        obj = serializers.ModelSerializer.update(self, instance, validated_data)
        message = []
        if len(fields) > 0:
            item = {
                'changed': {
                'fields': fields,
                }
            }
            message.append(item)
        log.log_change(self.request, obj, message)
        return obj
    
    def create(self, validated_data):
        self._set_password(validated_data)
        obj = serializers.ModelSerializer.create(self, validated_data)
        message = [{'added': {}}]
        log.log_addition(self.request, obj, message)
        return obj
    

class GeneralListSerializer(serializers.ModelSerializer):
    _admin: ModelAdmin = None
    
    def _get_admin_attr_value(self, attr_name, obj):
        if has_model_attr(self._admin, attr_name):
            return getattr(obj, attr_name)()
        return getattr(self._admin, attr_name)(obj)

        
class GeneralViewSet(viewsets.ModelViewSet):
    _admin: ModelAdmin = None
    list_serializer_class = None
    view_serializer_class = None
    autocomplete_serializer_class = None
    pagination_class = PagePagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    metadata_class = GeneralMetadata
    authentication_classes = [Authentication,]
    permission_classes = [GeneralPermission,]
    
 
    def _inner_delete(self, request, queryset):
        for obj in queryset:
            log.log_deletion(request, obj, str(obj))
        count, _ = queryset.delete()
        message = f'{count}条记录被删除'
        self._admin.message_user(request, message, messages.SUCCESS)
    
    def _call_admin_action(self, name, request):
        if 'all' in request.data:
            queryset = self.get_queryset()
        else:
            ids = request.data.get('ids', [])
            queryset = self.get_queryset().filter(pk__in=ids)
        if name == 'delete':
            func = self._inner_delete
        else:
            func = getattr(self._admin, name)
        func(request, queryset)
        msgs = []
        for msg in messages.get_messages(request):
            msgs.append({'level': msg.level, 'message': msg.message})
        
        return Response({'status': 0, 'message': msgs})
    
    @property
    def _model(self) -> models.Model:
        return self.serializer_class.Meta.model
    
    @property
    def _slots(self):
        if not hasattr(self._admin, 'slots'):
            return {}
        rs = {}
        for k, v in self._admin.slots.items():
            if isinstance(v, str):
                path = v
                params = {}
            else:
                path, params = v
            rs[k] = (path, params)
        return rs
    
    def _get_actions(self, request):
        actions = []
        origin_actions = self._admin.get_actions(request)
        if origin_actions != None:
            if self._admin.has_delete_permission(request):
                actions.append({'name': '删除', 'action': 'action_delete'})
            for item in origin_actions:
                if not hasattr(self._admin, item):
                    continue
                name = get_short_description(self._admin, item)
                actions.append({'name': name, 'action': f'action_{item}'})
        return {
            'items': actions,
            'onTop': self._admin.actions_on_top,
            'onButton': self._admin.actions_on_bottom,
            'showSelection': self._admin.actions_selection_counter
        }
    
    @property
    def _columns(self):
        rs = []
        for field in self._admin.list_display:
            if field == 'pk':
                continue
            column = {
                'title': get_field_title(self._admin, field),
                'dataIndex': field,
            }
            if field in self._slots:
                column['scopedSlots'] = {'customRender': field}
            rs.append(column)
        return rs
    
    def list(self, request, *args, **kwargs):
        self.serializer_class = self.list_serializer_class
        data = viewsets.ModelViewSet.list(self, request, *args, **kwargs)
        data.data['columns'] = self._columns
        data.data['slots'] = self._slots
        data.data['actions'] = self._get_actions(request)
        return data

    @action(detail=False)
    def autocomplete(self, request, *args, **kwargs):
        self.serializer_class = self.autocomplete_serializer_class
        return viewsets.ModelViewSet.list(self, request, *args, **kwargs)
    
    @action(detail=True)
    def view(self, request, *args, **kwargs):
        self.serializer_class = self.view_serializer_class
        return viewsets.ModelViewSet.retrieve(self, request, *args, **kwargs)
    
    @action(detail=True)
    def str(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'str': instance.__str__()})
    
    def perform_destroy(self, instance):
        log.log_deletion(self.request, instance, str(instance))
        viewsets.ModelViewSet.perform_destroy(self, instance)
