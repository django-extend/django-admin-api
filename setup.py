from setuptools import setup
setup(
    name='django-admin-api',
    version='0.0.1',
    packages=['admin_api'],
    zip_safe=False,
    include_package_data=True,
    license='BSD License',  # example license
    description='export Django Admin API by restful style',
    url='https://github.com/nieoding/django-admin-api',
    author='Nieo Ding',
    author_email='8285770@qq.com',
    install_requires = [
        'djangorestframework',
        'django-filter',
        'pyjwt',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 3 - Alpha'
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)