from typing import Iterable, List, Dict, Tuple
import gc

import numpy as np

TRUE_PAIR = float(1)
FALSE_PAIR = float(0)

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

class Batch:
    def __init__(self, maxSize: int) -> None:
        self.maxSize = maxSize
        self.count = 0
        self.pairIds: List[ Tuple[int, int] ] = []
        self.pairs: List[np.ndarray] = []
        self.predictions: Iterable[float]

    def isNotEmpty(self) -> bool:
        return self.count > 0

    def isFull(self) -> bool:
        return self.count == self.maxSize

    def addPair(self, a: np.ndarray, b: np.ndarray, a_id: int, b_id: int) -> None:
        assert self.maxSize > self.count, "Attempted to add item to full Batch." 

        self.pairs.append(np.concatenate((a, b), axis=None))
        self.pairIds.append((a_id, b_id))
        self.count += 1

    def saveAndReset(self, container: List[ Dict[str, int] ], triggerGC=False) -> None:
        for pairIds, prediction in zip(self.pairIds, self.predictions):
            if prediction == TRUE_PAIR:
                newItem = {
                    "left_instance_id": pairIds[0],
                    "right_instance_id": pairIds[1],
                }
                container.append(newItem)
        
        self.pairs.clear()
        self.pairIds.clear()
        self.count = 0

        if triggerGC:
            gc.collect()
