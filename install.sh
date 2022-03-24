#!/bin/bash

set -e

# RUN THIS FILE ONLY IF YOU WANT TO ADD EXECUTABLE PRIVELAGES TO ANY FILE USING A NEVER CHANGING DIRECTORY
# THIS WILL ALSO INSTALL NASM AND A LINKER

if [ "$EUID" -ne 0 ]
then
        printf "Please run this program as root by typing \"sudo ./install.sh\" \n"
        exit 1
else
       printf "[INFO] Updating the package sources list"
       printf "[CMD] sudo apt-get update -y"
       sudo apt-get update -y
    
       printf "[INFO] Installing Nasm"
       printf "[CMD] sudo apt-get install -y nasm"
       sudo apt-get install -y nasm 

       printf "[CMD] sudo rm -rf /usr/bin/hustle \n"
       sudo rm -rf /usr/bin/hustle
       
       printf "[CMD] sudo mkdir /usr/bin/hustle \n"
       sudo mkdir /usr/bin/hustle

       printf "[INFO] Copying directories to /usr/bin/hustle"
       printf "[CMD] sudo cp hustle.py /usr/bin/hustle \n"
       sudo cp hustle.py /usr/bin/hustle
       
       printf "[CMD] sudo cp stdlib.hsle /usr/bin/hustle \n" 
       sudo cp stdlib.hsle /usr/bin/hustle
       
       printf "[CMD] sudo cp std -r /usr/bin/hustle \n"
       sudo cp std -r /usr/bin/hustle
       
       printf "[CMD] sudo cp arrow_strings -r /usr/bin/hustle \n"
       sudo cp arrow_strings -r /usr/bin/hustle

       printf "[CMD] sudo cp keywords -r /usr/bin/hustle \n"
       sudo cp keywords -r /usr/bin/hustle

       printf "[CMD] sudo cp ops -r /usr/bin/hustle \n"
       sudo cp ops -r /usr/bin/hustle

       printf "\nInstallation Complete, You can now run hustle files as executables using a never changing directory"
       
fi
