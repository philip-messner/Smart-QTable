import typing

from PyQt6 import QtGui, QtCore

import datetime
import enum
import dataclasses

# common enumerated type classes

class SmartValueFlags(enum.IntFlag):

    NO_FLAG = 0
    REQUIRED = 1            # date is required. If None will be listed as UNKNOWN
    MIN_VALID_VALUE = 2      # any date below a specific minimum will be listed as INVALID
    MAX_VALID_VALUE = 4      # any date above a specific maximum will be listed as INVALID
    MAX_EXPECTED_VALUE = 8     # any date above a specific maximum will be considered as None (Blank)


@dataclasses.dataclass
class SmartValueAttributes:

    flags: SmartValueFlags = SmartValueFlags.NO_FLAG
    min_value: typing.Any = None
    max_value: typing.Any = None


class ThreadStatus(enum.IntEnum):
    UNINIT = -999
    STARTING = -1
    IDLE = 0
    ACTIVE = 1
    SUSPENDED = 2
    DEAD = 3

class ActionStatus(enum.IntEnum):
    UNINIT = -999
    IDLE = 0
    PENDING = 1
    IN_PROGRESS = 2
    COMPLETE = 3
    ERROR = 4
    FAILED = 5

class SmartDataTypes(enum.IntEnum):

    UNKNOWN = -1
    TEXT = 0
    INT = 1
    FLOAT = 2
    ACCT = 3
    DATE = 4
    DATE_TIME = 5
    OBJECT = 6
    BOOL = 7
    STATUS = 8


class SmartTableMode(enum.IntEnum):

    DATA_MODE = 0
    ACTION_MODE = 1


class SmartTableFlags(enum.IntFlag):

    NO_FLAG = 0
    ACTION_ENABLED = 1
    EDITABLE_DATA = 2
    ITERATIVE_REFRESH = 4


class SmartEditFlags(enum.IntFlag):

    DIRECT_EDIT = 0
    INDIRECT_EDIT = 1


class SmartEditorTypes(enum.IntEnum):

    BASIC_TEXT = 0
    INT_SPIN_BX = 1
    FLOAT_DBL_SPIN_BX = 2
    CBO_BOX = 3
    FLOAT_LINE_EDIT = 4

class HdrBtnIcons(enum.StrEnum):

    DEFAULT = ':/menu_down.PNG'
    SORT_ASCENDING = ':/menu_down_sort_up.PNG'
    SORT_DESCENDING = ':/menu_down_sort_down.PNG'
    FILTER = ':/menu_down_filter.PNG'
    FILTER_SORT_ASCENDING = ':/filter_sort_up.png'
    FILTER_SORT_DESCENDING = ':/filter_sort_dwn.png'

class SmartFilterAction(enum.IntEnum):

    NO_ACTION = 0
    SORT_ASCENDING = 1
    SORT_DESCENDING = 2
    CLR_SORT = 3
    CLR_FILTER = 4
    HIDE_COL = 5
    NEW_FILTER = 6

class SmartFilterMode(enum.IntEnum):

    TEXT = 0
    NUMBER = 1
    ACCT = 2
    DATE = 3
    DATE_TIME = 4

class DateTimeNodeData(enum.IntEnum):

    YEAR = 0
    MONTH = 1
    DAY = 2
    HOUR = 3
    MIN = 4
    SEC = 5


class ExcelVerticalAlignment(enum.IntEnum):

    BOTTOM = -4107
    CENTER = -4108
    DISTRIBUTED = -4117
    JUSTIFY = -4130
    TOP = -4160


class ExcelHorizontalAlignment(enum.IntEnum):

    CENTER = -4108
    CENTER_SELECTION = 7
    DISTRIBUTE = -4117
    FILL = 5
    GENERAL = 1
    JUSTIFY = -4130
    LEFT = -4131
    RIGHT = -4152


class ExcelPageOrientation(enum.IntEnum):

    LANDSCAPE = 2
    PORTRAIT = 1

# defined status colors
ACTION_STATUS_COLORS = {
    ActionStatus.UNINIT: QtGui.QColor('#000000'),
    ActionStatus.IDLE: QtGui.QColor('#9ea7ad'),
    ActionStatus.PENDING: QtGui.QColor('#2dccff'),
    ActionStatus.IN_PROGRESS: QtGui.QColor('#fce83a'),
    ActionStatus.COMPLETE: QtGui.QColor('#56f000'),
    ActionStatus.ERROR: QtGui.QColor('#ffb302'),
    ActionStatus.FAILED: QtGui.QColor('#ff3838')
}

THREAD_STATUS_COLORS = {
    ThreadStatus.UNINIT: QtGui.QColor('#000000'),
    ThreadStatus.STARTING: QtGui.QColor('#9ea7ad'),
    ThreadStatus.IDLE: QtGui.QColor('#2dccff'),
    ThreadStatus.ACTIVE: QtGui.QColor('#fce83a'),
    ThreadStatus.SUSPENDED: QtGui.QColor('#ffb302'),
    ThreadStatus.DEAD: QtGui.QColor('#ff3838')
}

# Application Universal File Directories
DEFAULT_APP_NAME = 'MyApp'
COMPANY_DIR = r'ConMed_ATL'
DATA_DIR = r'Data'
LOG_DIR = r'Logs'
LOG_FILE = r'_info.log'
SMART_TABLE_DATA_FOLDER = r'Smart_Table'
KEY_FILE = r'_prog_cryp.pkl'
USER_FILE = r'_user_data.pkl'

# These are based on the max and min timestamps allowable in pandas
UNKNOWN_DATETIME = datetime.datetime(1677, 9, 22, 0, 0, 0)
UNKNOWN_DATE = UNKNOWN_DATETIME.date()
INVALID_DATETIME = datetime.datetime(1975, 4, 29, 0, 0, 0)
INVALID_DATE = INVALID_DATETIME.date()
SORT_ASC_UNKNOWN_DATETIME = datetime.datetime(2262, 4, 11)
SORT_ASC_UNKNOWN_DATE = SORT_ASC_UNKNOWN_DATETIME.date()
MAX_DAYS_AHEAD = 4000
MAX_DAYS_BEHIND = 8000


# defined flag values
CONMED_ATL_NULL = -918273465
ADV_SORT_NO_SELECT_FLAG = -1234
ADV_SORT_COL_NAME_VALUE = 9876
ADV_SORT_SORT_ORD_VALUE = 6789
SMRT_TBL_BLANK_INT_FLAG = -975312468

# Custom assigned Item Data Roles
ACTION_STATUS_ROLE = QtCore.Qt.ItemDataRole.UserRole + 11
ACTION_PROGRESS_ROLE = QtCore.Qt.ItemDataRole.UserRole + 12
THREAD_STATUS_ROLE = QtCore.Qt.ItemDataRole.UserRole + 13
ACTION_PENDING_ROLE = QtCore.Qt.ItemDataRole.UserRole + 14
TABLE_SORT_ROLE = QtCore.Qt.ItemDataRole.UserRole + 15
TABLE_FILTER_ROLE = QtCore.Qt.ItemDataRole.UserRole + 16
DTYPE_QUERY_ROLE = QtCore.Qt.ItemDataRole.UserRole + 17
CBO_COL_LIST_ROLE = QtCore.Qt.ItemDataRole.UserRole + 18
CBO_TYPE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 19
SPN_MIN_VALUE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 20
SPN_MAX_VALUE_ROLE = QtCore.Qt.ItemDataRole.UserRole + 21

# model background colors
MODEL_DELETED_ROW_BG_COLOR = QtGui.QColor('#3e3f40')
MODEL_NEW_ROW_BG_COLOR = QtGui.QColor('#182238')
MODEL_UPDATED_CELL_BG_COLOR = QtGui.QColor('')
MODEL_PENDING_EDIT_BG_COLOR = QtGui.QColor('#3b381d')
EDITABLE_COLUMN_BG_COLOR = QtGui.QColor(68, 71, 36)

# For auto resizing of tables
MIN_COLUMN_WIDTH = 100

# action and data change timeout settings
TIMER_CHECK_FOR_OLD_ACTIONS_MSECS = 30000 # 30 sec
ACTION_TIMEOUT_SECS = 300 # 5 min
TABLE_DATA_CHANGE_TIMEOUT_SECS = 300 # 5 min

# for the smart data frame object, the number of informational columns to be added to front of table (at times)
DF_STATUS_COL = 1
DF_STATUS_COL_NAME = 'Status'
DF_PENDING_ACTION_COL = 0
DF_PENDING_ACTION_COL_NAME = 'Pending'
DF_PROGRESS_COL = 2
DF_PROGRESS_COL_NAME = 'Progress'
SMART_DATA_INFO_COLS = [DF_PENDING_ACTION_COL_NAME, DF_STATUS_COL_NAME, DF_PROGRESS_COL_NAME]
SMART_DATA_COL_DTYPES = [SmartDataTypes.OBJECT,
                         SmartDataTypes.OBJECT,
                         SmartDataTypes.FLOAT]
DF_ACTION_COLUMN = 'Pending Action'

DF_INDEX_NAME = 'Index'
FILTER_MAX_ROW_LIMIT = 10000

SELECT_ALL_TXT = '(Select All)'
SELECT_ALL_RESULTS = '(Select All Search Results)'
BLANKS_TXT = '(Blanks)'
UNKNOWN_TXT = '(Unknown)'
INVALID_TXT = '(Invalid)'
ADD_CURRENT_TXT = 'Add current selection to filter'
NO_MATCHES_TXT = 'No matches'
CUSTOM_VIEW_NAME = 'Custom...'
RECORD_COUNT_NAME = 'Records'

MAX_SUMMARY_WIDGETS = 3

INT_TO_MONTH = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

MONTH_TO_INT = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

DRAG_MOVE_SENSITIVITY = 10

NUM_PARALLEL_THREADS = 10

# priority queue constants
QUEUE_SHUTDOWN_PRIORITY = -5
WORKER_PAUSE_PRIORITY = 0
WORKER_RESUME_PRIORITY = 1
STD_ACTION_PRIORITY = 2

# worker constants
WORKER_WAIT_TIME = 0.5
