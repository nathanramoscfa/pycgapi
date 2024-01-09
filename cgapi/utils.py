import time
from datetime import datetime


def convert_ids_to_string(ids_list):
    """
    Convert a list of cryptocurrency IDs into a comma-separated string.

    Args:
        ids_list (list): A list of cryptocurrency IDs.

    Returns:
        str: A comma-separated string of cryptocurrency IDs.
    """
    return ','.join(ids_list)


def convert_to_unix(date_str):
    """Convert 'mm-dd-yyyy' string to UNIX timestamp."""
    if date_str is not None:
        try:
            # Assuming date_str is in UNIX timestamp format
            return int(date_str)
        except ValueError:
            # Converting from 'mm-dd-yyyy' format to UNIX timestamp
            return int(time.mktime(datetime.strptime(date_str, '%m-%d-%Y').timetuple()))
    return None
