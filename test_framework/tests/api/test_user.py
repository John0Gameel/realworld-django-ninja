import pytest

from test_framework.constants.constants import ENDPOINT, REQUEST_RESPONSE_BODY_PATH
from test_framework.data_classes.api_login import APIDataClass
from test_framework.factories.factories import UserFactory, UsersLoginPostRequestFactory
from test_framework.helpers.data_manipulation import tweak
from test_framework.helpers.helper import assert_api_response
from test_framework.helpers.matchers import JWTTokenMatch
from test_framework.helpers.user_helper import create_user_success
from test_framework.models.models import GenericErrorModel, UsersLoginPostResponse

VALID_USER = UserFactory.build()
TEST_DATA = [
    APIDataClass(
        name="successful_normal_login",
        payload=UsersLoginPostRequestFactory.build(email=VALID_USER.email, password=VALID_USER.password),
        expected_status=200,
        expected_schema=UsersLoginPostResponse,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={
            REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:response:username"]: VALID_USER.username,
            REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:response:token"]: JWTTokenMatch(),
        },
    ),
    APIDataClass(
        name="normal_login_with_incorrect_password",
        payload=UsersLoginPostRequestFactory.build(email=VALID_USER.email, password="wrongPassword"),
        expected_status=401,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_empty_email",
        payload=UsersLoginPostRequestFactory.build(email="", password=VALID_USER.password),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_empty_password",
        payload=UsersLoginPostRequestFactory.build(email=VALID_USER.email, password=""),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_empty_email_password",
        payload=UsersLoginPostRequestFactory.build(email="", password=""),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_null_email_password",
        payload=tweak(
            UsersLoginPostRequestFactory.build(),
            replace={
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:email"]: None,
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:password"]: None,
            },
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_without_email",
        payload=tweak(
            UsersLoginPostRequestFactory.build(password=VALID_USER.password),
            drop=[REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:email"]],
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_without_password",
        payload=tweak(
            UsersLoginPostRequestFactory.build(email=VALID_USER.email),
            drop=[REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:password"]],
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_without_email_password",
        payload=tweak(
            UsersLoginPostRequestFactory.build(),
            drop=[
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:email"],
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:password"],
            ],
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_invalid_email_type",
        payload=tweak(
            UsersLoginPostRequestFactory.build(password=VALID_USER.password),
            replace={
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:email"]: 12345,
            },
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_invalid_password_type",
        payload=tweak(
            UsersLoginPostRequestFactory.build(email=VALID_USER.email),
            replace={
                REQUEST_RESPONSE_BODY_PATH[f"{ENDPOINT['login']}:request:password"]: 12345,
            },
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
    APIDataClass(
        name="login_with_large_password_int",
        payload=tweak(
            UsersLoginPostRequestFactory.build(email=VALID_USER.email),
            replace={
                REQUEST_RESPONSE_BODY_PATH[
                    f"{ENDPOINT['login']}:request:password"
                ]: 99999999999999999999999999999999999999999999,
            },
        ),
        expected_status=422,
        expected_schema=GenericErrorModel,
        expected_headers={"Content-Type": "application/json"},
        expected_body_values={},
    ),
]


class TestUserLogin:
    @pytest.fixture(autouse=True, scope="module")
    @classmethod
    def setup(self, my_live_server):
        create_user_success(my_live_server, VALID_USER)
        yield

    @pytest.mark.parametrize("case", TEST_DATA, ids=lambda c: c.name)
    def test_api_user_login(self, client_api, case):
        actual_response = client_api.post(ENDPOINT["login"], json=case.payload)
        assert_api_response(
            response=actual_response,
            expected_code=case.expected_status,
            expected_schema=case.expected_schema,
            expected_headers=case.expected_headers,
            expected_body=case.expected_body_values,
        )
