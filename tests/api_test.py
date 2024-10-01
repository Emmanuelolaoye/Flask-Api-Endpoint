from flask.testing import FlaskClient
import time


"""

this file shows my implementation of the challenge

all tests show the my endpoint responses are correctly implemented

N.b time.sleep was implemented to show that my endpoint correctly checks for error code 300 only
    1. test_user_first_deposit_returns_no_error
    2. test_user_second_deposit_returns_no_error
    3. test_user_third_deposit_returns_error_300

"""


def test_user_withdrawal_returns_error_1100(client: FlaskClient) -> None:
    # this users deposit is 200 which should raise error code 1100
    user_action_test = {
        "type": "withdraw",
        "amount": "200.00",  # Over 100
        "user_id": 3,
        "time": 0000
    }

    expected_response = {'alert': True, 'alert_codes': [1100], 'user_id': 3}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_second_withdrawal_returns_no_error(client: FlaskClient) -> None:
    # user activity should not raise any error
    user_action_test = {
        "type": "withdraw",
        "amount": "99.99",  # under 100
        "user_id": 3,
        "time": 0000
    }

    # no error codes
    expected_response = {'alert': False, 'alert_codes': [], 'user_id': 3}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_third_withdrawal_returns_error_1100_and_30(client: FlaskClient) -> None:
    # test_user_third_deposit_returns_error_1100_and_30
    # 3rd consecutive withdrawal and this withdrawal is over 100
    user_action_test = {
        "type": "withdraw",
        "amount": "101.00",  # over 100
        "user_id": 3,
        "time": 0000
    }

    # should return error codes 1100 and 30
    expected_response = {'alert': True, 'alert_codes': [1100, 30], 'user_id': 3}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_fourth_withdrawal_returns_error_30(client: FlaskClient) -> None:
    # test_user_fourth_withdrawal_returns_error_30
    # 4th consecutive withdrawal and this withdrawal is not over 100
    user_action_test = {
        "type": "withdraw",
        "amount": "99.99",  # over 100
        "user_id": 3,
        "time": 0000
    }

    # should return error code 30
    expected_response = {'alert': True, 'alert_codes': [30], 'user_id': 3}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_first_deposit_returns_no_error(client: FlaskClient) -> None:
    # this user's 1st deposit should raise no errors
    user_action_test = {
        "type": "deposit",
        "amount": "10.00",
        "user_id": 4,
        "time": 0000
    }

    # should return error code 30
    expected_response = {'alert': False, 'alert_codes': [], 'user_id': 4}

    time.sleep(10)

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_second_deposit_returns_no_error(client: FlaskClient) -> None:

    # this user's 2nd deposit larger than the first which should raise no errors
    user_action_test = {
        "type": "deposit",
        "amount": "15.00",
        "user_id": 4,
        "time": 0000
    }

    # should return error code 30
    expected_response = {'alert': False, 'alert_codes': [], 'user_id': 4}

    time.sleep(10)

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_third_deposit_returns_error_300(client: FlaskClient) -> None:
    # this user's 3rd deposit larger than the first which should raise no errors
    user_action_test = {
        "type": "deposit",
        "amount": "20.00",
        "user_id": 4,
        "time": 0000
    }

    # should return error code 300
    expected_response = {'alert': True, 'alert_codes': [300], 'user_id': 4}

    time.sleep(12)

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_user_first_deposit_within_30_seconds_no_error(client: FlaskClient) -> None:
    # this user's 1st deposit
    user_action_test = {
        "type": "deposit",
        "amount": "100.00",
        "user_id": 5,
        "time": 0000
    }

    # should return error code 300
    expected_response = {'alert': False, 'alert_codes': [], 'user_id': 5}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response


def test_second_deposit_within_time_returns_error_123(client: FlaskClient) -> None:
    # this user's 1st deposit
    user_action_test = {
        "type": "deposit",
        "amount": "101.00",
        "user_id": 5,
        "time": 0000
    }

    # should return error code 300
    expected_response = {'alert': True, 'alert_codes': [123], 'user_id': 5}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response

def test_third_deposit_within_time_returns_error_300_and_123(client: FlaskClient) -> None:
    # this user's 1st deposit
    user_action_test = {
        "type": "deposit",
        "amount": "103.00",
        "user_id": 5,
        "time": 0000
    }

    # should return error code 300
    expected_response = {'alert': True, 'alert_codes': [300, 123], 'user_id': 5}

    # Send a POST request with the data
    response = client.post("/event", json=user_action_test)

    # Assert that the status code is 200 meaning a good connection
    assert response.status_code == 200

    # Assert that the response contains the same data
    assert response.json == expected_response

