#!{PYTHON}

import glob
import os
import sys
import time


configuration_file = sys.argv[1]
input_dir = sys.argv[2]
output_dir = sys.argv[3]

input_files = glob.glob(input_dir + '/*.txt')

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for input_file in input_files:
    input_file = input_file.replace('\\', '/')
    input_file_blank = input_file.split('/')[-1].replace('.txt', '')
    with open(input_file, 'r') as in_f:
        file_name = f'{output_dir}/{input_file_blank}_2.txt'
        print(f'Writing out {file_name}')
        with open(file_name, 'w+') as out_f:
            in_line = in_f.readline()
            print(in_line)
            out_f.write(f'{in_line}_2')
            out_f.close()
