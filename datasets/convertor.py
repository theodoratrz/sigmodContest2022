import pandas as pd
import re

Flag = True

if __name__ == '__main__':
    file_name = 'X1.csv'
    data = pd.read_csv(file_name)
    ids = data.to_dict('list')
    
    file_name2 = 'Y1.csv'
    data2 = pd.read_csv(file_name2)
    id2 = data2.to_dict('list')
    
    couples = []
    num = len(id2['lid'])
    for index in range(len(id2['lid'])):
        left = id2['lid'][index]
        right = id2['rid'][index]
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

    couples.to_csv("couples_titles.csv", sep=',', encoding='utf-8', index=False)
