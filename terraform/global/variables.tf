variable "aws_region" {
  description = "AWS region for global resources"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment tag (e.g., dev, staging, prod)"
  type        = string
}

## Cognito ##
variable "user_pool_name" {
  description = "Name of the Cognito user pool"
  type        = string
}

variable "callback_urls" {
  description = "List of callback URLs for the user pool client"
  type        = list(string)
}

variable "logout_urls" {
  description = "List of logout URLs for the user pool client"
  type        = list(string)
}

## S3 ##
variable "cors_allowed_origins" {
  description = "List of allowed origins for CORS in S3"
  type        = list(string)
  default     = ["http://localhost:3000"]
}
