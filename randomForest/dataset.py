from typing import List

import numpy as np

class Dataset:
    def __init__(self) -> None:
        self.x: List[np.ndarray] = []
        self.y: List[float] = []

    def __len__(self) -> int:
        return len(self.y)
    
    def addPair(self, a: np.ndarray, b: np.ndarray, label: float, addReverse: bool = True) -> None:
        pair = np.concatenate((a, b), axis=None)

        if addReverse:
            reversePair = np.concatenate((b, a), axis=None)

            # https://stackoverflow.com/questions/14446128/python-append-vs-extend-efficiency
            self.x.extend((pair, reversePair))
            self.y.extend((label, label))
        else:
            self.x.append(pair)
            self.y.append(label)
