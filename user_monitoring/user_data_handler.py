from datetime import datetime, timedelta

from csv import writer, DictReader


def handle_user_data(data: dict) -> dict:
    add_time(data)

    add_to_databse(data)

    print("done")

    return get_endpoint_response(data)


def add_time(data: dict):
    data["timestamp"] = datetime.now().strftime("%d:%m:%Y:%H:%M:%S")


def add_to_databse(data: dict):
    # get the user id:
    user_id = data['user_id']

    # get the time stamp
    timestamp = data['timestamp']

    # get the amount
    amount = data['amount']

    # get the type
    action_type = data['type']

    # get the time
    time = data['time']

    with open('user_monitoring/data.csv', 'a') as f_object:
        writer_object = writer(f_object)

        writer_object.writerow([user_id, action_type, amount, timestamp, time])

        f_object.close()



def get_codes(data):
    alert_codes = []

    if check_withdrawals_amount(data):
        alert_codes.append(1100)

    if check_consecutive_withdrawals(data["user_id"]):
        alert_codes.append(30)

    if check_consecutive_deposit(data["user_id"]):
        alert_codes.append(300)

    if check_user_activity_30_secs_ago(data['user_id']):
        alert_codes.append(123)

    return alert_codes


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


def check_withdrawals_amount(data: dict) -> bool:
    if float(data['amount']) > 100 and data['type'] == 'withdraw':
        return True

    return False


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
