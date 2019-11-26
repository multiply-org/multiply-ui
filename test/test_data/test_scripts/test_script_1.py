#!{PYTHON}

import datetime
import os
import sys


configuration_file = sys.argv[1]
start_date = datetime.datetime.strptime(sys.argv[2], '%Y-%m-%d')
stop_date = datetime.datetime.strptime(sys.argv[3], '%Y-%m-%d')
output_dir = sys.argv[4]
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

step = datetime.timedelta(days=2)

date = start_date
count = 1

while date < stop_date:
    file_name = f'{output_dir}/{date.year}_{date.month}_{date.day}.txt'
    print(f'Writing out {file_name}')
    with open(file_name, 'w+') as f:
        f.write(f'{count}')
        f.close()
        date += step
        count += 1
