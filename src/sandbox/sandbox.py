from PyQt6 import QtWidgets, QtCore, QtGui
import pandas as pd
import numpy as np

import sys
import random
import datetime

from smart_qtable import smrt_consts
from smart_qtable import smrt_tbl
from frameless_dialog import frmls_dialog
from smart_qtable import smrt_delegates
from smart_qtable import smrt_dataframe


def create_test_dataframe(num_rows: int = 100) -> pd.DataFrame:
    # Generate random data for the dataframe
    f_names = ['John', 'Alice', 'Bob', 'Emily', 'Charlie', 'Barry', 'Quinn', 'Jackie', 'James']
    l_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson']
    dates = [datetime.date(random.randint(2023, 2026), random.randint(1, 12), random.randint(1, 28)) for _ in range(100)]
    date_times = [datetime.datetime(
        random.randint(2023, 2026),
        random.randint(1, 12),
        random.randint(1, 28),
        random.randint(0, 23),
        random.randint(0, 59),
        random.randint(0, 59)
    ) for _ in range(100)]
    bool_values = [True, False]

    # Create a dictionary to store column data
    data = {
        'First Name': [random.choice(f_names) for _ in range(num_rows)],
        'Last Name': [random.choice(l_names) for _ in range(num_rows)],
        'Age': [random.randint(18, 80) for _ in range(num_rows)],
        'Height': [random.uniform(58.3, 71.9) for _ in range(num_rows)],
        'Income': [random.uniform(1000, 10000) for _ in range(num_rows)],
        'Birthdate': [random.choice(dates) for _ in range(num_rows)],
        'Registration_Date': [random.choice(date_times) for _ in range(num_rows)],
        'Is_Employed': [random.choice(bool_values) for _ in range(num_rows)]
    }

    # Introduce None values randomly
    for col in data:
        none_indices = random.sample(range(num_rows), random.randint(2, 5))
        for idx in none_indices:
            data[col][idx] = None

    # Create the dataframe
    df = pd.DataFrame(data)

    # Ensure the dtypes are compatible with SmartQTable functions
    df['Age'] = df['Age'].replace(np.nan, 0).astype('int').replace(0, None)

    # Display the dataframe
    return df

def create_dtype_dict() -> dict[str, smrt_consts.SmartDataTypes]:

    dtypes = {
        'First Name': smrt_consts.SmartDataTypes.TEXT,
        'Last Name': smrt_consts.SmartDataTypes.TEXT,
        'Age': smrt_consts.SmartDataTypes.INT,
        'Height': smrt_consts.SmartDataTypes.FLOAT,
        'Income': smrt_consts.SmartDataTypes.ACCT,
        'Birthdate': smrt_consts.SmartDataTypes.DATE,
        'Registration_Date': smrt_consts.SmartDataTypes.DATE_TIME,
        'Is_Employed': smrt_consts.SmartDataTypes.BOOL
    }

    return dtypes

def main():

    app = QtWidgets.QApplication(sys.argv)

    sandbox_win = frmls_dialog.FramelessDialog(parent=None)
    sandbox_win.setWindowTitle('SmartQTable Sandbox Application')

    data = create_test_dataframe(50)
    dtypes = create_dtype_dict()

    smrt_df = smrt_dataframe.SmartDataFrame(
        dtypes=dtypes,
        data_df=data
    )

    alt_toolbar_actions = [
        QtGui.QAction(QtGui.QIcon(':/remove_item_icon.png'), 'one', sandbox_win),
        QtGui.QAction(QtGui.QIcon(':/remove_item_icon.png'), 'two', sandbox_win)
    ]

    table_actions = [
        QtGui.QAction(QtGui.QIcon(':/remove_item_icon.png'), 'remove', sandbox_win),
        QtGui.QAction(QtGui.QIcon(':/remove_item_icon.png'), 'add', sandbox_win),
        QtGui.QAction(QtGui.QIcon(':/remove_item_icon.png'), 'sum', sandbox_win)
    ]

    tbl = smrt_tbl.SmartTable(
        smrt_df=smrt_df,
        parent=sandbox_win,
        table_name='Test Table',
        table_flags=smrt_consts.SmartTableFlags.NO_FLAG,
        sum_record_count=True,
        summary_columns =['Height', 'Income'],
        table_mode=smrt_consts.SmartTableMode.DATA_MODE,
        refresh_dt=datetime.datetime(2024,1,24,15,44,49)
    )
    sandbox_win.set_central_widget(tbl)
    sandbox_win.resize(1200, 800)
    sandbox_win.set_theme(frmls_dialog.DialogTheme.DARK)
    sandbox_win.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()