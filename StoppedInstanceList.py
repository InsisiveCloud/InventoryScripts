import re
import sys
import boto3
import datetime
import pytz

from datetime import datetime, timedelta

utc = pytz.UTC

def extract_instances(stopped_days):

    region_client = boto3.client('ec2')
    try:
        regions = region_client.describe_regions()
    except Exception as ex:
        print('Unable to fetch Regions:' + str(ex))

    for region in regions['Regions']:
        ec2 = boto3.resource('ec2', region_name=region['RegionName'])
        Filters = [{'Name': 'instance-state-name', 'Values': ['stopped']}]
        instances = ec2.instances.filter(Filters=Filters)

        for instance in instances:
            try:
                stop_time_str = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', instance.state_transition_reason)
                stop_time = datetime.strptime(stop_time_str.group(), "%Y-%m-%d %H:%M:%S")
            except Exception as ex:
                print('Error parsing Date: ' + str(ex))
            if datetime.utcnow().replace(tzinfo=utc) - stop_time.replace(tzinfo=utc) < timedelta(stopped_days):
                continue
            else:
                print(region['RegionName'] + ': '+instance._id + ' instance is ' + instance.state['Name'] + ' since '
                      + str(stop_time.replace(tzinfo=utc)))

if __name__ == "__main__":
    try:
        stopped_days = 3

        if len(sys.argv) == 2 and int(sys.argv[1]) > 0:
            stopped_days = int(sys.argv[1])

        try:
            extract_instances(stopped_days)
        except Exception as ex:
            print ('Exception while calling extract_instances'+ str(ex))
    except Exception as ex:
        print('Exception in Main' + str(ex))
