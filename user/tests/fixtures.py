import factory

from datetime import datetime

from user.models import UserProfile


class UserFactory(factory.Factory):
    class Meta:
        model = UserProfile

    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    date_joined = factory.LazyFunction(datetime.datetime.now)
    password = "12345"
