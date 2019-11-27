#!{PYTHON}
# prepro_hres2.py request_test_all.yaml /data/m3/inputs /data/auxiliary/brdf_des /data/m3/sdrs
# /Data/m3/inputs/highres/S2/30/S/WJ/2017/11/10/0

import os
import sys
import yaml
import glob
import pdb

# setup parameters
with open(sys.argv[1]) as f:
    parameters = yaml.load(f)
aoi = parameters['General']['roi']
processor_dir = '/software/atmospheric_correction_2.2.0/SIAC'

# pathnames
input_root = sys.argv[2]
brdf_des_dir = sys.argv[3]
emu_dir = sys.argv[4]
cams_dir = sys.argv[5]
vrt_dem_dir = sys.argv[6]
output_root_dir = sys.argv[7]

vrt_dem_file = glob.glob(vrt_dem_dir+'/'+'*.vrt')[0]
#s2_wv_dir = "/data/archive/emulators/s2_wv"
#s2_atcor_dir = "/data/archive/emulators/s2_atcor"
#cams_dir = "/data/auxiliary/cams"
working_dir = os.getcwd()

if not os.path.exists(output_root_dir):
    os.makedirs(output_root_dir)

#os.system("ln -s"+processor_dir+"/data ./data")

# derive proper names for input_dir and products
dirs = glob.glob(input_root + "/*/*/*/*/*/*/*")
for dir in dirs:
   input_dir = dir[len(input_root)+1:]
   input_parts = input_dir.split('/')
   product_name = "S2-" + input_parts[-7] + input_parts[-6] + input_parts[-5]  + input_parts[-4] + "-" +  input_parts[-3] + "-" +  input_parts[-2]

# create directories
#if not os.path.exists(input_dir):
#    os.makedirs(input_dir)
#if not os.path.exists(brdf_des_dir):
#    os.makedirs(brdf_des_dir)
#if not os.path.exists(output_root_dir):
#    os.makedirs(output_root_dir)

# setup working directory
# pwd  = os.getcwd
#os.system("ln -s " + input_root + "/" + input_dir + "/* "+input_dir+"/.")
#print(input_dir)
#print(output_root_dir)
#os.system("ln -s "+processor_dir+"/data ./data")

#code to integrate some methods from specific files (this can be made cleaner)
#-d /Data/auxiliary/dem/aster/aster-global.vrt
#s2_wv_dir = "/data/archive/emulators/s2_wv"
#s2_atcor_dir = "/data/archive/emulators/s2_atcor"
#cams_dir = "/data/auxiliary/cams"
   os.system("PYTHONPATH=$PYTHONPATH:"+processor_dir+"/util python "+processor_dir+"/SIAC_S2.py -f "+input_root+'/'+input_dir+"/ -m "+ brdf_des_dir + " -e "+emu_dir+" -c "+cams_dir + " -d "+vrt_dem_file+" -o False -a \'"+aoi+"\'")

   if not os.path.exists(output_root_dir+'/'+product_name+'/'):
       os.makedirs(output_root_dir+'/'+product_name+'/')

   #os.system('mkdir '+output_root_dir+'/'+product_name+'/')
   os.system("mv $(find "+input_root+'/'+input_dir+'/ -type f) '+output_root_dir+'/'+product_name+'/')
   os.system("cp `readlink "+input_root+'/'+input_dir+"/metadata.xml` "+output_root_dir+"/"+product_name+'/metadata.xml')
   #os.system("rm $(find "+input_root+'/'+input_dir+" -type l)")
   #call = "mv "+input_root+'/'+input_dir+"/ "+output_root_dir+"/" + product_name
    #print(call)
   #os.system(call)
   #os.system("rm -r "+input_parts[0])
   #os.system("rm $(find . -type l)")
