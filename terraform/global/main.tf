##### These are critical, long-lived resources managed separately from ephemeral, environment-specific resources #####
##### DO NOT run `terraform destroy` once setup for an environment. There is no need to run this again for the same environment #####
provider "aws" {
  profile = "is213project"
  region = var.aws_region
}

module "cognito" {
  source = "./cognito"
  environment = var.environment
  callback_urls = var.callback_urls
  user_pool_name = var.user_pool_name
  logout_urls = var.logout_urls
  project_name = var.project_name
}

module "ecr" {
  source       = "./ecr"
  aws_region   = var.aws_region
  project_name = var.project_name
  environment  = var.environment
}

module "s3" {
  source              = "./s3"
  project_name        = var.project_name
  environment         = var.environment
  cors_allowed_origins = var.cors_allowed_origins
}
