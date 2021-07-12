from setuptools import setup

def read(f):
    return open(f, 'r', encoding='utf-8').read()

setup(
    name='django-admin-api',
    version='0.0.1',
    packages=['admin_api'],
    zip_safe=False,
    include_package_data=True,
    license='BSD License',  # example license
    description='export Django Admin API by restful style',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/django-extend/django-admin-api.git',
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
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)