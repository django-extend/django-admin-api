English | [简体中文](./README.zh-CN.md)

----

# Requirements

* Python (3.5, 3.6, 3.7, 3.8, 3.9)
* Django (2.2, 3.0, 3.1, 3.2)

# Step 1: Installation

Install using `pip`...

    pip install django-admin-api

Add  to your `INSTALLED_APPS` setting as followed.

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'django_filters',
        'admin_api',
    ]

# Step 2: Startup up a demo project

Startup up a new project like so...

    django-admin startproject example
    cd example
    ./manage.py migrate
    ./manage.py createsuperuser

# Step 3: export API with 'api' end-point

```python
# example/urls.py
...
import admin_api
urlpatterns = [
  ...
  path('api/', admin_api.site.urls),
]
```

# Frontend framework

framework | project
---|---
ant-design(vue) | [antd-django](https://github.com/django-extend/antd-django.git)

# helper links

helper | link
---|---
api detail | [document](api.md)

