# InventoryScripts

# StoppedInstanceList
  This python script lists all instnaces that have been stopped for 'n' number of days in a particular account in all regions
  
  usage: python StoppedInstanceList.py <no_of_days>
  
  If number of days s not passed then 3 days is set as default

# VolumeMetaData
  This python script lists all volumes of all types that are "in-use" in a particular account in all regions. 
  The list is exported to a CSV with the following fields
  
  ["AvailabilityZone", "volumeId", "VolumeType", "State", "SnapshotId", "Size", "Encrypted",
                  "CreateTime", "Device", "InstanceId", "DeleteOnTermination", "AttachTime", "InstanceState",
                  "InstanceType", "IsRootVolume", "StateChangeTime"]
  
  usage: python VolumeMetaData.py <volume_type>
  
  If no volume type is provided then all volume types are listed, Possible values: gp2, io1, st1, sc1
