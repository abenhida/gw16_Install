import os
import shutil as sh
import configparser
import UpdateMaster

# Read the input dictionary to for config
config = configparser.RawConfigParser()
config.read('../Configurations/config.ini')

site = config.get('common info', 'site_name')
code = config.get('common info', 'site_code')
site_dir = config.get('common info', 'build_site_dir')
master_prop_loc = config.get('common info', 'master_prop_loc')

dest_dir = '{}{}-{}'.format(site_dir, site, code)

# creating new site directory if it does not exist
if not os.path.exists(dest_dir):
    print ("*** I could not find the path ****")
    os.mkdir(dest_dir)
    print("**** created dir:", dest_dir)

# now copy the master template file to the new directory
# check first if thr destination directory exists
if not os.path.exists(dest_dir):
    print('**** Destination directory does not exist - create it first')
    exit(0)
master_orig_loc = master_prop_loc+"master-property-template.properties.txt"
print('**** master_orig_loc:{}, dest_dir:{}'.format(master_orig_loc, dest_dir))
sh.copy2(master_orig_loc, dest_dir)
print('**** File copied:', master_orig_loc+"master-property-template.properties")

# now I need to modify master template properties file
print('**** calling class updateMaster')
fh = open('../Configurations/master_prop_dict.txt')
d = {}

UpdateMaster.UpdateMaster.load_dictionary(fh, d)
print('******* d:', d)

whereTo_mast = dest_dir+"/master-property-template.properties.txt"
print("$$$$$$ whereTo_mast:", whereTo_mast)

UpdateMaster.UpdateMaster.modify_master(whereTo_mast, d)
