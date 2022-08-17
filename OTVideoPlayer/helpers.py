# OTVideoPlayer: Helpers
# Copyright (C) 2022 OpenTrafficCam Contributors
# <https://github.com/OpenTrafficCam
# <team@opentrafficcam.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import datetime as dt
import platform
import re

EPOCH = dt.datetime.utcfromtimestamp(0)
"""Time from unix epoch in seconds"""

OS = platform.system().replace("Darwin", "Mac")
"""OS OTVision is currently running on"""

ON_WINDOWS = OS == "Windows"
"""Wether OS is Windows or not"""

ON_LINUX = OS == "Linux"
"""Wether OS is Linux or not"""

ON_MAC = OS == "Mac"
"""Wether OS is MacOS or not"""


def _get_datetime_from_filename(
    filename: str, epoch_datetime="1970-01-01_00-00-00"
) -> str:
    """Get date and time from file name.
    Searches for "yyyy-mm-dd_hh-mm-ss".
    Returns datetime object.

    Args:
        filename (str): filename with expression
        epoch_datetime (str): Unix epoch (00:00:00 on 1 January 1970)

    Returns:
        dt.datetime: datetime object
    """
    regex = "([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-[0-9]{2,2})"
    match = re.search(regex, filename)
    if not match:
        return dt.datetime.strptime(epoch_datetime, "%Y-%m-%d_%H-%M-%S")

    # Assume that there is only one timestamp in the file name
    datetime_str = match[1]

    try:
        return dt.datetime.strptime(datetime_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return dt.datetime.strptime(epoch_datetime, "%Y-%m-%d_%H-%M-%S")
