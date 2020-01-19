import boto3
import datetime
import csv
import sys
import re

from datetime import datetime


def get_volumes(volume_type):
    region_client = boto3.client('ec2')
    regions = []
    try:
        regions = region_client.describe_regions()['Regions']
    except Exception as ex:
        print('Unable to fetch Regions:' + str(ex))

    Filters = [{'Name': 'status', 'Values': ['in-use']}]
    if volume_type != 'all':
        Filters.append({'Name': 'volume-type', 'Values': [volume_type]})

    rows = []
    for region in regions:
        ec2 = boto3.client('ec2', region_name=region['RegionName'])
        volumes = ec2.describe_volumes(Filters=Filters)['Volumes']

        for volume in volumes:
            try:
                row = {}
                row["AvailabilityZone"] = volume['AvailabilityZone']
                row["volumeId"] = volume['VolumeId']
                row["VolumeType"] = volume['VolumeType']
                row["State"] = volume['State']
                row["SnapshotId"] = volume['SnapshotId']
                row["Size"] = str(volume['Size'])
                row["Encrypted"] = 'True' if volume['Encrypted'] else 'False'
                row["CreateTime"] = volume['CreateTime'].strftime("%m/%d/%Y, %H:%M:%S")
                row["Device"] = row["InstanceId"] = row['DeleteOnTermination'] = row['AttachTime'] = ''
                row["InstanceState"] = row["InstanceType"] = row["StateChangeTime"] = ''

                if 'Attachments' in volume and len(volume['Attachments']) > 0:
                    row["Device"] = volume['Attachments'][0]['Device']
                    row["InstanceId"] = volume['Attachments'][0]['InstanceId']
                    row["DeleteOnTermination"] = 'True' if volume['Attachments'][0]['DeleteOnTermination'] else 'False'
                    row["AttachTime"] = volume['Attachments'][0]['AttachTime'].strftime("%m/%d/%Y, %H:%M:%S")
                    reservations = ec2.describe_instances(InstanceIds=[row["InstanceId"]])
                    if 'Reservations' in reservations and 'Instances' in reservations['Reservations'][0] and len(
                            reservations['Reservations'][0]['Instances']):
                        instance = reservations['Reservations'][0]['Instances'][0]
                        row["InstanceState"] = instance["State"]["Name"]
                        row["InstanceType"] = instance['InstanceType']
                        row["IsRootVolume"] = 'true' if row["Device"] == instance['RootDeviceName'] else 'false'
                        if row["InstanceState"] == 'running':
                            row["StateChangeTime"] = instance['LaunchTime'].strftime("%m/%d/%Y, %H:%M:%S")
                        elif row["InstanceState"] == 'stopped':
                            stop_time_str = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                                                      instance['StateTransitionReason'])
                            stop_time = datetime.strptime(stop_time_str.group(), "%Y-%m-%d %H:%M:%S")
                            row["StateChangeTime"] = stop_time.strftime("%m/%d/%Y, %H:%M:%S")
                rows.append(row)
            except Exception as ex:
                print('Error Extracting Volume Meta Data: ' + str(ex))
    return rows


if __name__ == "__main__":
    try:
        volume_type = 'all'

        if len(sys.argv) == 2 and len(sys.argv[1]) > 0:
            volume_type = sys.argv[1]

        header = ["AvailabilityZone", "volumeId", "VolumeType", "State", "SnapshotId", "Size", "Encrypted",
                  "CreateTime", "Device", "InstanceId", "DeleteOnTermination", "AttachTime", "InstanceState",
                  "InstanceType", "IsRootVolume", "StateChangeTime"]

        try:
            metadata = get_volumes(volume_type)
            if metadata is not None and len(metadata) > 0:
                outfile = open("volume_metadata.csv", 'w', newline='\n')
                writer = csv.writer(outfile)
                writer.writerow(header)
                for data in metadata:
                    row = [data.get(key, "") for key in header]
                    writer.writerow(row)
                outfile.close()
        except Exception as ex:
            print('Exception while Getting Volumes: ' + str(ex))
    except Exception as ex:
        print('Exception in Main' + str(ex))
