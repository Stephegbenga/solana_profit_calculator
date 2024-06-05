import datetime, json
import pytz, time
import concurrent.futures, json
import traceback
import requests

def unix_timestamp_to_lagos_time(unix_timestamp):
    # Convert Unix timestamp to datetime object in UTC
    dt_utc = datetime.datetime.utcfromtimestamp(unix_timestamp)

    # Set the UTC timezone
    utc_timezone = pytz.timezone('UTC')
    dt_utc = utc_timezone.localize(dt_utc)

    # Convert UTC datetime to Lagos (WAT) timezone
    lagos_timezone = pytz.timezone('Africa/Lagos')
    dt_lagos = dt_utc.astimezone(lagos_timezone)

    # Format datetime object as a string in desired date and time format
    formatted_date = dt_lagos.strftime('%Y-%m-%d %H:%M')  # Example format

    return formatted_date


# Function to read JSON data from file
def read_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
            return json_data
    except Exception as e:
        with open(file_path, "w") as json_file:
            json.dump([], json_file, indent=4)
        return []



def save_json_to_file(file_name, data):
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print("Data saved to file")



def parallel_functions(items, func, max_workers=None):
    if max_workers is None:
        max_workers = len(items)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit each item processing task to the executor
        future_to_item = {executor.submit(func, item): item for item in items}

        results = []

        # Wait for each task to complete and collect the results
        for future in concurrent.futures.as_completed(future_to_item):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                error_message = str(e)
                # Capture the traceback information
                traceback_info = traceback.format_exc()
                # Append the traceback information to the error message
                error_message_with_traceback = f"{error_message}\n\nTraceback:\n{traceback_info}"
                print(error_message_with_traceback)

    return results


class SimpleCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            value, expiry_time = self.cache[key]
            if expiry_time is None or time.time() < expiry_time:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value, expiry_seconds=None):
        expiry_time = None
        if expiry_seconds is not None:
            expiry_time = time.time() + expiry_seconds
        self.cache[key] = (value, expiry_time)

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]


Local_Cache = SimpleCache()



def calculate_percentage_increase(initial_price, final_price):
    initial_price = float(initial_price)
    final_price = float(final_price)

    if initial_price == 0:
        raise ValueError("Initial price cannot be zero.")

    percentage_increase = ((final_price - initial_price) / initial_price) * 100
    rounded_percentage_increase = round(percentage_increase, 1)
    return rounded_percentage_increase


