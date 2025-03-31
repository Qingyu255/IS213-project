## Cognito ##
output "cognito_user_pool_id" {
  value       = module.cognito.cognito_user_pool_id
}

output "cognito_user_pool_client_id" {
  description = "The ID of the Cognito User Pool Client"
  value       = module.cognito.cognito_user_pool_client_id
}

## ECR ##
output "ecr_arn" {
  value = module.ecr.ecr_arn
}

output "ecr_id" {
  value = module.ecr.ecr_id
}

output "ecr_url" {
  value = module.ecr.ecr_url
}

## S3 ##
output "s3_bucket_id" {
  description = "The ID of the public S3 bucket"
  value       = module.s3.s3_bucket_id
}

output "s3_bucket_arn" {
  description = "The ARN of the public S3 bucket"
  value       = module.s3.s3_bucket_arn
}

output "s3_bucket_domain_name" {
  description = "The domain name of the public S3 bucket"
  value       = module.s3.s3_bucket_domain_name
}

output "s3_bucket_website_endpoint" {
  description = "The website endpoint of the public S3 bucket"
  value       = module.s3.s3_bucket_website_endpoint
}
