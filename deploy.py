#!/usr/bin/env python3
import boto3
import json
from icecream import ic
import yaml

# setup from deploy.ini
with open("deploy.yaml", "r") as ymlfile:
    config = yaml.safe_load(ymlfile)

boto3.setup_default_session(profile_name=config["aws"]["profile"], region_name=config["aws"]["region"])

ec2 = boto3.client('ec2')
response = ec2.create_key_pair(KeyName=config["keypair"]["name"])
ic(response)

ec2instances = []
for host in config["hosts"]:
    instance = ec2.create_instances(
        ImageId=config[host]["ami"],
        MinCount=config[host]["count"],
        MaxCount=config[host]["count"],
        InstanceType="t2.nano",
        KeyName=config["keypair"]["name"],
        UserData=[host]["userdata"],
        NetworkInterfaces=[
            {
                "SubnetId": SUBNET_ID,
                "DeviceIndex": 0,
                "AssociatePublicIpAddress": True,
                "Groups": [sg.group_id],
            }
        ],
    )

ec2 = boto3.resource('ec2')
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[{"Key":"TestVPC","Value":"default_vpc"}])
vpc.wait_until_available()
print(vpc.id)
subnet = ec2.create_subnet(CidrBlock = '10.0.2.0/24', VpcId= vpc.id)
print(subnet.id)
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId = ig.id)
print(ig.id)

response = sg.authorize_ingress(
    IpPermissions=[
        {
            "FromPort": 22,
            "ToPort": 22,
            "IpProtocol": "tcp",
            "IpRanges": [
                {"CidrIp": "0.0.0.0/0", "Description": "internet"},
            ],
        },
        {
            "FromPort": 80,
            "ToPort": 80,
            "IpProtocol": "tcp",
            "IpRanges": [
                {"CidrIp": "0.0.0.0/0", "Description": "internet"},
            ],
        },
    ],
)



response = ec2.delete_key_pair(KeyName=config["keypair"]["name"])
