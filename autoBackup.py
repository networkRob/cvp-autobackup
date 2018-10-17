#!/usr/bin/env python

# Copyright (c) 2018, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  - Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#  - Neither the name of Arista Networks nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# By Rob Martin, Arista Networks 2018
# robmartin@arista.com
#

import argparse, os
from subprocess import PIPE, Popen
from datetime import datetime

__version__ = 1.1
__author__ = 'robmartin@arista.com'

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

def main(u_args):
    #Main function
    # Add device hostname to base_cmds
    hostname = get_hostname()
    base_cmds.append(hostname)
    # Add user and pwd to base_cmds
    base_cmds.append('--user')
    base_cmds.append(u_args.user)
    base_cmds.append('--password')
    base_cmds.append(u_args.password)
    # Iterate through each option
    for item in u_args.objects:
        obj_cmd = []
        backup_file = cvp_data + '/' + hostname + '-' + item + '-' + get_date() + '.tar.gz'
        # Create custom backup comand list
        obj_cmd += base_cmds + ['--action','backup','--objects',item,'--tarFile',backup_file]
        # If a backup limit has been specified
        if u_args.limit:
            # Check to see if the limit has been reached
            current_count = count_files(hostname + '-' + item,cvp_data)
            if  current_count >= u_args.limit:
                print('Already %s %s backups, which put the backups over the %s limit.'%(current_count,item,u_args.limit))
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
            err_msg = b_cmd.stderr.read()
            # Adding error check for when the '/' directory does not have enough space to create tmp backup file
            # before writing to final destination
            if err_msg:
                if 'No space left on device' in err_msg:
                    print('ERROR! not enough space availble on "/" to create temporary backup file')
                else:
                    print(err_msg)
        except:
            print(b_cmd.stderr.read())
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--objects", type=str, default='configlets', nargs="*", choices=["configlets","containers","devices","images","imagebundles","roles","users","themes","aaa","changecontrol","certs","trustedcerts"], help="Specify which aspects to backup/restore", required=False)
    parser.add_argument("-u", "--user", type=str, default=None, help="Enter a valid user for CVP.", required=True)
    parser.add_argument("-p", "--password", type=str, default=None, help="Enter the password for the user.", required=True)
    parser.add_argument("-l", "--limit", type=int, default=None, help="Enter max amount of files to retain", required=False)
    args = parser.parse_args()
    main(args)