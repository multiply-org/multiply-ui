import datetime
import os
import sys


configuration_file = sys.argv[1]
start_date = sys.argv[2]
stop_date = sys.argv[3]
output_dir = sys.argv[4]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

step = datetime.timedelta(days=2)

date = start_date
count = 1

while date < stop_date:
    with open(f'{output_dir}/{date.year}_{date.month}_{date.day}.txt', 'w+') as f:
        f.write('{count}')
        f.close()
        date += step
        count += 1
