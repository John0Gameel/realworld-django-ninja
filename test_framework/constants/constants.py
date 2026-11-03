ENDPOINT = {"login": "/users/login"}


REQUEST_RESPONSE_BODY_PATH = {
    f"{ENDPOINT['login']}:request:email": "user.email",
    f"{ENDPOINT['login']}:request:password": "user.password",
    f"{ENDPOINT['login']}:response:username": "user.username",
    f"{ENDPOINT['login']}:response:token": "user.token",
}

API_FAILURE_MATRIX = {
    "status_code": {"Fail": False, "Message": ""},
    "schema": {"Fail": False, "Message": ""},
    "headers": {"Fail": False, "Message": ""},
    "body": {"Fail": False, "Message": ""},
    "unknown": {"Fail": False, "Message": ""},
}
