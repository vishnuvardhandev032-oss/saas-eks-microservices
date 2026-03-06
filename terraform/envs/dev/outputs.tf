output "aws_region" {
  value = var.aws_region
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}

output "ecr_users_repo_url" {
  value = aws_ecr_repository.users.repository_url
}

output "ecr_billing_repo_url" {
  value = aws_ecr_repository.billing.repository_url
}

output "ecr_gateway_repo_url" {
  value = aws_ecr_repository.gateway.repository_url
}