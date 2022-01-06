import os.path
import json
import re
import glob
import sys
import subprocess
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

from selenium.webdriver.support import wait

'''
this proc verifies if the directory or file exists as it is supposed to
returns 0/1
'''


def check_dir_file(checks):
    check_pass = 1
    for i in checks.keys():
        if checks[i] == 'file':
            if os.path.isfile(i):
                print(f'... Exists: {i}')
            else:
                print(f'... Does not Exist: {i}')
                check_pass = 0

        if checks[i] == 'dir':
            if os.path.isdir(i):
                print(f'... Directory Exists: {i}')
            else:
                print(f'... Directory Does not Exist: {i}')
                check_pass = 0
    return check_pass


'''
This proc verifies the version downloaded in a file "f", if it is the one supposed to download
returns 1 if correct version, 0 if not
'''


def check_version(f, version):
    fh_version = open(f, "r")
    readfile = fh_version.read()
    result = 1 if version in readfile else 0
    fh_version.close()
    print(f'...... version in file result:{result}')
    return result


'''
This proc dictates which parts of the scripts to run
the script is broken into parts that can run individually
or collectively.
These parts can be found and modified in run_parts.json file
'''


def parts_to_run(file):
    print(file)
    with open(file) as f:
        dat = json.load(f)
        print(dat)
    return dat


'''
this proc returns the latest file in a directory
as there will be a file/files created on the fly and differ by timestamp
like xxx_20211122-203653\\zips\\database.zip
either returns "None" or latest file
'''


def get_newest_file(path):
    list_of_files = glob.glob(path)
    try:
        x = max(list_of_files, key=os.path.getctime)
        return x
    except ValueError:
        return None


'''
since this getting called more than one time, decided to put it in this 
proc
'''


def get_latest_database(db_path):
    db_source_zip = get_newest_file(db_path)
    if db_source_zip is None:
        print(f'\n?... ERROR, Exiting, database source not found at:{db_path}\n')
        sys.exit()
    return db_source_zip


def run_cmd(command):
    out = subprocess.call(command)
    if out is None:
        print(f'?... ERROR running command:{command}, out:{out}')
        sys.exit()
    else:
        print(f'--- Successfully run command:{command}, out:{out} -----\n\n')
    return


def change_dir(moveto):
    print(f'changing directory to:{moveto}')
    try:
        r = os.chdir(moveto)
        print(f'.. moved to: {os.getcwd()}')
    except FileNotFoundError:
        print(f'.. ERROR, not able to cd to:{moveto}')
        sys.exit()


'''
This proc opens up the Chrome browser and downloads the build based on the
version specified thr config.ini, download directory must be adjusted in config.ini
if it is other than default (i.e downloads)
'''


def download_all_builds(build_url, build_version):
    path = '../Drivers/chromedriver.exe'
    driver = webdriver.Chrome(path)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(build_url)
    for build in ['download-pre-base', 'download-pre-release', 'refresh']:
        print('Build:', build)
        driver.find_element_by_link_text(f'{build}-{build_version}').click()
    time.sleep(15)
    driver.close()
    driver.quit()
    return


def merge_master(build_url, build_version, master_path):
    path = '../Drivers/chromedriver.exe'
    driver = webdriver.Chrome(path)
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.get(f'{build_url}{build_version}')
    time.sleep(5)
    driver.find_element_by_xpath("//input[@type='file']").send_keys(master_path)
    driver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
    time.sleep(2)
    driver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
    time.sleep(5)
    driver.close()
    driver.quit()
    return
