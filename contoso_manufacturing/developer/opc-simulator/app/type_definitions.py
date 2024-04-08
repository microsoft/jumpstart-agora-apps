# pylint: disable=too-few-public-methods

from typing import List, Tuple, Any
from datetime import datetime


UpdateList = List[Tuple[str, Any, bool]]
UpdateListWithTimeStamp = Tuple[UpdateList, datetime]

# pylint: enable=too-few-public-methods
