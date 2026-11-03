import json
from copy import deepcopy
from logging import getLogger

from glom import glom
from pydantic import BaseModel
from requests.models import Response

from test_framework.constants.constants import API_FAILURE_MATRIX

logger = getLogger()


def assert_api_response(
    response: Response,
    expected_code: int,
    expected_schema: BaseModel,
    expected_headers: dict,
    expected_body: dict,
):
    # First layer check on the status code
    response_matrix_check = deepcopy(API_FAILURE_MATRIX)

    try:
        if response.status_code == expected_code:
            response_matrix_check["status_code"]["Fail"] = False
            response_matrix_check["status_code"]["Message"] = (
                f"Status Code Match\n" f"Actual: {response.status_code}, Expected: {expected_code}"
            )
        else:
            response_matrix_check["status_code"]["Fail"] = True
            response_matrix_check["status_code"]["Message"] = (
                "API Response with unexpected status "
                f"code\nActual: {response.status_code}, Expected: {expected_code}"
            )

        response_json = response.json()
        if expected_schema:
            schema_string = json.dumps(expected_schema.model_json_schema(), indent=2)
            try:
                expected_schema(**response_json)
                response_matrix_check["schema"]["Fail"] = False
                response_matrix_check["schema"]["Message"] = "Response Schema Match. " f"Schema: \n{schema_string}"
            except Exception as e:
                response_matrix_check["schema"]["Fail"] = True
                response_matrix_check["schema"]["Message"] = (
                    "API response broke the " f"schema contract, Expected Schema \n{schema_string}, {e}"
                )

        for header, value in expected_headers.items():
            if value in response.headers[header]:
                response_matrix_check["headers"]["Message"] += (
                    f"Header {header} was received correctly\n"
                    f"Actual: {response.headers[header]}, Expected {value} \n"
                )
            else:
                response_matrix_check["headers"]["Fail"] = True
                response_matrix_check["headers"]["Message"] += (
                    f"Header {header} was not received correctly\n"
                    f"Actual: {response.headers[header]}, Expected {value} \n"
                )

        for target_path, value in expected_body.items():
            actual_value = glom(response_json, target_path)
            if actual_value == value:
                response_matrix_check["body"]["Message"] += (
                    "Response Body is received as "
                    f"expected for {target_path}\n"
                    f"Actual: {actual_value}, Expected {value} \n"
                )
            else:
                response_matrix_check["body"]["Fail"] = True
                response_matrix_check["body"]["Message"] += (
                    "Response Body is not received as "
                    f"expected for {target_path}\n"
                    f"Actual: {actual_value}, Expected {value} \n"
                )
    except Exception as e:
        response_matrix_check["unknown"]["Fail"] = True
        response_matrix_check["unknown"]["Message"] = f"Unexpected Error Occurred {e} \n"

    status_msg = "\n".join([v["Message"] for v in response_matrix_check.values()])
    assert all(not v["Fail"] for v in response_matrix_check.values()), status_msg
    print(status_msg)
