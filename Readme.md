# Hammer CTF 2022 range build
This is for the purpose of asset creation for a CTF. Some code used from Terraform's [HashiCorp Learn platform](https://learn.hashicorp.com/tutorials/terraform/cloud-init?in=terraform/provision).

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
- website/:     Makes up the web server at the center of this story

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
[...]

$ terraform show #optional - to show assets and addresses again
```

### Connect to the website host with the IP from the Terraform Output
- `ssh website@websiteIPHere -i ../tf-cloud-init`
- If you've lost track of those IPs, just `terraform show` to see them again

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
