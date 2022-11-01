# CTF range build software
This repo is for the purpose of asset creation for a CTF.

## Learning Objective
Parse some PCAP - maybe a web log too. Identify certain attacks, especially XXE.

## Dependencies
- [AWS IAM Credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to interact with an AWS account
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed
- [Boto3](https://aws.amazon.com/sdk-for-python/) installed

## Files
- Readme.md:        This file explains the repository
- deploy.py:        The script that builds, downloads assets, and destroys
- deploy.yaml:      Settings for the range
- requirements.txt: `pip3 install -r requirements.txt` to fetch the dependencies deploy.py needs
- assets/:          Files copied to instances
- assets/website/:  Makes up the web server at the center of this story
- output/:          Artifacts created in the range can be pulled to this directory

## Setup Steps
### Set Default AWS Credentials
- Check to see what you have in your `~/.aws/credentials` file:
  - `cat ~/.aws/credentials`
- Change the `profile` variable in `deploy.yaml` to your favorite AWS profile:
```
aws:
  profile: elgee-mgmt
  region: us-east-2
```

### Create the Range with Boto3
```
$ python3 deploy.py
------------------------------------------------------------
EC2 instance i-07e5b449a9cf52c2a information:
Instance name: WebClients
Instance state: running
Public IPv4 address: 18.222.86.46
------------------------------------------------------------
EC2 instance i-09ed819f96d09a07f information:
Instance name: Attacker
Instance state: running
Public IPv4 address: 18.222.86.32
------------------------------------------------------------
EC2 instance i-0167d89231c21d1e3 information:
Instance name: WebServer
Instance state: running
Public IPv4 address: 3.138.184.18
------------------------------------------------------------
 Region is us-east-2
 S3 bucket is s3://hammer-bucket8675309
 AWS AccessKeyID is AKIAABC123ABC1234567 and SecretAccessKey is kwijibokwijibokwijibokwijibokwijibokwijibo1
Type l to List available files
Type d to Download target assets
Type e to Exit and tear it all down
Type anything else to reload target status:
```

### Optional: connect to the website host with the IP from the Boto output
- `ssh ubuntu@websiteIPHere -i hammer-deploy.pem`

## Tear Down Steps
- Type `e` at the prompt:
```
Type anything else to reload target status:  e
Checking for living instances...  ...  I count 17 alive.  Sleeping for 10s.
Checking for living instances...  ...  I count 1 alive.  Sleeping for 10s.
Checking for living instances...  ...  I count 0 alive.
  All dead!
ic| tearDown: [{'ResponseMetadata': {'HTTPHeaders': {'cache-control': 'no-cache, no-store',
[...]
Successfully torn down!
```
