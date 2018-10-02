#!/usr/bin/env python

# This script will create auto backups of the following for CVP
# 1. Configlets
# 2. Devices
# 3. Images (To Come)
# 4. Image Bundles (To Come)
#
# By Rob Martin, Arista Networks 2018
# rmartin@arista.com
#

import argparse, os
from subprocess import call, PIPE, Popen
from datetime import datetime

__version__ = 1.0
__author__ = 'rmartin@arista.com'

cvp_data = '/data/cvpbackup'
base_cmds = ['/cvpi/tools/./cvptool.py','--host']

def get_hostname():
    dev_host = Popen(['hostname'],stdout=PIPE)
    dev_hostname = dev_host.stdout.read()
    dev_hostname = dev_hostname.replace('\n','')
    return(dev_hostname)

def count_files(backup_pre,f_path):
    "Function to count the number of files within a directory"
    fc = 0
    for r1 in os.listdir(f_path):
        if backup_pre in r1:
            fc += 1
    return(fc)

def get_backup(backup_pre,f_path):
    f_list = []
    for r1 in os.listdir(f_path):
        if backup_pre in r1:
            f_list.append(r1)
    return(f_list)

def get_date():
    return(datetime.now().strftime('%Y%m%d-%H%M'))

def checkDestination(host):
    ping_result = call(['ping','-c1','-w1',host],stdout=PIPE,stderr=PIPE)
    if ping_result == 0:
        return True
    else:
        return False

def main(u_args):
    #Main function
    # Add device hostname to base_cmds
    hostname = get_hostname()
    base_cmds.append(hostname)
    # Get current date/time
    cur_date = get_date()
    # Add user and pwd to base_cmds
    base_cmds.append('--user')
    base_cmds.append(u_args.user)
    base_cmds.append('--password')
    base_cmds.append(u_args.password)
    # Iterate through each option
    for item in u_args.objects:
        obj_cmd = []
        backup_file = cvp_data + '/' + hostname + '-' + item + '-' + cur_date + '.tar.gz'
        # Create custom backup comand list
        obj_cmd += base_cmds + ['--action','backup','--objects',item,'--tarFile',backup_file]
        # If a backup limit has been specified
        if u_args.limit:
            # Check to see if the limit has been reached
            current_count = count_files(hostname + '-' + item,cvp_data)
            if  current_count >= u_args.limit:
                print('Already %s %s backups, which is over the %s limit.'%(current_count,item,u_args.limit))
                obj_backup = get_backup(item,cvp_data)
                obj_backup.sort()
                for old_ind in range(0,current_count - (u_args.limit-1)):
                    print('Removing old backup: %s'%obj_backup[old_ind])
                    os.remove(cvp_data + '/' + obj_backup[old_ind])
            else:
                print('Already %s %s backups, which is less than the %s limit. No backups to be removed.'%(current_count,item,u_args.limit))
        # Try to create backup file for object
        try:
            print("Backing up file: %s"%backup_file)
            b_cmd = Popen(obj_cmd,stdout=PIPE,stderr=PIPE)
            print(b_cmd.stdout.read())
        except:
            print(b_cmd.stderr.read())
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--objects", type=str, default='configlets', nargs="*", choices=["configlets","containers","devices","images","imagebundles","roles","users","themes","aaa","changecontrol"], help="Specify which aspects to backup/restore", required=False)
    parser.add_argument("-u", "--user", type=str, default=None, help="Enter a valid user for CVP.", required=True)
    parser.add_argument("-p", "--password", type=str, default=None, help="Enter the password for the user.", required=True)
    parser.add_argument("-l", "--limit", type=int, default=None, help="Enter max amount of files to retain", required=False)
    args = parser.parse_args()
    main(args)