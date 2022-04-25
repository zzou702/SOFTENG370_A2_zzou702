#!/usr/bin/env python3
from asyncore import socket_map
import os
import sys

dir1 = sys.argv[1]
dir2 = sys.argv[2]

print(dir1, dir2)

def check_directory():
    print(os.getcwd())
    return os.path.exists(os.getcwd())

something = check_directory()
print(something)