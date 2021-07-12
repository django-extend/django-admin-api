def register(*models):
    from .sites import site
    def _wrapper(admin_class):
        site.register(models, admin_class)
        return admin_class
    return _wrapper