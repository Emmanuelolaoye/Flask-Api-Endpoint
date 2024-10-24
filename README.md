# Emmanuel's Flask API Endpoint

---

## Introduction

I set up the  Flask API that runs on port `5001` and i made some aditions to the `pytest` test showing the endpoint appropriately handling all required conditions.


---

The provided `Makefile` was kept as is and the project file should run using the following.


### 1. Install dependencies

```sh
poetry install
```

### 2. Start API server

```sh
make run
```

### 3. Run tests

```sh
make test
```

### 4. Testing

```sh
curl -XPOST 'http://127.0.0.1:5001/event' -H 'Content-Type: application/json' \
-d '{ "type": "deposit",
    "amount": "42.00",
    "user_id": 1,
    "time": 10 }'
```
---

## Walkthrough

### api.py
a few alterations were made to the `api.py` firstly the `request` object was imported to get the request data sent by the client. this user activity data was sent to `user_data_handler.py` to be validated and create the reply (`handle_user_data`)

### user_data_handler.py
In this file the bulk of the user activity handling was done here 

The user activity in the form of a dictionary is parsed and the added into a CSV file `data.csv` along with a datetime timestamp.


| user_id | type       | amount   | time                |  timestamp |
|---------|------------|----------|---------------------|------------|
| 3       | withdraw   | 200.00   | 28:09:2024:23:50:54 | 0          |
| 3       | withdraw   | 99.99    | 28:09:2024:23:51:40 | 0          |
| 3       | withdraw   | 101.00   | 28:09:2024:23:51:49 | 0          |
| ....    | ....       | ....     | ....                | ....       |



This will mean that every time a new payload is received by the endpoint, they payload will first be stored in the csv file before any checks are made 

Once the checks are made the function `get_endpoint_response` will begin the steps of creating a response.

### get_endpoint_response
```python
def get_endpoint_response(data: dict) -> dict:
    user_id = data["user_id"]
    alert = False

    alert_codes = get_codes(data)

    if alert_codes:
        alert = True

    return {
        "alert": alert,
        "alert_codes": alert_codes,
        "user_id": user_id
    }
```

This function was responsible for actually creating the JSON object by since all responses will end up having the same steructure it can be pre built now and then altered by adding the alert codes as the check are made in real time.

---

# Response Handling

### `Alert code 1100:` A withdrawal amount over 100

This was the first alert code that i tried to check for. it was pretty straight forward. all i did was look at the user's activity and if the amount was greater than 100, the function would return true. 

```python
def check_withdrawals_amount(data: dict) -> bool:
    if float(data['amount']) > 100 and data['type'] == 'withdraw':
        return True

    return False
```




### `Alert code 30`: *The user makes 3 consecutive withdrawals*

This was the first alert code checks that required storing previous user activity to be able to check for this condition. So to solve this challenge, using the user_id i counted if the user last 3 transactions were `withdraw` and if so i would return truu and return flase if not


```python
   


def check_consecutive_withdrawals(user_id: str) -> bool:
    user_id = str(user_id)
    number_of_consecutive_withdrawals = 0
    
    with open('user_monitoring/data.csv', mode='r') as csv_file:
        csv_reader = DictReader(csv_file)

        user_activity_database = list(csv_reader)

        for row in reversed(user_activity_database):

            if row["user_id"] == user_id:
                if row['type'] == "withdraw":
                    number_of_consecutive_withdrawals += 1
                    if number_of_consecutive_withdrawals == 3:
                        return True

                else:
                    return False  # Reset counter if not a withdrawal

    return False  # Return alert codes after the entire user_activity_database are processed
```


### `Alert code 300:` The user makes 3 consecutive deposits where each one is larger than the previous deposit (withdrawals in between deposits can be ignored).

To check for this condition, it was necessary to search through the database of previous user activity. However, we needed to determine if one deposit was larger than the previous one. Similar to `Alert code 30`, the function iterates through the user activity, starting from the most recent entry, and checks if the deposit amount for a given `user_id` is larger than the previous one. This process continues until three consecutive deposits have been found. If three consecutive increasing deposits are identified, the function returns `True`; otherwise, it returns `False`.

```python
def check_consecutive_deposit(user_id: int) -> bool:
    user_id = str(user_id)
    number_of_consecutive_deposits = 0
    last_deposit_amount = float('inf')  # initialised to infinity as it's an impossibly high number

    # Open the CSV file
    with open('user_monitoring/data.csv', mode='r') as csv_file:
        csv = DictReader(csv_file)

        # Convert the reader to a list, so we can reverse it
        user_activity_database = list(csv)

        # Reverse the list to read the most recent deposits first
        for row in reversed(user_activity_database):

            print(row, "conssy", number_of_consecutive_deposits)

            if row["user_id"] == user_id:
                if row['type'] == "deposit":
                    current_amount = float(row["amount"])

                    # Check if the current deposit is greater than the previous one
                    if current_amount < last_deposit_amount:
                        number_of_consecutive_deposits += 1
                        last_deposit_amount = current_amount  # Update last deposit amount

                        # If we've found 3 consecutive increasing deposits
                        if number_of_consecutive_deposits == 3:
                            return True

                    elif row['type'] == 'withdraw':
                        continue

                    else:
                        return False

    return False  # If no consecutive increasing deposits were found
```

### `Alert code 123: ` The total amount deposited in a 30-second window exceeds 200

Here's the proofread version of the function description:

---

This function checks if a user has made deposits totaling at least 200 within the last 30 seconds. It works by reading through a CSV file of user activity, starting from the most recent entry. First, the function determines the timestamp of 30 seconds prior to the latest recorded activity. Then, it scans the user’s transactions within that time window. If the deposits made by the specified `user_id` during this period add up to 200 or more, the function returns `True`. If not, it returns `False`.

---

```python

def check_user_activity_30_secs_ago(user_id: str) -> bool:
    total = 0
    user_id = str(user_id)

    # Open the CSV file and read the data
    with open('user_monitoring/data.csv', mode='r') as csv_file:
        csv_reader = DictReader(csv_file)

        # Convert the reader to a list so we can reverse it
        rows = list(csv_reader)

        # Get the most recent time (which would be at the bottom of the table)
        most_recent_time = rows[-1]['time']
        converted_date = datetime.strptime(most_recent_time, "%d:%m:%Y:%H:%M:%S")

        # Calculate the timestamp 30 seconds ago
        time_thirty_seconds_ago = converted_date - timedelta(seconds=30)

        # Iterate over the rows in reverse order
        for row in reversed(rows):
            row_time = datetime.strptime(row['time'], "%d:%m:%Y:%H:%M:%S")

            # Check if the row time is within the last 30 seconds
            if row_time > time_thirty_seconds_ago and row['user_id'] == user_id and row["type"] == "deposit":
                total += float(row['amount'])

                # Return True if total exceeds 200
                if total >= 200:
                    return True

    # If we exit the loop without hitting 200, return False
    return False

```

---

# Testing

```python
from flask.testing import FlaskClient


def test_handle_user_event_doesnt_do_anything_yet(client: FlaskClient) -> None:
    response = client.post("/event")
    assert response.status_code == 200
    assert response.json == {}
```

Fortunately, I was provided with a skeleton template to test the basic functionality of my code. However, to thoroughly evaluate my function's capabilities, I needed to create my own unit tests, which included the following:



### `alert code 1100`:

```python
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

```

### `alert code 30`:
```python
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
```

### `alert code 300`:

```python
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
```

### `alert code 300`:

```python
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
```




---

### Results

In total, 10 different unit tests were run, where the endpoints were provided with various payloads and had to adapt to each scenario. For example, the tests included waiting for 3 consecutive withdrawals before raising `alert code 300`, among others.

The following are the results of the tests:

```
tests/api_test.py::test_user_withdrawal_returns_error_1100 PASSED                                                                                                 [ 10%]
tests/api_test.py::test_user_second_withdrawal_returns_no_error PASSED                                                                                            [ 20%]
tests/api_test.py::test_user_third_withdrawal_returns_error_1100_and_30 PASSED                                                                                    [ 30%]
tests/api_test.py::test_user_fourth_withdrawal_returns_error_30 PASSED                                                                                            [ 40%]
tests/api_test.py::test_user_first_deposit_returns_no_error PASSED                                                                                                [ 50%]
tests/api_test.py::test_user_second_deposit_returns_no_error PASSED                                                                                               [ 60%]
tests/api_test.py::test_user_third_deposit_returns_error_300 PASSED                                                                                               [ 70%]
tests/api_test.py::test_user_first_deposit_within_30_seconds_no_error PASSED                                                                                      [ 80%]
tests/api_test.py::test_second_deposit_within_time_returns_error_123 PASSED                                                                                       [ 90%]
tests/api_test.py::test_third_deposit_within_time_returns_error_300_and_123 PASSED                                                                                [100%]

========================================================================== 10 passed in 32.15s ==========================================================================
(junior-technical-test-template-py3.12) emmanuelolaoye@Emmanuels-Air junior-technical-test-template % 
```

**Note:** These tests can only be run once without clearing the database. Some assertions rely on specific conditions, such as expecting a second withdrawal. Running the tests again without resetting the database may lead to inaccurate results, as the conditions in the database would have changed and no longer match the original test assertions.


---

### Challenges

While I was trying to complete this challenge I faced numerous challenges. firstly initially I had problems trying to run the server on `port 5000` namely due to a port already in use error as macos uses that port for *handoff* and *airdrop* so this now made me then choose to run the server on `port 5001`. this also meant that when testing the endpoint using a curl command it had to be changed accordingly

```sh
curl -XPOST http://127.0.0.1:5001/event -H 'Content-Type: application/json' \
    -d '{"type": "deposit", "amount": "42.00", "user_id": 1, "time": 0}'
```

Once I got the server skeleton running I was then faced with the problem of trying to understand what the `'time': int` meant so to make things easier for myself i then chose to make a function called `add_time` and use the `datetime` library to actually give each user activity payload a DateTime which was when it was passed to the endpoint.

apart from all these, i found this challenge  quite enjoyable and I hope that it can help demonstrate my skills and ability to Midnite

---
`- Emmanuel_Olaoye`






