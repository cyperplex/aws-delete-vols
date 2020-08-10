#This script will find and delete disks that are unattached in AWS.
# This version requires the use of the aws-adfs ahead of execution to be logging in with a sufficient role to execute the deletes

import boto3
from pprint import pprint
import os, datetime

def collect_disks():
    # create a list where the volume ids of unused volumes will be stored
    volumes_to_delete = list();

    # call describe_volumes() method of client to get the details of all ebs volumes in given region
    # if you have large number of volumes then get the volume detail in batch by using nextToken and process accordingly
    volume_detail = client.describe_volumes();

    # process each volume in volume_detail
    if volume_detail['ResponseMetadata']['HTTPStatusCode'] == 200:
        for each_volume in volume_detail['Volumes']:
            # Generate DiskUsage Report
            f = open("volume_delete_report_" + (datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")) +".txt", "w")
            f.write("----------------Start------------------------");
            f.write("Working for volume with volume_id: " + str(each_volume['VolumeId']));
            f.write("State of volume: " + str(each_volume['State']));
            f.write("Attachment state length: " + str(len(each_volume['Attachments'])));
            f.write("--------------------------------------------");
            f.write(str(each_volume['Attachments']));
            f.write("-----------------END------------------------");
            # identify all the unused Volumes by checking number of attachments and the state of the volume ie the volumes which do not have 'Attachments' key and their state is 'available' is considered to be unused in aws
            if len(each_volume['Attachments']) == 0 and each_volume['State'] == 'available':
                volumes_to_delete.append(each_volume['VolumeId'])
            # these are the candidates to be deleted by maintaining waiters for them
        f.close()
        if not volumes_to_delete:
            print("Sorry there are no unattached volumes currently.. exiting")
        else:
            pprint(volumes_to_delete)
            reply = str(raw_input('Would you like to delete the volumes now (y/n): ')).lower().strip()
            if reply[0] == 'y':
                print("You have chosen to proceed to delete")
                for each_volume_id in volumes_to_delete:
                    try:
                        print("Deleting Volume with volume_id: " + each_volume_id)
                        response = client.delete_volume(
                            VolumeId=each_volume_id
                        )
                    except Exception as e:
                        print("Issue in deleting volume with id: " + each_volume_id + "and error is: " + str(e))

                # waiters to verify deletion and keep alive deletion process until completed
                waiter = client.get_waiter('volume_deleted')
                try:
                    waiter.wait(
                        VolumeIds=volumes_to_delete,
                    )
                    print("Successfully deleted all volumes")
                except Exception as e:
                    print("Error in process with error being: " + str(e))

            if reply[0] == 'n':
                print("Canceled Operation")
                exit(0)
            else:
               print("  Please select y/n")


# Dunder init :)  Create boto3 client for ec2
client = boto3.client('ec2', region_name=os.getenv('AWS_REGION'))
# AWS auth provided by Federation login using aws-adfs login commandline tool
#Call Collect Function to get disk listing
collect_disks()
