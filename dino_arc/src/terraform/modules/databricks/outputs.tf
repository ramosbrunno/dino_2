# Databricks Module Outputs - Premium Configuration

# ========================
# Databricks Workspace Outputs
# ========================

output "databricks_workspace_name" {
  description = "Nome do Azure Databricks Workspace"
  value       = azurerm_databricks_workspace.main.name
}

output "databricks_workspace_id" {
  description = "ID do Azure Databricks Workspace"
  value       = azurerm_databricks_workspace.main.id
}

output "databricks_workspace_url" {
  description = "URL do Azure Databricks Workspace"
  value       = azurerm_databricks_workspace.main.workspace_url
}

output "databricks_workspace_resource_id" {
  description = "Resource ID do Azure Databricks Workspace"
  value       = azurerm_databricks_workspace.main.workspace_id
}

output "databricks_sku" {
  description = "SKU do Azure Databricks Workspace"
  value       = azurerm_databricks_workspace.main.sku
}

# ========================
# Storage Account Outputs (DBFS Root)
# ========================

# Outputs relacionados ao storage do DBFS removidos - Azure gerencia automaticamente

# ========================
# Unity Catalog Storage Outputs
# ========================

output "unity_catalog_storage_name" {
  description = "Nome da Storage Account para Unity Catalog"
  value       = azurerm_storage_account.unity_catalog.name
}

output "unity_catalog_storage_id" {
  description = "ID da Storage Account para Unity Catalog"
  value       = azurerm_storage_account.unity_catalog.id
}

output "unity_catalog_storage_endpoint" {
  description = "Endpoint da Storage Account para Unity Catalog"
  value       = azurerm_storage_account.unity_catalog.primary_blob_endpoint
}

output "unity_catalog_container_name" {
  description = "Nome do container do Unity Catalog"
  value       = azurerm_storage_container.unity_catalog.name
}

output "unity_catalog_storage_root" {
  description = "URI root para Unity Catalog Storage"
  value       = "abfss://${azurerm_storage_container.unity_catalog.name}@${azurerm_storage_account.unity_catalog.name}.dfs.core.windows.net/"
}

# Commented out because we're using Databricks-managed access connector
# output "unity_catalog_access_connector_id" {
#   description = "ID do Access Connector para Unity Catalog"
#   value       = azurerm_databricks_access_connector.unity_catalog.id
# }

output "databricks_access_token" {
  description = "Token de acesso do Databricks (sensível)"
  value       = random_password.databricks_token.result
  sensitive   = true
}

# ========================
# Configuration Outputs
# ========================

output "public_network_access_enabled" {
  description = "Se o acesso à rede pública está habilitado"
  value       = azurerm_databricks_workspace.main.public_network_access_enabled
}

output "managed_resource_group" {
  description = "Resource Group gerenciado pelo Databricks"
  value       = azurerm_databricks_workspace.main.managed_resource_group_name
}

# ========================
# Summary Output
# ========================

output "databricks_summary" {
  description = "Resumo completo dos recursos do Databricks Premium"
  value = {
    workspace = {
      name         = azurerm_databricks_workspace.main.name
      id           = azurerm_databricks_workspace.main.id
      url          = azurerm_databricks_workspace.main.workspace_url
      resource_id  = azurerm_databricks_workspace.main.workspace_id
      sku          = azurerm_databricks_workspace.main.sku
      location     = azurerm_databricks_workspace.main.location
      features     = ["unity-catalog", "serverless", "premium"]
    }
    storage = {
      # dbfs_root removido - Azure gerencia automaticamente
      unity_catalog = {
        name               = azurerm_storage_account.unity_catalog.name
        id                 = azurerm_storage_account.unity_catalog.id
        primary_endpoint   = azurerm_storage_account.unity_catalog.primary_blob_endpoint
        container_name     = azurerm_storage_container.unity_catalog.name
        hierarchical_namespace = azurerm_storage_account.unity_catalog.is_hns_enabled
      }
    }
    configuration = {
      public_network_access = azurerm_databricks_workspace.main.public_network_access_enabled
      managed_resource_group = azurerm_databricks_workspace.main.managed_resource_group_name
      secrets_stored = true
      unity_catalog_enabled = true
      serverless_enabled = true
    }
    secrets_stored = {
      workspace_url = azurerm_key_vault_secret.databricks_workspace_url.name
      workspace_id = azurerm_key_vault_secret.databricks_workspace_id.name
      unity_catalog_storage_name = azurerm_key_vault_secret.unity_catalog_storage_name.name
      unity_catalog_storage_key = azurerm_key_vault_secret.unity_catalog_storage_key.name
    }
  }
}
