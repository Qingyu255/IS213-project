# Global Infrastructure Modules

This directory contains Terraform configurations for global (persistent) infrastructure resources that are shared across all environments (development, staging, production). Although AWS Cognito is regional, they are treated as global resources because they are centrally managed and used across multiple environments.

## Directory Structure

```
terraform/global/
├── cognito/
│   ├── cognito.tf           # Defines the Cognito user pool and client configuration.
|   └── variables.tf
├── route53/
│   ├── route53.tf           # Creates a Route 53 zone.
|   └── variables.tf
├─ ecr/
│   ├── ecr.tf           # Provisions an ECR repository for storing container images.
|   └── variables.tf
├── main.tf           # Spins up the cognito, route53 and ecr modules
├── variables.tf      # Declares variables such as aws_region, repo_name, environment tag, etc.
└── terraform.tfvars  # Assigns variable values
```

## Purpose

- **Cognito:**  
  Manages our user authentication and identity services. Although Cognito is regional, we treat it as a global resource because it serves all environments and should be managed independently.

- **Route 53:**  
  Provides a hosted DNS zone for our domain, ensuring consistent and reliable DNS management for our CRM system.

- **ECR:**  
  Hosts our container images that are used across different environments. As a persistent resource, it is shared by all teams and CI/CD pipelines.

## Usage

### Setup

To provision the global resources, in the same directory as this `README` and run the following commands:

1. **Initialise Terraform:**
   ```sh
   terraform init
   ```

2. **Review the Execution Plan:**
   ```sh
   terraform plan
   ```

3. **Apply the Configuration:**
   ```sh
   terraform apply
   ```
   This will create the resources as defined in the module (Cognito, Route 53 and ECR).

**Use `terraform apply` to apply any changes to the resources**

### Tear Down

These global resources are meant to be long-lived and should only be destroyed when **absolutely** necessary (for example, during a complete infrastructure teardown in a test environment).

**Note:** There should not be a need to `terraform destroy` in this global directory, as these resources (e.g., your DNS zone and container repository) are critical and shared across environments. If you do plan on destroying the global resources, please discuss with the team.
