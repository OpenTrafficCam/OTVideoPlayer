import datetime as dt
import re


def _get_datetime_from_filename(
    filename: str, epoch_datetime="1970-01-01_00-00-00"
) -> str:
    """Get date and time from file name.
    Searches for "_yyyy-mm-dd_hh-mm-ss".
    Returns "yyyy-mm-dd_hh-mm-ss".

    Args:
        filename (str): filename with expression
        epoch_datetime (str): Unix epoch (00:00:00 on 1 January 1970)

    Returns:
        str: datetime
    """
    regex = "_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-[0-9]{2,2})"
    match = re.search(regex, filename)
    if not match:
        return epoch_datetime

    # Assume that there is only one timestamp in the file name
    datetime_str = match[1]

    try:
        return dt.datetime.strptime(datetime_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return dt.datetime.strptime(epoch_datetime)
