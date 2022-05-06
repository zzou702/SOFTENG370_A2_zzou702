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



# this function returns a value based on whether the directories inputted exist
def check_directory(d1, d2):
    if os.path.isdir(d1) and os.path.isdir(d2):
        return 1 # return 1 if both directories inputted exists
    elif (not os.path.isdir(d1) and (not os.path.isdir(d2))):
        return 2 # 2return 2 if none of the directories exists
    else:
        return 3 #return 3 if one of the diretory exists

# this function creates a new directory
def create_directory(d1, d2):
    # create dir 2
    if os.path.isdir(d1) and (not os.path.isdir(d2)):
        os.mkdir(d2)
        return d2
    elif os.path.isdir(d2) and (not os.path.isdir(d1)): #create dir 1
        os.mkdir(d1)
        return d1

# returns true if there is a sync file in the directory, 
def check_sync_file(directory):
    #loop through the directory for each files and check if there is a .sync.json file
    for file in os.listdir(directory):
        if file == ".sync":
            return True
    
    return False

# this function creates the sync file in directory
def create_sync_file(directory):
    # sync file path name
    path_to_file = os.path.join(directory, ".sync")
    # creates the file since it doesn't exist
    open(path_to_file, 'w')


# Iterate through the directory, checking if there is a sync file, and if there is subdirectories, and iterate through them, and updating the hash values through each directories
def iterate_directory(directory):
    for file in os.listdir(directory):
        #creating a temp file to maintain the full path name
        temp_file = os.path.join(directory, file)

        # if the current file is a directory, iterate again
        if os.path.isdir(temp_file):
            iterate_directory(temp_file)
            
    # create sync file if it doesn't exist in the directory
    if not check_sync_file(directory):
        create_sync_file(directory)
        # initial hashing for the files in the directory
        initial_hash_files(directory)
    
    # updating the hash values of files
    update_hash(directory)

# This file hashes the files in the directory when the sync file has first been created
def initial_hash_files(directory):
    # iterate through all the files in the directory
    for file in os.listdir(directory):
        #skipping past files starting with . i.e. hidden files
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
        json_file_path = os.path.join(directory, ".sync")
        
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
                    json.dump(data, f, indent=2)

# this file updates the hash values of files in the directory, if there has been changes
def update_hash(directory):
    #initilising the deleted file list for later processing
    deleted_file = []

    # checking for the current hash value of the file
    json_file_path = os.path.join(directory, ".sync")
    
    # iterate through all the file in the directory
    for file in os.listdir(directory):
        # if the json file is not empty
        if os.path.getsize(json_file_path) != 0:
            with open(json_file_path, "r+") as j_file:
                data = json.load(j_file)

                # checking for deletion of files
                for filename in data:
                    temp = os.path.join(directory, filename)
                    
                    # if the file in the json file does not exist in the directory, and it has not been previously appended to the deleted file list
                    if not os.path.exists(temp) and filename not in deleted_file:
                        # adding it to the deleted file list
                        deleted_file.append(filename)
                
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
            # hashing the file and turn the value into a readable format
            file_hash = hashlib.sha256(bytes).hexdigest()
            
        # input string for updating the json file
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

            # inputting the file with its modification time and hash values into the json file
            with open(json_file_path, "r+") as j_file:
                json.dump(j_string, j_file, indent=2)

            # move onto the next file
            continue

        # updating the information on the files
        with open(json_file_path, "r+") as j_file:
            data = json.load(j_file)
            
            # for the newly created files, i.e. if te file in the directory is not in the json file
            if file not in data:
                with open(json_file_path, "r+") as j_file_create:
                    # inputting the value into the json file
                    data[file] = [[mod_time, file_hash]]
                    json.dump(data, j_file_create, indent=2)
                continue

            # for updating existing files
            element = data[file]
            current_mod = element[0]

            # if the content of the file has changed or if the modification time has changed
            if file_hash != current_mod[1] or mod_time != current_mod[0]:
                # appending the input string to the front of the list
                data[file].insert(0, input_string)

                # writing to the json file
                with open(json_file_path, "r+") as j_file_update:
                    json.dump(data, j_file_update, indent=2)
        

    # updating information on the deleted files
    for file in deleted_file:
        # getting the current time as per requirement
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        # The value to be inputted into the json file for the deletion of a file
        input_deletion_value = [current_time, "deleted"]

        # writing to the json file with the deletion values
        with open(json_file_path, "r+") as j_file:
            data = json.load(j_file)
            
            file_name = data[file]
            element = file_name[0]

            if element[1] != "deleted":
                data[file].insert(0, input_deletion_value)

                with open(json_file_path, "r+") as j_file_delete:
                        json.dump(data, j_file_delete, indent=2)


# this function merges both directories inputted, resulting in a synced state
def merge_directories(d1, d2):
    # iterate through both directories
    for i in os.listdir(d1):
        for j in os.listdir(d2):
            temp_file1 = os.path.join(d1, i)
            temp_file2 = os.path.join(d2, j)

            # if the current file is a directory, and the directory does not exist in dir2, copy the directory, iterate again
            if os.path.isdir(temp_file1) and not os.path.isdir(os.path.join(d2, i)):
                os.mkdir(os.path.join(d2, i))
                copy_dir(temp_file1, os.path.join(d2, i))
                merge_directories(temp_file1, os.path.join(d2, i))
            elif os.path.isdir(temp_file1) and os.path.isdir(os.path.join(d2, i)): #if current file is a direstory, and the directory exist, iterate again, syncing the subdirectories
                merge_directories(temp_file1, os.path.join(d2, i))
            
            # Same process as above but for the files/directories in directory 2
            if os.path.isdir(temp_file2) and not os.path.isdir(os.path.join(d1, j)):
                os.mkdir(os.path.join(d1, j))
                copy_dir(temp_file2, os.path.join(d1, j))
                merge_directories(temp_file2, os.path.join(d1, j))
            elif os.path.isdir(temp_file2) and os.path.isdir(os.path.join(d1, j)):
                merge_directories(temp_file2, os.path.join(d1, j))

    # updating directory information for further operation
    iterate_directory(d1)
    iterate_directory(d2)

    # Sync files of each directories
    sync_file_1 = os.path.join(d1, ".sync") #sync file for directory one
    sync_file_2 = os.path.join(d2, ".sync")

    # dealing with deletion of files
    # if the sync file is not empty
    if os.path.getsize(sync_file_1) != 0:
        # loading information for files in directory 1
        with open(sync_file_1, "r+") as f1:
            data1 = json.load(f1)
            
            #loading information for files in directory 2
            with open(sync_file_2, "r+") as f2:
                data2 = json.load(f2)
                
                # For the files in directory 1
                for file in data1:
                    
                    # Getting the file's most current status
                    f_element = data1[file]
                    f_status = f_element[0]

                    # see if the file in the json file for dir 1 exist in the json file for dir 2
                    try:
                        data2[file]
                    except KeyError:
                        # file does not exist in json file for dir 2
                        file_exists = False
                    else:
                        # file exists in json file for dir 2
                        file_exists = True

                    # if the file exists in json file for dir 2
                    if file_exists:
                        # getting the most recent status for the file 
                        f_element2 = data2[file]
                        f_status2 = f_element2[0]
                    else:
                        # if the file does not exist in json file for dir 2
                        f_status2 = ["0-0-0 0:0:0",0]
                        

                    # for deleted files in diretory 1 and not deleted in directory 2, and the file has not been created again
                    if f_status[1] == "deleted" and os.path.exists(os.path.join(d2, file)):
                        # tracking the newly created file
                        newly_created = False

                        # check whether the deletion in dir 1 matches an earlier deletion of dir 2
                        for file2 in data2:
                            # find the same file in the other diretory
                            if file2 == file:
                                # get the hash information on the file
                                f_element2 = data2[file]
                                #go through the information
                                for temp_status in f_element2:
                                    # matching earlier deletion of the same file, the file has been newly created
                                    if f_status == temp_status:
                                        # recreating the file along with the mod time
                                        shutil.copy2(os.path.join(d2, file), os.path.join(d1, file))
                                        newly_created = True
                                        break
                                    else:
                                        newly_created = False

                        # if the file has not been newly created
                        if newly_created == False:
                            # remove the other file
                            os.remove(os.path.join(d2, file))
                    
                    # Files that exist in d1 but not d2 and file 2 has not been deleted
                    elif f_status[1] != "deleted" and not os.path.exists(os.path.join(d2, file)) and f_status2[1] != "deleted": 
                        # create/copy the file along with its modification and access time
                        shutil.copy2(os.path.join(d1, file), os.path.join(d2, file))
            
        #updating hash information on directory 2
        iterate_directory(d2)

    # this is the same process as above, but we iterate through files in json file for dir 2 and carry out the respective operations for file in dir 1
    if os.path.getsize(sync_file_2) != 0:
        # for files in directory 2
        with open(sync_file_2, "r+") as f2:
            data2 = json.load(f2)

            with open(sync_file_1, "r+") as f1:
                data1 = json.load(f1)
                # for files in directory 2
                for file in data2:
                    f_element = data2[file]
                    f_status = f_element[0]

                    try:
                        data1[file]
                    except KeyError:
                        file_exists = False
                    else:
                        file_exists = True

                    if file_exists:
                        f_element2 = data1[file]
                        f_status2 = f_element2[0]
                        
                    else:
                        f_status2 = ["0-0-0 0:0:0",0]

                    if f_status[1] == "deleted" and os.path.exists(os.path.join(d1, file)):
                        # tracking the newly created file
                        newly_created = False

                        # check whether the deletion in dir 1 matches an earlier deletion of dir 2
                        for file1 in data1:
                            # find the same file in the other diretory
                            if file1 == file:
                                # get the hash information on the file
                                f_element1 = data1[file]
                                #go through the information
                                for temp_status in f_element1:
                                    # matching earlier deletion of the same file, the file has been newly created
                                    if f_status == temp_status:
                                        shutil.copy2(os.path.join(d1, file), os.path.join(d2, file))
                                        newly_created = True
                                        break
                                    else:
                                        newly_created = False

                        # if the file has not been newly created
                        if newly_created == False:
                            os.remove(os.path.join(d1, file))

                    # Files that exist in d2 but not d1, and file was not deleted in d1
                    elif f_status[1] != "deleted" and not os.path.exists(os.path.join(d1, file)) and f_status2[1] != "deleted": 
                        shutil.copy2(os.path.join(d2, file), os.path.join(d1, file)) 

        iterate_directory(d1)

    # for files that exists in both directories but has different content or modification time
    for file1 in os.listdir(d1):
        for file2 in os.listdir(d2):
            # for the same file in both directories, and they are not directories
            if file1 == file2 and not file1.startswith(".") and not os.path.isdir(os.path.join(d1, file1)) and os.path.getsize(sync_file_1) != 0 and os.path.getsize(sync_file_2) != 0:
                with open(sync_file_1, "r+") as f1:
                    data1 = json.load(f1)
                    with open(sync_file_2, "r+") as f2:
                        data2 = json.load(f2)

                        # getting the most recent status for the files in both json file
                        f_element1 = data1[file1]
                        f_status1 = f_element1[0]
                        
                        f_element2 = data2[file2]
                        f_status2 = f_element2[0]

                        # if both files have the same digest but different mod date
                        if f_status1[1] == f_status2[1] and f_status1[0] != f_status2[0]:
                            # Formatting the time from string to allow for later comparison
                            time1 = datetime.strptime(f_status1[0], '%Y-%m-%d %H:%M:%S')
                            time2 = datetime.strptime(f_status2[0], '%Y-%m-%d %H:%M:%S')

                            # if file one has earlier date
                            if time2 > time1:
                                input_value = [f_status1[0], f_status1[1]]
                                data2[file1].insert(0, input_value)
                                # copying the modification and access date over to file 2
                                shutil.copystat(os.path.join(d1, file1), os.path.join(d2, file2))

                                # Wrting the updated mod time to the json file
                                with open(sync_file_2, "r+") as j_file:
                                    json.dump(data2, j_file, indent=2)
                            elif time1 > time2: # if file two has earlier date
                                input_value = [f_status2[0], f_status2[1]]
                                data1[file2].insert(0, input_value)
                                shutil.copystat(os.path.join(d2, file2), os.path.join(d1, file1))

                                with open(sync_file_1, "r+") as j_file:
                                    json.dump(data1, j_file, indent=2)
                        # for files that have different digests i.e. different content
                        elif f_status1[1] != f_status2[1]:
                            # time formated from string for later comparison
                            time1 = datetime.strptime(f_status1[0], '%Y-%m-%d %H:%M:%S')
                            time2 = datetime.strptime(f_status2[0], '%Y-%m-%d %H:%M:%S')

                            # boolean for tracking operation
                            cont_file = False

                            #if current version of file 1 is the same one of the previous digest of file 2
                            for pre_value in f_element2:
                                if f_status1 == pre_value:
                                    # update the file 1 to match the current digest of file 2
                                    input_value = [f_status2[0], f_status2[1]]
                                    data1[file1].insert(0, input_value)

                                    # copy the file2 to file1 along with the matadata
                                    shutil.copy2(os.path.join(d2, file2), os.path.join(d1, file1))

                                    # update the sync file for d1
                                    with open(sync_file_1, "r+") as j_file:
                                        json.dump(data1, j_file, indent=2)
                                    
                                    # setting the tracker to true, since operation on the same file in both directories has been carried out
                                    cont_file = True

                                    break
                            
                            # continue to the next file in the direcotry if the current file has been modified 
                            if cont_file:
                                continue

                            # if current version of file 2 is the same one of the previous digest of file 1
                            for pre_value in f_element1:
                                if f_status2 == pre_value:

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

                            # if the process reach this section, meaning that none of the current versions of both files matches previous versions of each other, now we sync based
                            # on the time of modification as specified in the assginment brief

                            # if file 2 is more recent, modify file 1 based on the contents and modification time of file 2
                            if time2 > time1:
                                input_value = [f_status2[0], f_status2[1]]
                                data1[file1].insert(0, input_value)

                                shutil.copy2(os.path.join(d2, file2), os.path.join(d1, file1))

                                with open(sync_file_1, "r+") as j_file:
                                    json.dump(data1, j_file, indent=2)
                            
                            # if file 1 is more recent, modify file 2 based on file 1
                            elif time1 > time2: 
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

        # src file in dir1 and dst file in dir 2
        src = os.path.join(source, element)
        dst = os.path.join(destination, element)
        
        # if the source file is a directory, copy the entire subdirectories, ignoring hidden files
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".*")) # copy the trees ignoring hidden files starting with "."
        else:
            # if the source file is not a directory, copy it over to the dst file
            shutil.copy2(src, dst)

# modified listdir function to return all the files in the directory without hidden files
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

# checking the whether the directories inputted exists
dir_validity = check_directory(dir1, dir2)

# checking the validity of the inputted directories
if dir_validity == 2:
    print("Error: None of the input directories exist")
    exit()
elif dir_validity == 3:
    # creating a new directory
    create_directory(dir1,dir2) 

# Iterate through both directories and perform the initialisation or update of the files in them
iterate_directory(dir1)
iterate_directory(dir2)

# Get the length of the input directories
dir_length1 = listdir_no_hidden(dir1)
dir_length2 = listdir_no_hidden(dir2)

# If dir1 is empty i.e. length = one since the sync file is created
if dir_length1 == 0 and dir_length2 != 0:
    # copy the entire content of dir2 to dir 1
    copy_dir(dir2, dir1)
elif dir_length1 != 0 and dir_length2 == 0: # if dir2 is empty
    copy_dir(dir1, dir2)
else: # both directories are not empty
    # sync the two directories
    merge_directories(dir1, dir2)

# updating the hash values of files in each directories and subdirectories again
iterate_directory(dir1)
iterate_directory(dir2)