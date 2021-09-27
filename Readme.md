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
`ssh-keygen -t rsa -C "your_email@example.com" -f ../tf-cloud-init`

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

`ssh attack@AttackIPHere -i ../tf-cloud-init`
