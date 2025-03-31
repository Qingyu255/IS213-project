output "ecr_arn" {
  value = aws_ecr_repository.ecr.arn
}

output "ecr_id" {
  value = aws_ecr_repository.ecr.id
}

output "ecr_url" {
  value = aws_ecr_repository.ecr.repository_url
}
