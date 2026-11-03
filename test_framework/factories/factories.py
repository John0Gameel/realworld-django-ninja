import string

import factory
import factory.fuzzy

from test_framework.models import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.NewUser

    class Params:
        mail_domain = factory.fuzzy.FuzzyText(length=5, chars=string.ascii_lowercase)

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda o: f"{o.username}@{o.mail_domain}.com")
    password = factory.Faker("password")


class UsersPostRequestFactory(factory.Factory):
    class Meta:
        model = models.UsersPostRequest

    class Params:
        username = None
        email = None
        password = None

    user = factory.LazyAttribute(
        lambda o: UserFactory.build(
            **{
                k: v
                for k, v in (("email", o.email), ("username", o.username), ("password", o.password))
                if v is not None
            }
        )
    )


class LoginUserFactory(factory.Factory):
    class Meta:
        model = models.LoginUser

    email = factory.Faker("email")
    password = factory.Faker("password")


class UsersLoginPostRequestFactory(factory.Factory):
    class Meta:
        model = models.UsersLoginPostRequest

    class Params:
        email = None
        password = None

    user = factory.LazyAttribute(
        lambda o: LoginUserFactory.build(
            **{k: v for k, v in (("email", o.email), ("password", o.password)) if v is not None}
        ),
    )
