#!{PYTHON}

import glob
import logging
import os
import sys
import yaml

logger = logging.getLogger('ScriptProgress')
logger.setLevel(logging.INFO)

# setup parameters
with open(sys.argv[1]) as f:
    parameters = yaml.load(f)
aoi = parameters['General']['roi']

# pathnames
s2_l1c_dir = sys.argv[4]
brdf_des_dir = sys.argv[5]
emu_dir = sys.argv[6]
cams_dir = sys.argv[7]
vrt_dem_dir = sys.argv[8]
output_root_dir = sys.argv[9]

vrt_dem_file = glob.glob(vrt_dem_dir+'/'+'*.vrt')[0]
processor_dir = '/software/atmospheric_correction/SIAC'
if not os.path.exists(output_root_dir):
    os.makedirs(output_root_dir)
dirs = glob.glob(s2_l1c_dir + "/*")

for i, directory in enumerate(dirs):
    logger.info(f'{int((i/len(dirs)) * 100)}-{int((i+1/len(dirs)) * 100)}')
    directory_parts = directory.split('/')
    product_name = f"{directory_parts[-1]}-ac"
    print(f'Start pre-processing S2 L1 data from {directory_parts[-2]}')
    output_dir = output_root_dir + '/' + product_name + '/'
    command = "PYTHONPATH=$PYTHONPATH:" + processor_dir + "/util python " + processor_dir + "/SIAC_S2.py -f " \
              + directory + "/ -m " + brdf_des_dir + " -e " + emu_dir + " -c " + cams_dir + " -d " \
              + vrt_dem_file + " -o False" + " -a \'" + aoi + "\'"
    os.system(command)

    output_product_dir = os.path.join(output_root_dir, product_name)
    if not os.path.exists(output_product_dir):
        os.makedirs(output_product_dir)

    cmd2 = "mv $(find " + directory + '/ -type f) ' + output_dir + '/'
    os.system(cmd2)

    cmd3 = "cp `readlink " + directory + "/metadata.xml` " + output_dir + "/metadata.xml"
    os.system(cmd3)
    cmd3 = "cp `readlink " + directory + "/MTD_MSIL1C.xml` " + output_dir + "/MTD_MSIL1C.xml"
    os.system(cmd3)
    paths_to_mtd_tl = glob.glob(os.path.join(directory, 'GRANULE/*/MTD_TL.xml'))
    if len(paths_to_mtd_tl) > 0:
        cmd3 = "cp `readlink " + paths_to_mtd_tl[0] + "` " + output_dir + "/MTD_TL.xml"
    os.system(cmd3)
logger.info('100-100')