import pandas as pd
import json

ls_files = [
    '10_backward.csv',
    '10_forward.csv',
    '11_backward.csv',
    '11_forward.csv',
    '12_backward.csv',
    '12_forward.csv',
    '13_backward.csv',
    '13_forward.csv',
    '16_backward.csv',
    '16_forward.csv',
    '17_backward.csv',
    '17_forward.csv',
    '1_backward.csv',
    '1_forward.csv',
    '20_backward.csv',
    '20_forward.csv',
    '21_backward.csv',
    '21_forward.csv',
    '22_backward.csv',
    '22_forward.csv',
    '23_backward.csv',
    '23_forward.csv',
    '24_backward.csv',
    '24_forward.csv',
    '25_backward.csv',
    '25_forward.csv',
    '26_backward.csv',
    '26_forward.csv',
    '27_backward.csv',
    '27_forward.csv',
    '29_backward.csv',
    '29_forward.csv',
    '2_backward.csv',
    '2_forward.csv',
    '30_backward.csv',
    '30_forward.csv',
    '31_backward.csv',
    '31_forward.csv',
    '32_backward.csv',
    '32_forward.csv',
    '34_backward.csv',
    '34_forward.csv',
    '35_backward.csv',
    '35_forward.csv',
    '36_backward.csv',
    '36_forward.csv',
    '37_backward.csv',
    '37_forward.csv',
    '3_backward.csv',
    '3_forward.csv',
    '4_backward.csv',
    '4_forward.csv',
    '5_backward.csv',
    '5_forward.csv',
    '7_forward.csv',
    '7_backward.csv',
    '8_backward.csv',
    '8_forward.csv',
    '9_backward.csv',
    '9_forward.csv'
]

ls_files_json = [
    '10_backward.json',
    '10_forward.json',
    '11_backward.json',
    '11_forward.json',
    '12_backward.json',
    '12_forward.json',
    '13_backward.json',
    '13_forward.json',
    '16_backward.json',
    '16_forward.json',
    '17_backward.json',
    '17_forward.json',
    '1_backward.json',
    '1_forward.json',
    '20_backward.json',
    '20_forward.json',
    '21_backward.json',
    '21_forward.json',
    '22_backward.json',
    '22_forward.json',
    '23_backward.json',
    '23_forward.json',
    '24_backward.json',
    '24_forward.json',
    '25_backward.json',
    '25_forward.json',
    '26_backward.json',
    '26_forward.json',
    '27_backward.json',
    '27_forward.json',
    '29_backward.json',
    '29_forward.json',
    '2_backward.json',
    '2_forward.json',
    '30_backward.json',
    '30_forward.json',
    '31_backward.json',
    '31_forward.json',
    '32_backward.json',
    '32_forward.json',
    '34_backward.json',
    '34_forward.json',
    '35_backward.json',
    '35_forward.json',
    '36_backward.json',
    '36_forward.json',
    '37_backward.json',
    '37_forward.json',
    '3_backward.json',
    '3_forward.json',
    '4_backward.json',
    '4_forward.json',
    '5_backward.json',
    '5_forward.json',
    '7_forward.json',
    '7_backward.json',
    '8_backward.json',
    '8_forward.json',
    '9_backward.json',
    '9_forward.json'
]

rom_eng = {
    'â': 'a',
    'ş': 's',
    'ţ': 't',
    'ă': 'a'
}


def load_route_with_order(route_name: str, direction: int, day: str):
    file = route_name
    if direction == 0:
        file = file + '_forward_'
    else:
        file = file + '_backward_'

    df = pd.read_csv('schedules/' + file)
    if day == 'WORKWEEK':
        return df['Luni - Vineri'].tolist()
    if day == 'SATURDAY':
        return df['Sambata'].tolist()
    if day == 'SUNDAY':
        return df['Duminica'].tolist()

    return None


def convert_to_csv() -> None:
    for file in ls_files_json:
        with open('schedules/' + file, 'r') as f:
            d = json.loads(f.read())
            df = pd.DataFrame(columns=d.keys())
            for k in d.keys():
                vals = d[k]
                strs = []
                for x in vals:
                    if (len(x[1]) == 1):
                        x[1] = '0' + x[1]
                    strs.append(x[0] + ":" + x[1])
                df[k] = pd.Series(strs)
            df.to_csv('schedules/' + file.split(".")[0] + ".csv")


convert_to_csv()
