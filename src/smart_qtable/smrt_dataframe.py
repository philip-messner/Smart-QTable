import pandas as pd

import dataclasses
import datetime
import typing

from smart_qtable import smrt_consts


@dataclasses.dataclass
class SmartDataFrame:

    dtypes: dict[str, smrt_consts.SmartDataTypes]
    data_df: typing.Optional[pd.DataFrame] = None
    refresh_dt: typing.Optional[datetime.datetime] = datetime.datetime.now()

    def __post_init__(self):
        if self.dtypes is None:
            raise ValueError('The dtypes parameter is required.')
        if self.data_df is None:
            self.data_df = pd.DataFrame(columns=list(self.dtypes.keys()))
        else:
            if len(self.dtypes) != self.data_df.shape[1]:
                raise ValueError('The dataframe columns and dtype key columns must match exactly.')
            for column in self.dtypes.keys():
                if column not in self.data_df.columns:
                    raise ValueError('The dataframe columns and dtype key columns must match exactly.')
