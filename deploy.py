#!/usr/bin/env python3
import boto3
import json
from icecream import ic
import yaml
from time import sleep

def ec2StatusWait(instances=[], status="running", napLen=10):
    while not ready:
        ready = True
        for instance in instances:
            if instance.state["Name"] != status: ready = False
        sleep(napLen)

# setup from deploy.ini
with open("deploy.yaml", "r") as ymlfile:
    config = yaml.safe_load(ymlfile)

boto3.setup_default_session(profile_name=config["aws"]["profile"], region_name=config["aws"]["region"])
ec2Client = boto3.client('ec2')
ec2Resource = boto3.resource('ec2')
iamClient = boto3.client("iam")
iamResource = boto3.resource("iam")
s3Client = boto3.client('s3')
s3Resource = boto3.resource('s3')
accountID = boto3.client('sts').get_caller_identity().get('Account')
ic(accountID)

# create keypair
keypair = ec2Client.create_key_pair(KeyName=config["keypair"]["name"])
ic(keypair)
with open(config["keypair"]["name"]+".pem", "w") as fout:
    fout.write(keypair["KeyMaterial"])

# create IAM user
iam = iamClient.create_user(UserName=config["iam"]["name"])
principal = f'{{ "AWS": "arn:aws:iam::{accountID}:user/{config["iam"]["name"]}" }}'
ic(iam)

# create usable keys from IAM user
resp = iamClient.create_access_key(UserName=config["iam"]["name"])
iamAccessKeyId = resp['AccessKey']['AccessKeyId']
iamSecretAccessKey = resp['AccessKey']['SecretAccessKey']

# create S3 bucket and upload files
bucket = s3Client.create_bucket(Bucket=config["bucket"]["name"], CreateBucketConfiguration={'LocationConstraint': config["aws"]["region"]})
ic(bucket)
bucketPolicyString = json.dumps(config["bucket"]["policy"])
bucketPolicy = bucketPolicyString\
    .replace("BUCKET_NAME",config["bucket"]["name"])\
    .replace('"PRINCIPAL_NAME"', principal)

ic(bucketPolicy)
s3Client.put_bucket_policy(Bucket=config["bucket"]["name"], Policy=bucketPolicy)
for file in config["bucket"]["upload"]:
    s3Client.upload_file(config["bucket"]["uploadDir"]+file, config["bucket"]["name"], file)

sleep(5) # replace with some kind of bucket/principal wait

# create VPC
vpc = ec2Resource.create_vpc(CidrBlock=config["vpc"]["net"])
vpc.create_tags(Tags=[{"Key":"Project","Value":config["tags"]["project"]}])
vpc.wait_until_available()
ic(vpc.id)

# create subnet
subnet = ec2Resource.create_subnet(CidrBlock = config["subnet"]["net"], VpcId= vpc.id)
subnetResponse = ec2Client.modify_subnet_attribute(
    SubnetId = subnet.id,
    MapPublicIpOnLaunch={'Value': True}
    )
ic(subnet.id)

# create internet gateway
ig = ec2Resource.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId = ig.id)
ic(ig.id)

#rtTableResponse = ec2Client.create_route_table(VpcId=vpc.id)
routeTable = vpc.create_route_table()
route = routeTable.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=ig.id)
routeTable.associate_with_subnet(SubnetId=subnet.id)

# create security group
sg = ec2Client.create_security_group(GroupName=config["sg"]["name"],
    Description=config["sg"]["desc"],
    VpcId=vpc.id)

sgResponse = ec2Client.authorize_security_group_ingress(
    GroupId=sg["GroupId"],
    IpPermissions=[
        {
            "FromPort": config["sg"]["ingress"]["fromPort"],
            "ToPort": config["sg"]["ingress"]["toPort"],
            "IpProtocol": config["sg"]["ingress"]["proto"],
            "IpRanges": [
                {"CidrIp": "0.0.0.0/0", "Description": "Internet"},
            ],
        }
    ],
)

# create instances
# ec2instances = []
for host in config["hosts"]:
    userData = config[host]["userdata"].replace("AWSACCESSKEYID", iamAccessKeyId)
    userData = userData.replace("SECRETACCESSKEY", iamSecretAccessKey)
    userData = userData.replace("REGION", config["aws"]["region"])
    userData = userData.replace("BUCKETNAME", config["bucket"]["name"])
    instances = ec2Resource.create_instances(
        ImageId=config[host]["ami"],
        #ImageId="ami-07f84a50d2dec2fa4",
        MinCount=config[host]["count"],
        MaxCount=config[host]["count"],
        InstanceType=config[host]["size"],
        KeyName=config["keypair"]["name"],
        UserData=userData,
        NetworkInterfaces=[
            {
                "SubnetId": subnet.id,
                "DeviceIndex": 0,
                "AssociatePublicIpAddress": True,
                "Groups": [sg["GroupId"]],
            }
        ]
    )
    sleep(1)
    for instance in instances:
        ec2Resource.create_tags(Resources=[instance.id], Tags=[{'Key':'Name', 'Value': config[host]["name"]}])

ec2instances = ec2Resource.instances.all()
ic(ec2instances)

# ec2StatusWait(ec2instances, "running")
# for instance in ec2instances:
#     for line in 
#     ec2SendCommand()

userInput = "foo"
while userInput != "exit":
    print('='*60)
    instanceCheck = ec2Resource.instances.all()
    for each in instanceCheck:
        print(f'EC2 instance {each.id} information:')
        print(f'Instance name: {each.tags[0]["Value"]}')
        print(f'Instance state: {each.state["Name"]}')
        # print(f'Instance AMI: {each.image.id}')
        # print(f'Instance platform: {each.platform}')
        # print(f'Instance type: {each.instance_type}')
        print(f'Public IPv4 address: {each.public_ip_address}')
        print('-'*60)
    userInput = input("To tear it all down, type 'exit': ")


# build a list of tear-down feedback
tearDown = []

# delete instances
for instance in ec2instances:
    tearDown.append(instance.terminate())

notDeadYet = 1
while notDeadYet > 0:
    notDeadYet = 0
    print("Checking for living instances...", end='')
    for instance in ec2instances:
        if instance.state["Name"] != "terminated": notDeadYet += 1
    print(f"... I still count {notDeadYet} alive.")
    sleep(10)
print("All dead!")

# delete security group
tearDown.append(ec2Client.delete_security_group(GroupId=sg["GroupId"]))

# delete internet gateway
vpc.detach_internet_gateway(InternetGatewayId = ig.id)
tearDown.append(ig.delete())

# delete subnet
tearDown.append(subnet.delete())

# delete route table
tearDown.append(routeTable.delete())

# delete VPC
tearDown.append(vpc.delete())

# delete S3 bucket
s3Resource.Bucket(config["bucket"]["name"]).objects.all().delete()
tearDown.append(s3Client.delete_bucket(Bucket = config["bucket"]["name"]))

# delete usable access keys
tearDown.append(iamClient.delete_access_key(AccessKeyId=iamAccessKeyId))

# delete IAM user
tearDown.append(iamClient.delete_user(UserName = config["iam"]["name"]))

# delete keypair
tearDown.append(ec2Client.delete_key_pair(KeyName=config["keypair"]["name"]))

ic(tearDown)
