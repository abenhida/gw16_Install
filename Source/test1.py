import os
import zipfile
from checks import check_dir_file



# this will unzip the zip file to the folder "zippedPictures"
# if that zippedPictures already  has files/folders it will update them
# if the folder "zippedPictures" not there it will create it

db_target_zip = 'C:\\Users\\ABenhida\\Desktop\\database_7441_Ahmedb'
db_source_zip = 'E:\\17.0\\staging\\rel-17-0\\7441-Ahmedb\\17.0.41_20211122-203653\\zips\\database.zip'

with zipfile.ZipFile(db_source_zip, "r") as zip_ref:
    zip_ref.extractall(db_target_zip)

#print('I will execute some dos commands')
#os.system("copy C:\\Users\\ABenhida\\text.txt C:\\Users\\ABenhida\\text3.txt")

print('--------------------')

import subprocess
output = subprocess.getoutput("copy C:\\Users\\ABenhida\\text.txt C:\\Users\\ABenhida\\text5.txt")
print('output:', output)
print('expected: output:         1 file(s) copied.')