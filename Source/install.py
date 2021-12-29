import subprocess
import os.path
import sys
import zipfile
import configparser
import datetime
import shutil

import UpdateMaster
from procs import check_dir_file, check_version, parts_to_run, get_newest_file

# cd C:\Users\ABenhida\Documents\Test1\Source
# run on powershell: C:\Users\ABenhida\AppData\Local\Programs\Python\Python310\python.exe .\install.py

# start timer
start_time = datetime.datetime.now()
print(f'======= start time {start_time} ================')

# Read the input dictionary to for config
config = configparser.RawConfigParser()
config.read('../Configurations/config.ini')
fhmas = open('../Configurations/master_prop_dict.txt')

# where the batch "bat' files reside
loc_bat = config.get('common info', 'loc_bat')

site_code = config.get('common info', 'site_code')
site_name = config.get('common info', 'site_name')
site = f'{site_code}-{site_name}'

disk_target = config.get('common info', 'disk_target')

version = config.get('common info', 'version')
MM, NN, B = version.split('.')

download_folder = config.get('common info', 'download_folder')

master_file = 'master-property-template.properties'
config_loc = f'{disk_target}:\\{MM}.{NN}\\staging\\rel-{MM}-{NN}\\config'
master_dir = f'{disk_target}:\\{MM}.{NN}\\staging\\rel-{MM}-{NN}\\{site}'
wildfly_version = config.get('common info', 'wildfly_version')
keycloak_version = config.get('common info', 'keycloak_version')
# this one is for me I set it to unzip to my C: drive
db_target_zip = f"{config.get('common info', 'disk_target')}:\\{site}.{B}_unzipped_db"

# find out the the sections of the script to run
parts = parts_to_run("../Utilities/run_parts.json")
if not parts:
    print('no data read - what parts to run, exiting .. ')
    sys.exit()
#
print('... Checking the ".bat" files exist for pre-base, pre-rel, refresh')
checkThese = {f'{loc_bat}download-pre-base-{version}.bat': 'file', f'{loc_bat}download-pre-release-{version}.bat': 'file',
          f'{loc_bat}refresh-{version}.bat': 'file'}
if not check_dir_file(checkThese):
    print(f'download batch files do not exist in: {loc_bat}')
    sys.exit()

# ------------------------------------------------
if parts['run_pre_base_bat']:
    print (f'..... running {loc_bat} download-pre-base-{version}.bat, please wait ......')
    output = subprocess.getoutput(loc_bat+f"download-pre-base-{version}.bat")
    print('output:', output)
    print('------- No need to check for errors here -----------------')
#
print('\n....>  Verify the existance of these directories/files\n')
checkThese = {f'{disk_target}:/{MM}.{NN}/AppTools': 'dir',
          f'{disk_target}:/{MM}.{NN}/AppServers/{wildfly_version}-CE.zip': 'file',
          f'{disk_target}:/{MM}.{NN}/AppServers/{keycloak_version}-CE.zip': 'file',
          f'{disk_target}:/{MM}.{NN}/keycloak/KEYCLOAK-{MM}-{NN}.DMP': 'file'}

print(f'Check dir & files exist:{ check_dir_file(checkThese)}, {checkThese}')

#
# ------------------------------------------------
if parts['run_pre_release_bat']:
    print(f'..... running {loc_bat}download-pre-release-{version}.bat, please wait ......')
    output = subprocess.getoutput(loc_bat+f"download-pre-release-{version}.bat")
    print('output:', output)
    #
    f_version = f'{disk_target}:\\{MM}.{NN}\\{MM}.{NN}.{B}\\GWInstall\\rel-{MM}-{NN}\\version.txt'
    checkThese = {f'{f_version}': 'file'}
    print (f'Check dir & files exist:{ check_dir_file(checkThese)}, {checkThese}')

    # Verify version format
    if not check_version(f_version, version):
      print(f'.... Wrong version format {version}, expecting {version}')
      sys.exit()
    print(f'.... correct version format {version}, same as expected: {version}')

# ------------------------------------------------
# Refresh staging directory on admin Gateway server
if parts['run_refresh_bat']:
    print(f'... running {loc_bat} refresh-{version}.bat, please wait ....')
    output = subprocess.getoutput(loc_bat+f"refresh-{version}.bat")
    print('output:', output)

    #
    checks = {f'{disk_target}:/{MM}.{NN}/staging/rel-{MM}-{NN}/version.txt': 'dir'}
    f = f'{disk_target}:/{MM}.{NN}/staging/rel-{MM}-{NN}/version.txt'
    print(check_version(f, version))

# ------------------------------------------------
master_new_loc = f'{disk_target}:\\{MM}.{NN}\\staging\\rel-{MM}-{NN}\\{site}\\'
if parts['create_deployment_dir']:
    print('.... Creating client deployment directory, and copy master property ....')
    path = f'{disk_target}:/{MM}.{NN}/staging/rel-{MM}-{NN}/{site}'

    try:
        os.mkdir(path)
        print('.... Directory created ...')
    except OSError as error:
        print(f'....... Error creating directory:{error}, I will continue with existing dir')
        #sys.exit()  -- don't exit, continue, exits already
    print(f'  {path}')

    master_orig_loc = f"{disk_target}:\\AppServers\\{wildfly_version}\\standalone\\data\\ce\\config\\master-config\\"
    #master_new_loc = f'{disk_target}:\\{MM}.{NN}\\staging\\rel-{MM}-{NN}\\{site}\\'

    output = subprocess.getoutput(f'copy {master_orig_loc}{master_file} {master_new_loc}{master_file}')
    print('output:', output)


#-------------------------------------------------
if parts['decrypt_master_prop']:
    # c.    Go to E:\MM.NN\staging\rel-MM-NN\config
    print(f'changing directory to:{config_loc} ->:{os.chdir(config_loc)}')
    if os.getcwd() != config_loc:
        print(f'.... I am not at the right directory, config_loc:{config_loc}')
        sys.exit()
    print(f'++ curent directory:{os.getcwd()}, running decryption')
    output = subprocess.getoutput('decrypt-master-prop.cmd ..\\'+site)
    print('output:', output)

''' 
------------------------------------------------------------------------------------
Now time to to merge your master prop file using Support Tool (ST)
    Once you click download, it gets downloaded to "download" folder
moving the master prop from "download" folder to "7447-Ahmed" as example here
------------------------------------------------------------------------------------
'''
downloaded_file = download_folder+"master-property*"
if parts['move_master_prop_downloaded_from_ST']:
    print(f'... moving the master prop from file: {downloaded_file}')
    f_n_p_downlded = get_newest_file(downloaded_file)
    if not f_n_p_downlded:
        print(f'master prop files does not exist in: {download_folder}')
        sys.exit()
    new_master_prop = f'master-pro{f_n_p_downlded.split("master-pro")[1]}'
    try:
        shutil.copy(f'{f_n_p_downlded}', f'{master_new_loc}\\{master_file}')
    except EnvironmentError:
        print(f".... Error moving TS downloaded master template to: {master_new_loc} ")
    else:
        print(f".... TS downloaded master template file moved to: {master_new_loc} ")

'''
------------------------------------------------------------------------------------
now the master property file is decrypted so you can modify it.
Modify the property file

 i.e.  Check the following file and it should be decrypted:
       E:\MM.NN\staing\rel-MM-NN\XXXX-ClientA\master-property-template.properties
------------------------------------------------------------------------------------
'''
if parts['run_master_prop_population']:
    print('==========> running master properties file population ==========')
    # now I need to modify master template properties file
    d = {}
    UpdateMaster.UpdateMaster.load_dictionary(fhmas, d)
    master_dest = master_dir+"\\master-property-template.properties"
    print("$$$$$$ whereTo_mast:", master_dest)
    UpdateMaster.UpdateMaster.modify_master(master_dest, d)
    fhmas.close()
'''
------------------------------------------------------------------------------------
Copy the merged master property files to the admin Gateway server at:
E:\MM.NN\staing\rel-MM-NN\XXXX-ClientA\master-property-template.properties
------------------------------------------------------------------------------------
'''
if parts['run_master_prop_config']:
    print('==========> running master properties config ===============')
    # Run the config now that master.property has been updated
    # E:\MM.NN\staging\rel-MM-NN\config>config ..\XXXX-ClientA
    print(f'changing directory to:{config_loc} ->:{os.chdir(config_loc)}')
    if os.getcwd() != config_loc:
        print(f'.... not at the right directory, config_loc:{config_loc}, curdir:{os.getcwd()}, quiting')
        sys.exit()
    print(f'...... I am at: {os.getcwd()}. running the config for master.property file ... ')
    output = subprocess.getoutput('config.cmd ..\\'+site)
    print('output:', output)

'''
------------------------------------------------------------------------------------
Verify E:\MM.NN\staging\rel-MM-NN\XXXX-ClientA\MM.NN.EE_MMDDYYYY-HHMISS
this one to figure out, as it will be generated later
sometimes old versions are there too, I need to find the latest.
call a function to do that ....
------------------------------------------------------------------------------------
'''
db_versions_path = f'{disk_target}:\\{MM}.{NN}\\staging\\rel-{MM}-{NN}\\{site}\\{version}_*'
# first find the latest file:
db_source_zip = get_newest_file(db_versions_path)
print(f'db_source_zip:{db_source_zip} , db unzip target:{db_target_zip}')
if db_source_zip == None:
    print(f'db versions directory not found at: {db_source_zip}')
    sys.exit()

'''
------------------------------------------------------------------------------------
this will unzip the zip file to the folder "zipF"
if that zipF already  has files/folders it will update them
if the folder "zipF" not there it will create it
first find the latest file:
------------------------------------------------------------------------------------
'''
if parts['unzip_database']:
    dbase_source_zip = f'{db_source_zip}\\zips\\database.zip'
    with zipfile.ZipFile(dbase_source_zip, "r") as zip_ref:
        zip_ref.extractall(db_target_zip)
    print(f'... database files are unzipped to:{db_target_zip}')

if parts['unzip_wildfly']:
    zip_source = f'{disk_target}:\\{MM}.{NN}\\AppServers\\{wildfly_version}-CE.zip'
    target_zip = f'{disk_target}:\\AppServers\\{wildfly_version}'

    print(f'Unzip the {zip_source} to:{target_zip}')
    with zipfile.ZipFile(zip_source, "r") as zip_ref:
        zip_ref.extractall(target_zip)
    print(f'... database files are unzipped to:{target_zip}')


if parts['unzip_keycloak']:
    zip_source = f'{disk_target}:\\{MM}.{NN}\\AppServers\\{keycloak_version}-CE.zip'
    target_zip = f'{disk_target}:\\AppServers\\{keycloak_version}'

    print(f'Unzip the {zip_source} to:{target_zip}')
    with zipfile.ZipFile(zip_source, "r") as zip_ref:
        zip_ref.extractall(target_zip)
    print(f'... database files are unzipped to:{target_zip}')

# to continue ..
zips_target = f'E:\\17.0\\GWInstall\\releases\\{MM}.{NN}.{B}'

Orig_zip = f'{db_source_zip}\\zips\\QAAP{site_code}'
zip_source = f'{Orig_zip}\\QAAP{site_code}-install.zip'
zip_target = f'{zips_target}\\QAAP{site_code}-install'

# check first if it exists already
if parts['create_GWInstall_dir']:
    path = f'{disk_target}:/{MM}.{NN}/GWInstall/releases/{MM}.{NN}.{B}'
    try:
        os.mkdir(path)
        print('.... Directory created ...')
    except OSError as error:
        print(f'....... Error creating directory:{error}')
        #sys.exit()
    print(f'.... directory created at :{path}')

    '''
    Example (not real paths):
    go to: (E:\17.0\staging\rel-17-0\7446-Ahmed\17.0.42_20211005-191134\zips\QAAP7446
    Copy [admin hostname].zip and [admin hostname].zip.MD5 to E:\17.0\GWInstall\releases\17.0.xx 
    Copy [admin hostname]-install.zip and [admin hostname]-install.zip.MD5 to E:\17.0\GWInstall\releases\17.0.xx 
    Copy auth-server.zip and auth-server.zip.MD5 to E:\17.0\GWInstall\releases\17.0.xx
    '''
    # we can make this more variable putting it in ini.config
    print(f'--> zips_target:{zips_target}, Orig_zip:{Orig_zip}')
    output = subprocess.getoutput(f'copy {Orig_zip}* {zips_target}')
    print('output:', output)

    '''
    Install admin Gateway server and Keycloak server 
    extract-all [admin hostname]-install.zip to E:\17.0\GWInstall\releases\17.0.42\[admin hostname]-install  
    '''
    with zipfile.ZipFile(zip_source, "r") as zip_ref:
        zip_ref.extractall(zip_target)
    print(f'... QAAP{site_code}-install.zip files are unzipped to:{zip_target}')

'''
------------------------------------------------------------------------------------
Gateway installation - time to run the install-all.bat script
------------------------------------------------------------------------------------
'''
if parts['run_GWInstall_config']:

    '''
    Go to E:\17.0\GWInstall\releases\17.0.42\[admin hostname]-install
    cd E:\17.0\GWInstall\releases\17.0.42\QAAP7446-install    
    '''
    print(f'changing directory to:{zip_target} ->:{os.chdir(zip_target)}')
    if os.getcwd() != zip_target:
        print(f'.... I am not at the right directory, config_loc:{zip_target}')
        sys.exit()
    print(f'++ curent directory:{os.getcwd()}, running gateway Installation ...., please wait.')
    output = subprocess.getoutput('install-all.bat')
    print('output:', output)


# ----------------------------------------------------------------------------------------------

# time the execution took
print(f'=========  all done\n It took:{datetime.datetime.now() - start_time} for this to run ============')