import pandas as pd
from handler_x1 import handle_x1
from handler_x3 import handle_x3
from handler_x4 import handle_x4

Flag = True

if __name__ == '__main__':
    for file_name in ['X1.csv']:
        data = pd.read_csv(file_name)
        if 'name' not in data.columns:
            output = handle_x1(data)
            
        if Flag:
            output.to_csv("output.csv", sep=',', encoding='utf-8', index=False)
            Flag = False
        else:
            output.to_csv(
                "output.csv",
                mode='a',
                sep=',',
                encoding='utf-8',
                index=False,
                header=None)
