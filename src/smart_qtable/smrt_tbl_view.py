import dataclasses


@dataclasses.dataclass
class SmartTableView:

    name: str
    hidden_cols: list[str]
    col_order: list[str]

    def __eq__(self, other):
        if not isinstance(other, SmartTableView):
            return False
        same = True
        same = same and len(self.hidden_cols) == len(other.hidden_cols)
        if not same:
            return False
        same = same and len(self.col_order) == len(other.col_order)
        if not same:
            return False
        for col in self.hidden_cols:
            same = same and col in other.hidden_cols
        if not same:
            return False
        for i in range(len(self.col_order)):
            same = same and self.col_order[i] == other.col_order[i]
        return same

