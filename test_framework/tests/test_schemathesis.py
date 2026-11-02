import schemathesis
from hypothesis import settings
from test_framework.factories.user_factory import UserFactory
from test_framework.helpers.my_api import MyAPI
from test_framework.helpers.user_helper import create_user_success
from test_framework.fixtures.my_live_server import my_live_server, my_live_db
import pytest

BASE_URL = "http://localhost:8001/api"
schema = schemathesis.openapi.from_path("realworld/specs/api/openapi.yml")
# Show the token in the curl reproduction command
schema.config.output.sanitization.update(enabled=False)
schema.config.update(base_url=BASE_URL)


@schema.parametrize()
@settings(max_examples=500)
def test_api(case):
    case.call_and_validate()

@pytest.fixture
def state_machine(my_live_server):
    class APIWorkflow(schema.as_state_machine()):
        def setup(self):
            # Runs at the start of each scenario
            myapi = MyAPI(BASE_URL, auth_type= "Token")
            user = UserFactory()
            create_user_success(my_live_server, myapi, user)
            response = myapi.post("/users/login", json={"user" : {"username": user.username, "password": user.password, "email":user.email}})
            response.raise_for_status()
            self.headers = {"Authorization": f"Token {response.json()['user']['token']}"}

        def before_call(self, case):
            # Runs before every request in the scenario
            case.headers = {**(case.headers or {}), **self.headers}
    return APIWorkflow

def test_statefully(state_machine):
    state_machine.run(settings=settings(state_machine.TestCase.settings, max_examples=1000, stateful_step_count=10))
