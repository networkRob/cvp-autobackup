### CVP AutoBackup

This script will perform backups for portions of the CVP node.  This can be utilized as a cronjob within CVP to be scheduled to take backups at a certain time for the specified data objects.

Tested on version CVP-2018.1.4

#### Setup

Copy the `autoBackup.py` file to the `root` users home directory on the CVP node for a single node, or the primary node in a cluster.

Below are the parameters needed for the script to run: 
- `--objects` defaults to `configlets` the possible options are: `configlets`, `containers`, `devices`, `images`, `imagebundles`, `roles`, `users`, `themes`, `aaa`, `changecontrol`, `certs`, `trustedcerts`
- `--user` (Required) An authorized user for CloudVision
- `--password` (Required) The password for the above authorized user
- `--limit` (Optional) This parameter limits the amount of backups are retained on CVP in `/data/cvpbackup`

#### Example
Below are some example ways to run the script:
##### Configlet Backup only
```
[root@cvp-01 ~]# ./autoBackup.py --objects configlets --user {CVP_USER} --password {CVP_PASSWORD}
```
##### Configlet, User, and Roles Backups: Retains a limit of 2 copies of Each Backup
```
[root@cvp-01 ~]# ./autoBackup.py --objects configlets roles users --user {CVP_USER} --password {CVP_PASSWORD} --limit 2
```