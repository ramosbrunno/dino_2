# Main Outputs - Modular Architecture
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
# Databricks Module Outputs (Conditional)
# ========================

output "databricks_workspace_name" {
  description = "Nome do Azure Databricks Workspace (se habilitado)"
  value       = var.enable_databricks ? module.databricks[0].databricks_workspace_name : null
}

output "databricks_workspace_url" {
  description = "URL do Azure Databricks Workspace (se habilitado)"
  value       = var.enable_databricks ? module.databricks[0].databricks_workspace_url : null
}

output "databricks_workspace_id" {
  description = "ID do Azure Databricks Workspace (se habilitado)"
  value       = var.enable_databricks ? module.databricks[0].databricks_workspace_id : null
}

# ========================
# SQL Database Module Outputs (Conditional)
# ========================

output "sql_server_name" {
  description = "Nome do SQL Server para logs do Dino SDK (se habilitado)"
  value       = var.enable_sql_database ? module.sql_database[0].sql_server_name : null
}

output "sql_server_fqdn" {
  description = "FQDN do SQL Server para logs do Dino SDK (se habilitado)"
  value       = var.enable_sql_database ? module.sql_database[0].sql_server_fqdn : null
}

output "sql_database_name" {
  description = "Nome do banco de dados de logs do Dino SDK (se habilitado)"
  value       = var.enable_sql_database ? module.sql_database[0].sql_database_name : null
}

output "sql_connection_string_secret_name" {
  description = "Nome do secret no Key Vault com connection string (se habilitado)"
  value       = var.enable_sql_database ? module.sql_database[0].connection_string_secret_name : null
}

output "dino_sdk_database_config" {
  description = "Configuração do banco para uso do Dino SDK (se habilitado)"
  value       = var.enable_sql_database ? module.sql_database[0].dino_sdk_database_config : null
  sensitive   = false
}

# ========================
# Deployment Summary
# ========================

output "deployment_summary" {
  description = "Resumo completo da implantação"
  value = {
    foundation = module.foundation.foundation_summary
    databricks = var.enable_databricks ? module.databricks[0].databricks_summary : null
    sql_database = var.enable_sql_database ? module.sql_database[0].dino_sdk_database_config : null
    modules_enabled = {
      foundation = true
      databricks = var.enable_databricks
      sql_database = var.enable_sql_database
    }
    deployment_info = {
      projeto           = var.projeto
      ambiente          = var.ambiente
      location          = var.location
      terraform_version = ">=1.0"
      timestamp         = timestamp()
    }
  }
  sensitive = false
}
