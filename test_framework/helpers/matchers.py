import re


class JWTTokenMatch:
    JWT_REGEX = re.compile(r"^[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+$")

    def __eq__(self, other):
        return isinstance(other, str) and bool(self.JWT_REGEX.match(other))


class DateTimeMatch:
    datetime = None

    def __init__(self, datetime):
        self.datetime = datetime

    def __eq__(self, other):
        pass
