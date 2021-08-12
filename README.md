简体中文 | [English](./README.en-US.md)

----

# 版本要求

* Python (3.5, 3.6, 3.7, 3.8, 3.9)
* Django (2.2, 3.0, 3.1, 3.2)

# 第一步: 安装

使用`pip`安装...

    pip install django-admin-api


# 第二步: 创建一个简单项目

```bash
django-admin startproject example
cd example
./manage.py migrate
./manage.py createsuperuser
```

`INSTALLED_APPS` 加入如下依赖.
```python
# example/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'django_filters',
    'admin_api',
]
```

# 第三步: 输出API接口
```python
# example/urls.py
...
import admin_api
urlpatterns = [
  ...
  path('api/', admin_api.site.urls),
]
```

# 前端框架列表

框架 | 设备 | 项目
---|---|---
ant-design(vue) | 桌面端 | [antd-django](https://github.com/django-extend/antd-django.git)
element(vue) | 桌面端 | [element-django](https://github.com/django-extend/element-django.git)
vant(vue) | 移动端 | [vant-django](https://github.com/django-extend/vant-django.git)

后端项目创建完成以后，移步到前端框架项目中...

