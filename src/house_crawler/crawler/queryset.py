from django.db.models import QuerySet, Manager


class BaseManager(Manager):
    def active(self):
        return self.filter(is_active=True)


class PostTokenManager(BaseManager):
    pass


class PostManager(BaseManager):
    pass
