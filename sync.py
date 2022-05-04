#!/usr/bin/env python3
from dataclasses import dataclass
from genericpath import exists
from importlib.resources import path
import json
from locale import DAY_2
from operator import mod
import os
import string
import sys
import hashlib
import time
from xml.etree.ElementTree import ElementTree
import shutil
from datetime import datetime

from torch import true_divide



def check_directory(d1, d2):
    if os.path.isdir(d1) and os.path.isdir(d2):
        print("hi")
        return 1 # return 1 if both directories inputted exists
    elif (not os.path.isdir(d1) and (not os.path.isdir(d2))):
        return 2 # 2return 2 if none of the directories exists
    else:
        return 3 #return 3 if one of the diretory exists

def create_directory():
    if os.path.isdir(dir1) and (not os.path.isdir(dir2)):
        os.mkdir(dir2)
        return dir2
    elif os.path.isdir(dir2) and (not os.path.isdir(dir1)):
        os.mkdir(dir1)
        return dir1

# returns true if there is a sync file in the directory, 
def check_sync_file(directory):

    # to be implemented
    #loop through the directory for each files and check if there is a .sync.json file
    for file in os.listdir(directory):
        if file == ".sync.json":
            return True
    
    return False


def create_sync_file(directory):
    path_to_file = os.path.join(directory, ".sync.json")
    open(path_to_file, 'w')


# Iterate through the directory, checking if there is a sync file, and if there is subdirectories, and iterate through them, and updating the hash values through each directories
def iterate_directory(directory):

    for file in os.listdir(directory):
        #creating a temp file to maintain the full path name
        temp_file = os.path.join(directory, file)

        # if the current file is a directory, iterate again
        if os.path.isdir(temp_file):
            iterate_directory(temp_file)
            
    # 
    if not check_sync_file(directory):
        create_sync_file(directory)
        initial_hash_files(directory)
    
    update_hash(directory)


def initial_hash_files(directory):
    for file in os.listdir(directory):
        #skipping past files starting with .
        if file.startswith("."):
            continue
        
        #creating a temp file to maintain the full path name
        temp_file = os.path.join(directory, file)

        # if the current file is a directory, iterate again
        if os.path.isdir(temp_file):
            continue


        #get the modification time of the file
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(temp_file)))
        

        # read the file in order to produce a hash value
        with open(temp_file, "rb") as f:
            bytes = f.read()
            file_hash = hashlib.sha256(bytes).hexdigest()
            

        # checking for the current hash value of the file
        json_file_path = os.path.join(directory, ".sync.json")
        
        # string to be put into the json file
        json_string = {
            file : [
                [
                    mod_time, 
                    file_hash
                ]
            ]
        }

        # Inputting the data into the json file
        with open(json_file_path, "r+") as j_file:
            # If the file is empty
            if os.path.getsize(json_file_path) == 0:
                json.dump(json_string, j_file, indent=2)
            else: # File is not empty
                with open(json_file_path, "r+") as f:
                    data = json.load(j_file)
                    data[file] = [[mod_time, file_hash]]
                    
                    #j_file.seek(0)
                    json.dump(data, f, indent=2)


def update_hash(directory):
    deleted_file = []

    # checking for the current hash value of the file
    json_file_path = os.path.join(directory, ".sync.json")
    

    for file in os.listdir(directory):
        #skipping past invisible files that start with .
        if file.startswith("."):
            continue
        
        #creating a temp file to maintain the full path name
        temp_file = os.path.join(directory, file)

        # if the current file is a directory, iterate again
        if os.path.isdir(temp_file):
            continue

        #get the modification time of the file
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(temp_file)))
       

        # read the file in order to produce a hash value
        with open(temp_file, "rb") as f:
            bytes = f.read()
            file_hash = hashlib.sha256(bytes).hexdigest()
            
        input_string = [mod_time, file_hash]

        # if the json file is empty
        if os.path.getsize(json_file_path) == 0:
            j_string = {
            file : [
                [
                    mod_time, 
                    file_hash
                ]
            ]
            }

            with open(json_file_path, "r+") as j_file:
                json.dump(j_string, j_file, indent=2)

            continue


        with open(json_file_path, "r+") as j_file:
            data = json.load(j_file)

            # checking for deletion of files
            for filename in data:
                temp = os.path.join(directory, filename)
                if not os.path.exists(temp) and filename not in deleted_file:
                    deleted_file.append(filename)
                    continue
            
            # for the newly created files
            if file not in data:
                # print("it doesnt exists")
                with open(json_file_path, "r+") as j_file_create:
                    
                    data[file] = [[mod_time, file_hash]]
                        
                        #j_file.seek(0)
                    json.dump(data, j_file_create, indent=2)
                continue

            # for updating existing files
            #try:
            # 
            element = data[file]
            current_mod = element[0]
            # print(element)
            # print(current_mod)

            # if the content of the file has changed or if the modification time has changed
            if file_hash != current_mod[1] or mod_time != current_mod[0]:
                data[file].insert(0, input_string)

                with open(json_file_path, "r+") as j_file_update:
                    json.dump(data, j_file_update, indent=2)
        

    # updating information on the deleted files
    for file in deleted_file:
        
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        input_deletion_value = [current_time, "deleted"]

        with open(json_file_path, "r+") as j_file:
            data = json.load(j_file)
            
            file_name = data[file]
            element = file_name[0]
            

            if element[1] != "deleted":
                data[file].insert(0, input_deletion_value)

                with open(json_file_path, "r+") as j_file_delete:
                        json.dump(data, j_file_delete, indent=2)



def merge_directories(d1, d2):
    for i in os.listdir(d1):
        for j in os.listdir(d2):
            temp_file1 = os.path.join(d1, i)
            temp_file2 = os.path.join(d2, j)

            # if the current file is a directory, and the directory does not exist in dir2, copy the directory, iterate again
            if os.path.isdir(temp_file1) and not os.path.isdir(os.path.join(d2, i)):
                os.mkdir(os.path.join(d2, i))
                copy_dir(temp_file1, os.path.join(d2, i))
                merge_directories(temp_file1, os.path.join(d2, i))
            elif os.path.isdir(temp_file1) and os.path.isdir(os.path.join(d2, i)):
                merge_directories(temp_file1, os.path.join(d2, i))
            
            if os.path.isdir(temp_file2) and not os.path.isdir(os.path.join(d1, j)):
                os.mkdir(os.path.join(d1, j))
                copy_dir(temp_file2, os.path.join(d1, j))
                merge_directories(temp_file2, os.path.join(d1, j))
            elif os.path.isdir(temp_file2) and os.path.isdir(os.path.join(d1, j)):
                merge_directories(temp_file2, os.path.join(d1, j))

    
    sync_file_1 = os.path.join(d1, ".sync.json") #sync file for directory one
    sync_file_2 = os.path.join(d2, ".sync.json")


    # for files in directory 1
    with open(sync_file_1, "r+") as f1:
        data1 = json.load(f1)
            
        for file in data1:
            
            f_element = data1[file]
            f_status = f_element[0]

            # for deleted files in diretory 1 and not deleted in directory 2
            if f_status[1] == "deleted" and os.path.exists(os.path.join(d2, file)):
                os.remove(os.path.join(d2, file))
            elif f_status[1] != "deleted" and not os.path.exists(os.path.join(d2, file)): # Files that exist in d1 but not d2
                shutil.copy(os.path.join(d1, file), os.path.join(d2, file))
        
    #updating hash information on directory 2
    iterate_directory(d2)

    # for files in directory 2
    with open(sync_file_2, "r+") as f2:
        data2 = json.load(f2)
        # for files in directory 2
        for file in data2:
            f_element = data2[file]
            f_status = f_element[0]

            if f_status[1] == "deleted" and os.path.exists(os.path.join(d1, file)):
                os.remove(os.path.join(d1, file))
            elif f_status[1] != "deleted" and not os.path.exists(os.path.join(d1, file)): # Files that exist in d2 but not d1
                shutil.copy(os.path.join(d2, file), os.path.join(d1, file))
        
    iterate_directory(d1)

    

    # for files that exists in both directories but has different content or modification time
    for file1 in os.listdir(d1):
        for file2 in os.listdir(d2):
            # for the same file in both directories
            if file1 == file2 and not file1.startswith(".") and not os.path.isdir(os.path.join(d1, file1)): 
                with open(sync_file_1, "r+") as f1:
                    data1 = json.load(f1)
                    with open(sync_file_2, "r+") as f2:
                        data2 = json.load(f2)

                        f_element1 = data1[file1]
                        f_status1 = f_element1[0]
                        
                        f_element2 = data2[file2]
                        f_status2 = f_element2[0]

                        # if both files have the same digest but different mod date
                        if f_status1[1] == f_status2[1] and f_status1[0] != f_status2[0]:
                            time1 = datetime.strptime(f_status1[0], '%Y-%m-%d %H:%M:%S')
                            time2 = datetime.strptime(f_status2[0], '%Y-%m-%d %H:%M:%S')
                            print(time1, time2)


                            # if file one has earlier date
                            if time2 > time1:
                                print("hi from time1")
                                input_value = [f_status1[0], f_status1[1]]
                                data2[file1].insert(0, input_value)
                                shutil.copystat(os.path.join(d1, file1), os.path.join(d2, file2))

                                with open(sync_file_2, "r+") as j_file:

                                    json.dump(data2, j_file, indent=2)
                                
                            elif time1 > time2: # if file two has earlier date
                                print("hi from time2")
                                input_value = [f_status2[0], f_status2[1]]
                                data1[file2].insert(0, input_value)
                                shutil.copystat(os.path.join(d2, file2), os.path.join(d1, file1))

                                with open(sync_file_1, "r+") as j_file:
                                    
                                    json.dump(data1, j_file, indent=2)
                            
                        
                        # for files that have different digests i.e. different content
                        elif f_status1[1] != f_status2[1]:
                            time1 = datetime.strptime(f_status1[0], '%Y-%m-%d %H:%M:%S')
                            time2 = datetime.strptime(f_status2[0], '%Y-%m-%d %H:%M:%S')

                            cont_file = False


                            #if current version of file 1 is the same one of the previous digest of file 2
                            for pre_value in f_element2:
                                if f_status1 == pre_value:
                                    print("true1")

                                    # update the file 1 to match the current digest of file 2
                                    input_value = [f_status2[0], f_status2[1]]
                                    data1[file1].insert(0, input_value)

                                    # copy the file2 to file1 along with the matadata
                                    shutil.copy2(os.path.join(d2, file2), os.path.join(d1, file1))

                                    # update the sync file for d1
                                    with open(sync_file_1, "r+") as j_file:

                                        json.dump(data1, j_file, indent=2)
                                    
                                    cont_file = True

                                    break
                            
                            # continue to the next file in the direcotry if 
                            if cont_file:
                                continue

                            # if current version of file 2 is the same one of the previous digest of file 1
                            for pre_value in f_element1:
                                if f_status2 == pre_value:
                                    print("true2")

                                    # update the file 1 to match the current digest of file 2
                                    input_value = [f_status1[0], f_status1[1]]
                                    data2[file2].insert(0, input_value)

                                    # copy the file2 to file1 along with the matadata
                                    shutil.copy2(os.path.join(d1, file1), os.path.join(d2, file2))

                                    #update the sync file for d2
                                    with open(sync_file_2, "r+") as j_file:

                                        json.dump(data2, j_file, indent=2)

                                    cont_file = True
                                    
                                    break

                            if cont_file:
                                continue

                            # if file 2 is more recent
                            if time2 > time1:
                                input_value = [f_status2[0], f_status2[1]]
                                data1[file1].insert(0, input_value)
                                shutil.copy2(os.path.join(d2, file2), os.path.join(d1, file1))

                                with open(sync_file_1, "r+") as j_file:

                                    json.dump(data1, j_file, indent=2)
                                
                            elif time1 > time2: # if file 1 is more recent
                                input_value = [f_status1[0], f_status1[1]]
                                data2[file2].insert(0, input_value)
                                shutil.copy2(os.path.join(d1, file1), os.path.join(d2, file2))

                                with open(sync_file_2, "r+") as j_file:
                                    
                                    json.dump(data2, j_file, indent=2)



# This method copies the entire directory of source onto dest
def copy_dir(source, destination):
    for element in os.listdir(source):
        # bypassing files starting with "."
        if element.startswith("."):
            continue

        src = os.path.join(source, element)
        dst = os.path.join(destination, element)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".*")) # copy the trees ignoring hidden files starting with "."
        else:
            shutil.copy2(src, dst)


def listdir_no_hidden(dir):
    dir_list = []
    for element in os.listdir(dir):
        if not element.startswith("."):
            dir_list.append(element)
    
    return len(dir_list)


# main code
dir1 = os.path.join(os.getcwd(), sys.argv[1])
dir2 = os.path.join(os.getcwd(), sys.argv[2])

# dir1 = os.path.join(os.getcwd(), "SOFTENG370_A2_zzou702/hello1")
# dir2 = os.path.join(os.getcwd(), "SOFTENG370_A2_zzou702/hello3")
#print(dir1, dir2)


dir_validity = check_directory(dir1, dir2)

# checking the validity of the inputted directories
if dir_validity == 2:
    print("none exists")
    exit()
elif dir_validity == 3:
    print("one existes")
    # creating a new directory
    create_directory() 

# if there is no sync files in the directory, create a new one
iterate_directory(dir1)
iterate_directory(dir2)

dir_length1 = listdir_no_hidden(dir1)
dir_length2 = listdir_no_hidden(dir2)

# print(dir_length1, dir_length2)

# If dir1 is empty i.e. length = one since the sync file is created
if dir_length1 == 0 and dir_length2 != 0:
    copy_dir(dir2, dir1)
    #iterate_directory(dir1)
elif dir_length1 != 0 and dir_length2 == 0: # if dir2 is empty
    print("dir2 is empty")
    copy_dir(dir1, dir2)
    #iterate_directory(dir2)
else: # both directories are not empty
    merge_directories(dir1, dir2)

# updating the hash values of files in each directories and subdirectories
iterate_directory(dir1)
iterate_directory(dir2)


# read through