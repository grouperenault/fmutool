from zipfile import ZipFile
import os
import sys

version = sys.argv[1]

# create a ZipFile object
base_directory = "build"
zip_filename = f"fmu_manipulation_toolbox-{version}.zip"

with ZipFile(zip_filename, 'w') as zip_file:
    for folder_name, subfolders, filenames in os.walk(base_directory):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            zip_file.write(file_path, file_path[len(base_directory)+1:])

print(f"Package {zip_filename} created")
