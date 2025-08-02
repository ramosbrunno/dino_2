# Main Outputs - Complete Infrastructure
# Aggregates outputs from all modules

# ========================
# Foundation Module Outputs
# ========================

output "resource_group_name" {
  description = "Nome do Resource Group criado"
  value       = module.foundation.resource_group_name
}

output "resource_group_id" {
  description = "ID do Resource Group criado"
  value       = module.foundation.resource_group_id
}

output "key_vault_name" {
  description = "Nome do Key Vault criado"
  value       = module.foundation.key_vault_name
}

output "key_vault_id" {
  description = "ID do Key Vault criado"
  value       = module.foundation.key_vault_id
}

output "key_vault_uri" {
  description = "URI do Key Vault"
  value       = module.foundation.key_vault_uri
}

output "service_principal_name" {
  description = "Nome do Service Principal criado"
  value       = module.foundation.service_principal_name
}

output "service_principal_application_id" {
  description = "Application ID do Service Principal"
  value       = module.foundation.service_principal_application_id
}

# ========================
# Databricks Module Outputs (Always Created)
# ========================

output "databricks_workspace_name" {
  description = "Nome do Azure Databricks Workspace"
  value       = module.databricks.databricks_workspace_name
}

output "databricks_workspace_url" {
  description = "URL do Azure Databricks Workspace"
  value       = module.databricks.databricks_workspace_url
}

output "databricks_workspace_id" {
  description = "ID do Azure Databricks Workspace"
  value       = module.databricks.databricks_workspace_id
}

output "unity_catalog_storage_name" {
  description = "Nome da Storage Account do Unity Catalog"
  value       = module.databricks.unity_catalog_storage_name
}

output "unity_catalog_storage_root" {
  description = "URI root do Unity Catalog Storage"
  value       = module.databricks.unity_catalog_storage_root
}

output "databricks_access_token" {
  description = "Token de acesso do Databricks (sensível)"
  value       = module.databricks.databricks_access_token
  sensitive   = true
}

# ========================
# Deployment Summary
# ========================

output "deployment_summary" {
  description = "Resumo completo da implantação"
  value = {
    foundation = module.foundation.foundation_summary
    databricks = module.databricks.databricks_summary
    modules_enabled = {
      foundation = true
      databricks = true
    }
    deployment_info = {
      projeto           = var.projeto
      ambiente          = var.ambiente
      location          = var.location
      terraform_version = ">=1.0"
      features_enabled  = ["foundation", "databricks-premium", "unity-catalog", "serverless"]
      timestamp         = timestamp()
    }
  }
}
