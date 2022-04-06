import pandas as pd
import re

brands = ['dell', 'lenovo', 'acer', 'asus', 'hp']

cpu_brands = ['intel', 'amd']

intel_cores = [' i3', ' i5', ' i7', '2 duo', 'celeron', 'pentium', 'centrino']
amd_cores = ['e-series', 'a8', 'radeon', 'athlon', 'turion', 'phenom']

families = {
    'hp': [r'elitebook', r'compaq', r'folio', r'pavilion'],
    'lenovo': [r' x[0-9]{3}[t]?', r'x1 carbon'],
    'dell': [r'inspiron'],
    'asus': [r'zenbook', ],
    'acer': [r'aspire', r'extensa', ],
    '0': []
}

trash = [ "amazon",
                "alibaba",
                "com:",
                "\d+ ?[Tt][Bb]",
                "hdd",
                "ssd",
                "vology",
                "downgrade",
                "brand new",
                "laptops",
                "laptop",
                "pc",
                "computers",
                "china",
                "buy",
                "famous,",
                "australia",
                "accessories",
                "wireless lan",
                "wifi",
                "wholeshale"
                "win(dows)? (xp|7|8.1|8|10)( pro(fessional)?| home premium)? ?((64|32)-bit)?",
                "notebook",
                "led",
                "ips",
                "processor",
                "core",
                "[\(\):&]",
                "\"",
                "''",
                ",",
                "-",
                " +$",
                "\|",
                "e[Bb]ay",
                "webcam",
                "best",
                "and",
                "kids",
                "bit",
                "win",
                "com",
                "general",
                "linux",
                "cheap",
                "inch",
                "with",
                "great",
                "product",
                "dvdrw",
                "quality"
        ]

def clean_X1(data):
    ids = data.filter(items=['id'], axis=1)
    ids = data.values.tolist()
    title = data.drop(['id'], axis=1)
    title = title.fillna('')
    title = title.values.tolist()
    splitted_list = []

    for row in range(len(ids)):
        temp = title[row][0].lower()
        information = temp.split()

        brand = '0'
        cpu_brand = '0'
        cpu_core = '0'
        cpu_model = '0'
        cpu_frequency = '0'
        ram_capacity = '0'
        display_size = '0'
        name_number = '0'
        name_family = '0'

        row_info = ""
        for name in information:
            row_info = row_info + " " + name

        for b in brands:
            if b in information:
                brand = b
                break

        for b in cpu_brands:
            if b in information:
                cpu_brand = b
                break

        result_frequency = re.search(
            r'[123][ .][0-9]?[0-9]?[ ]?[Gg][Hh][Zz]', row_info)
        if result_frequency is not None:
            result_frequency = re.split(r'[GgHhZz]', result_frequency.group())[
                0].strip().replace(' ', '.')
            if len(result_frequency) == 3:
                result_frequency = result_frequency + '0'
            if len(result_frequency) == 1:
                result_frequency = result_frequency + '.00'
            result_frequency = result_frequency
            cpu_frequency = result_frequency
        

        for f in families:
            if f in information:
                name_family = f

        if cpu_brand != 'intel':
            for b in amd_cores:
                if b in row_info:
                    cpu_core = b.strip()
                    cpu_brand = 'amd'
                    break
        if cpu_brand != 'amd':
            for b in intel_cores:
                if b in row_info:
                    cpu_core = b.strip()
                    cpu_brand = 'intel'
                    break

        if cpu_brand == 'intel':
            result_model = re.search(
                r'[\- ][0-9]{4}[Qq]?[MmUu](?![Hh][Zz])', row_info)
            if result_model is None:
                result_model = re.search('[\\- ][0-9]{3}[Qq]?[Mm]', row_info)
            if result_model is None:
                result_model = re.search('[\\- ][MmQq][0-9]{3}', row_info)
            if result_model is None:
                result_model = re.search('[\\- ][PpNnTt][0-9]{4}', row_info)
            if result_model is None:
                result_model = re.search('[\\- ][0-9]{4}[Yy]', row_info)
            if result_model is None:
                result_model = re.search('[\\- ][Ss]?[Ll][0-9]{4}', row_info)
            if result_model is None:
                result_model = re.search('[\\- ]867', row_info)
            if result_model is None:
                result_model = re.search(
                    '[\\- ]((1st)|(2nd)|(3rd)|([4-9]st))[ ][Gg]en', row_info)
            if result_model is not None:
                cpu_model = result_model.group()[1:].lower()
            elif cpu_brand == 'amd':
                if cpu_core == 'a8':
                    cpu_core = 'a-series'
                result_model = re.search(r'([AaEe][0-9][\- ][0-9]{4})', row_info)
                if result_model is None:
                    result_model = re.search('[\\- ]HD[\\- ][0-9]{4}', row_info)
                if result_model is None:
                    result_model = re.search('[\\- ][AaEe][\\- ][0-9]{3}', row_info)
                if result_model is not None:
                    cpu_core = result_model.group()[:1].lower() + '-series'
                    cpu_model = result_model.group()[1:].lower().replace(' ', '-')
                if cpu_core in ('radeon', 'athlon', 'turion', 'phenom'):
                    if result_model is None:
                        result_model = re.search('[\\- ][NnPp][0-9]{3}', row_info)
                    if result_model is None:
                        result_model = re.search(
                            '[\\- ](64[ ]?[Xx]2)|([Nn][Ee][Oo])', row_info)
                    if result_model is not None:
                        cpu_model = result_model.group().lower().replace('-', '').replace(' ', '')

            if brand == 'lenovo':
                result_name_number = re.search(
                    r'[\- ][0-9]{4}[0-9a-zA-Z]{3}(?![0-9a-zA-Z])', row_info)
                if result_name_number is None:
                    result_name_number = re.search(
                        r'[\- ][0-9]{4}(?![0-9a-zA-Z])', row_info)
                if result_name_number is not None:
                    name_number = result_name_number.group().replace(
                        '-', '').strip().lower()[:4]
            elif brand == 'hp':
                result_name_number = re.search(r'[0-9]{4}[pPwW]', row_info)
                if result_name_number is None:
                    result_name_number = re.search(
                        r'15[\- ][a-zA-Z][0-9]{3}[a-zA-Z]{2}', row_info)
                if result_name_number is None:
                    result_name_number = re.search(r'[\s]810[\s](G2)?', row_info)
                if result_name_number is None:
                    result_name_number = re.search(r'[0-9]{4}[mM]', row_info)
                if result_name_number is None:
                    result_name_number = re.search(
                        r'((DV)|(NC))[0-9]{4}', row_info)
                if result_name_number is None:
                    result_name_number = re.search(r'[0-9]{4}DX', row_info)
                if result_name_number is not None:
                    name_number = result_name_number.group().lower().replace('-', '').replace(' ', '')
            elif brand == 'dell':
                result_name_number = re.search(
                    r'1[57][Rr]?[\s]?([0-9]{4})?[\s]([iI])?[0-9]{4}', row_info)
                if result_name_number is None:
                    result_name_number = re.search(
                        r'[\s][A-Za-z][0-9]{3}[A-Za-z][\s]', row_info)
                if result_name_number is not None:
                    name_number = result_name_number.group().lower().replace(
                        '-', '').replace('i', '').strip().split(' ')[-1]
            elif brand == 'acer':
                result_name_number = re.search(
                    r'[A-Za-z][0-9][\- ][0-9]{3}', row_info)
                if result_name_number is None:
                    result_name_number = re.search(r'AS[0-9]{4}', row_info)
                if result_name_number is None:
                    result_name_number = re.search(
                        r'[0-9]{4}[- ][0-9]{4}', row_info)
                if result_name_number is not None:
                    name_number = result_name_number.group().lower().replace(' ', '-').replace('-', '')
                    if len(name_number) == 8:
                        name_number = name_number[:4]
            elif brand == 'asus':
                result_name_number = re.search(
                    r'[A-Za-z]{2}[0-9]?[0-9]{2}[A-Za-z]?[A-Za-z]', row_info)
                if result_name_number is not None:
                    name_number = result_name_number.group().lower().replace(' ', '-').replace('-', '')

        if brand == 'lenovo':
            result_name_number = re.search(
                r'[\- ][0-9]{4}[0-9a-zA-Z]{3}(?![0-9a-zA-Z])', name)
            if result_name_number is None:
                result_name_number = re.search(
                    r'[\- ][0-9]{4}(?![0-9a-zA-Z])', name)
            if result_name_number is not None:
                name_number = result_name_number.group().replace(
                    '-', '').strip().lower()[:4]
        elif brand == 'hp':
            result_name_number = re.search(r'[0-9]{4}[pPwW]', name)
            if result_name_number is None:
                result_name_number = re.search(
                    r'15[\- ][a-zA-Z][0-9]{3}[a-zA-Z]{2}', name)
            if result_name_number is None:
                result_name_number = re.search(r'[\s]810[\s](G2)?', name)
            if result_name_number is None:
                result_name_number = re.search(r'[0-9]{4}[mM]', name)
            if result_name_number is None:
                result_name_number = re.search(
                    r'((DV)|(NC))[0-9]{4}', name)
            if result_name_number is None:
                result_name_number = re.search(r'[0-9]{4}DX', name)
            if result_name_number is not None:
                name_number = result_name_number.group().lower().replace('-', '').replace(' ', '')
        elif brand == 'dell':
            result_name_number = re.search(
                r'1[57][Rr]?[\s]?([0-9]{4})?[\s]([iI])?[0-9]{4}', name)
            if result_name_number is None:
                result_name_number = re.search(
                    r'[\s][A-Za-z][0-9]{3}[A-Za-z][\s]', name)
            if result_name_number is not None:
                name_number = result_name_number.group().lower().replace(
                    '-', '').replace('i', '').strip().split(' ')[-1]
        elif brand == 'acer':
            result_name_number = re.search(
                r'[A-Za-z][0-9][\- ][0-9]{3}', name)
            if result_name_number is None:
                result_name_number = re.search(r'AS[0-9]{4}', name)
            if result_name_number is None:
                result_name_number = re.search(
                    r'[0-9]{4}[- ][0-9]{4}', name)
            if result_name_number is not None:
                name_number = result_name_number.group().lower().replace(' ', '-').replace('-', '')
                if len(name_number) == 8:
                    name_number = name_number[:4]
        elif brand == 'asus':
            result_name_number = re.search(
                r'[A-Za-z]{2}[0-9]?[0-9]{2}[A-Za-z]?[A-Za-z]', name)
            if result_name_number is not None:
                name_number = result_name_number.group().lower().replace(' ', '-').replace('-', '')

        flag = 0
        information.sort()
        
        if len(information) > 6:
            flag = 1
        if len(information) > 12:
            flag = 2
        
        clean_info = ''
        sorted_title = ''
        for name in information:
            sorted_title = sorted_title + " " + name
            if name not in trash:
                clean_info = clean_info + " " + name
        
        res = re.sub(r'[^\w\s]', '', clean_info)
        res1 = re.sub(r'[^\w\s]', '', sorted_title)
        splitted_list.append([
            ids[row][0],
            brand,
            cpu_brand,
            cpu_core,
            cpu_model,
            cpu_frequency,
            name_number,
            name_family,
            row_info,
            flag,
            res,
            res1
        ])

    splitted_list = pd.DataFrame(splitted_list)
    name = [
        'instance_id',
        'brand',
        'cpu_brand',
        'cpu_core',
        'cpu_model',
        'cpu_frequency',
        'pc_name',
        'family',
        'title',
        'flag',
        'clean_info',
        'sorted_title'
    ]
    for i in range(len(name)):
        splitted_list.rename({i: name[i]}, inplace=True, axis=1)
    splitted_list.to_csv("cleaning_data.csv", sep=',', encoding='utf-8', index=False)
    return splitted_list
        