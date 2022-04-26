#!/usr/bin/env python3
from genericpath import exists
from importlib.resources import path
import json
import os
import sys

dir1 = os.path.join(os.getcwd(), sys.argv[1])
dir2 = os.path.join(os.getcwd(), sys.argv[2])

print(dir1, dir2)

def check_directory():
    print(os.getcwd())

    if os.path.exists(dir1) and os.path.exists(dir2):
        return 1 # return 1 if both directories inputted exists
    elif (not os.path.exists(dir1) and (not os.path.exists(dir2))):
        return 2 # 2return 2 if none of the directories exists
    else:
        return 3 #return 3 if one of the diretory exists

def create_directory():
    if os.path.exists(dir1) and (not os.path.exists(dir2)):
        os.mkdir(dir2)
        return dir2
    elif os.path.exists(dir2) and (not os.path.exists(dir1)):
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


def iterate_directory(directory):

    for file in os.listdir(directory):
        #creating a temp file to maintain the full path name
        temp_file = os.path.join(directory, file)

        print(temp_file)

        # if the current file is a directory, iterate again
        if os.path.isdir(temp_file):
            iterate_directory(temp_file)
            
    # 
    if not check_sync_file(directory):
        create_sync_file(directory)



# main code

dir_validity = check_directory()


if dir_validity == 1: # Both directories exist
    print("both exists")
    #checking for the sync files in the directories, if it dosn't exist, create one
    iterate_directory(dir1)
    iterate_directory(dir2)

elif dir_validity == 2:
    print("none exists")
    exit()
elif dir_validity == 3:
    print("one existes")
    # creating a new directory
    create_directory() 

    # if there is no sync files in the directory, create a new one
    iterate_directory(dir1)
    iterate_directory(dir2)

# read throught