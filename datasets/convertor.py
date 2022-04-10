import pandas as pd
import re

Flag = True

if __name__ == '__main__':
    file_name = '/home/theodora/Documents/SigmodContest/sigmodContest2022/datasets/X1.csv'
    data = pd.read_csv(file_name)
    ids = data.to_dict('list')
    
    file_name2 = '/home/theodora/Documents/SigmodContest/sigmodContest2022/rules/output.csv'
    data2 = pd.read_csv(file_name2)
    id2 = data2.to_dict('list')
    
    couples = []
    num = len(id2['left_instance_id'])
    for index in range(num):
        left = id2['left_instance_id'][index]
        right = id2['right_instance_id'][index]
        posl = ids['id'].index(left)
        posr = ids['id'].index(right)
        couples.append([
            ids['title'][posl], 
            ids['title'][posr]
        ])

    couples = pd.DataFrame(couples)
    name = [
        'title_left',
        'title_right'
    ]
    for i in range(len(name)):
        couples.rename({i: name[i]}, inplace=True, axis=1)

    couples.to_csv("myCouples.csv", sep=',', encoding='utf-8', index=False)
