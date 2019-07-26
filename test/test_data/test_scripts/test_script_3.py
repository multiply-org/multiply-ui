#!{PYTHON}

import glob
import os
import sys


configuration_file = sys.argv[1]
input_dir = sys.argv[2]
output_dir = sys.argv[3]

input_files = glob.glob(input_dir + '/*.txt')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for input_file in input_files:
    input_file = input_file.replace('\\', '/')
    input_file_blank = input_file.split('/')[-1].replace('_2.txt', '')
    with open(input_file, 'r') as in_f:
        file_name = f'{output_dir}/{input_file_blank}_3.txt'
        print(f'Writing out {file_name}')
        with open(file_name, 'w+') as out_f:
            in_line = in_f.readline()
            out_f.write(f'{in_line}_3')
            out_f.close()
