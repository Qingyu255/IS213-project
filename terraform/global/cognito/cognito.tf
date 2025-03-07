resource "aws_cognito_user_pool" "cognito" {
  name                     = var.user_pool_name
  auto_verified_attributes = ["email"]
  
  alias_attributes = ["email"]

  # Note that this custom id represents the UMS generated userId 
  schema {
    name                = "id"
    attribute_data_type = "String"
    mutable             = false
  }

  # schema {
  #   name                = "lastname"
  #   attribute_data_type = "String"
  #   mutable             = true
  # }

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  tags = {
    Environment = var.environment
  }

  lifecycle {
    # This tells Terraform to ignore any differences in the schema block.
    ignore_changes = [schema]
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name             = "${var.user_pool_name}-client"
  user_pool_id     = aws_cognito_user_pool.cognito.id

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                   = ["code", "implicit"]
  allowed_oauth_scopes                  = ["phone", "email", "openid", "profile", "aws.cognito.signin.user.admin"]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  supported_identity_providers = ["COGNITO"]

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_CUSTOM_AUTH"
  ]
}

resource "aws_cognito_user_pool_domain" "domain" {
  domain      = "${var.project_name}-${var.environment}"
  user_pool_id = aws_cognito_user_pool.cognito.id
}
