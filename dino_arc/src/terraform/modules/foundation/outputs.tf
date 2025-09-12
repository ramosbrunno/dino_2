# Foundation Module Outputs

# ========================
# Resource Group Outputs
# ========================

output "resource_group_name" {
  description = "Nome do Resource Group criado"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "ID do Resource Group criado"
  value       = azurerm_resource_group.main.id
}

output "resource_group_location" {
  description = "Localização do Resource Group"
  value       = azurerm_resource_group.main.location
}

# ========================
# Key Vault Outputs
# ========================

output "key_vault_name" {
  description = "Nome do Key Vault criado"
  value       = azurerm_key_vault.main.name
}

output "key_vault_id" {
  description = "ID do Key Vault criado"
  value       = azurerm_key_vault.main.id
}

output "key_vault_uri" {
  description = "URI do Key Vault"
  value       = azurerm_key_vault.main.vault_uri
}

# ========================
# Service Principal Outputs
# ========================

output "service_principal_name" {
  description = "Nome do Service Principal criado"
  value       = azuread_service_principal.main.display_name
}

output "service_principal_object_id" {
  description = "Object ID do Service Principal"
  value       = azuread_service_principal.main.object_id
}

output "service_principal_application_id" {
  description = "Application ID do Service Principal"
  value       = azuread_application.main.client_id
}

output "service_principal_tenant_id" {
  description = "Tenant ID"
  value       = data.azurerm_client_config.current.tenant_id
}

# ========================
# Tags Output
# ========================

output "resource_tags" {
  description = "Tags aplicadas aos recursos"
  value       = local.final_tags
}

# ========================
# Summary Output
# ========================

output "foundation_summary" {
  description = "Resumo dos recursos da infraestrutura base"
  value = {
    resource_group = {
      name     = azurerm_resource_group.main.name
      id       = azurerm_resource_group.main.id
      location = azurerm_resource_group.main.location
    }
    key_vault = {
      name = azurerm_key_vault.main.name
      id   = azurerm_key_vault.main.id
      uri  = azurerm_key_vault.main.vault_uri
      sku  = azurerm_key_vault.main.sku_name
    }
    service_principal = {
      name           = azuread_service_principal.main.display_name
      object_id      = azuread_service_principal.main.object_id
      application_id = azuread_application.main.client_id
      tenant_id      = data.azurerm_client_config.current.tenant_id
    }
    secrets_stored = {
      client_id     = azurerm_key_vault_secret.spn_client_id.name
      client_secret = azurerm_key_vault_secret.spn_client_secret.name
      tenant_id     = azurerm_key_vault_secret.tenant_id.name
    }
  }
}
