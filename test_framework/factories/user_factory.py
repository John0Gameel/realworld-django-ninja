import factory
import factory.fuzzy
import string
from accounts.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    class Params:
        mail_domain = factory.fuzzy.FuzzyText(length=5, chars=string.ascii_lowercase)

    username = factory.Faker("user_name")
    email = factory.LazyAttribute(lambda o: f"{o.username}@{o.mail_domain}.com")
    password = "secret123"
    bio = factory.fuzzy.FuzzyText(length=50)
    image = factory.Faker("url")
