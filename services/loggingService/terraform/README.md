# Terraform

Terraform is an Infrastructure as Code tool that helps manage infrastructure, secrets, and configurations intuitively on any cloud.

We use Terraform to build and deploy our infrastructure.

## Pre-requisites
### Install Terraform:
- https://developer.hashicorp.com/terraform/install

### Install AWS CLI:
- https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

### Generate IAM Access Key for AWS CLI
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html

## Quickstart
Ensure Pre-quisites above are fulfilled.
1. Configure AWS CLI (Only Needed to be done once initially)
    ```sh
    cd ~/.aws

    # requires AWS CLI accessKey
    aws configure
    ```
2. You can now run terraform scripts with `terraform plan` `terraform apply` and `terraform apply`. Please see individual sub-directories' README.md for detailed setup and tear down instructions.

## Troubleshooting
- When running `terraform apply`:
    - **Error:** `Retrieving AWS account details: validating provider credentials: retrieving caller identity from STS: operation error STS: GetCallerIdentity, https response error StatusCode: 403, RequestID:...`
    - **Fix:** Recreate AccessKey and `aws configure` again