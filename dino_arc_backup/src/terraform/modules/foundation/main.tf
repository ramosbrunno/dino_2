# Foundation Module - Resource Group, Service Principal, and Key Vault
# This module creates the base infrastructure for the project

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Get current client configuration
data "azurerm_client_config" "current" {}
data "azurerm_subscription" "current" {}

# Generate random suffix for Key Vault name (must be globally unique)
resource "random_string" "keyvault_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Generate random password for Service Principal
resource "random_password" "spn_password" {
  length  = 32
  special = true
}

# Local values for resource naming
locals {
  # Nomenclatura padrão: projeto-ambiente-sufixo
  resource_group_name = "${var.projeto}-${var.ambiente}-rsg"
  keyvault_name      = "${var.projeto}-${var.ambiente}-akv-${random_string.keyvault_suffix.result}"
  spn_display_name   = "${var.projeto}-${var.ambiente}-spn"
  
  # Tags padrão que serão aplicadas a todos os recursos
  default_tags = {
    Project     = var.projeto
    Environment = var.ambiente
    ManagedBy   = "terraform"
    CreatedBy   = "dino-arc-cli"
    Module      = "foundation"
  }
  
  # Merge das tags padrão com tags customizadas
  final_tags = merge(local.default_tags, var.tags)
}

# ========================
# Resource Group
# ========================

resource "azurerm_resource_group" "main" {
  name     = local.resource_group_name
  location = var.location

  tags = local.final_tags
}

# ========================
# Service Principal Creation
# ========================

# Create Azure AD Application
resource "azuread_application" "main" {
  display_name = local.spn_display_name
  
  tags = [
    var.projeto,
    var.ambiente,
    "terraform-managed"
  ]
}

# Create Service Principal
resource "azuread_service_principal" "main" {
  client_id                    = azuread_application.main.client_id
  app_role_assignment_required = false
  
  tags = [
    var.projeto,
    var.ambiente,
    "terraform-managed"
  ]
}

# Create Service Principal Password
resource "azuread_service_principal_password" "main" {
  service_principal_id = azuread_service_principal.main.object_id
  display_name         = "terraform-managed-secret"
}

# ========================
# Role Assignments for Service Principal
# ========================

# Reader role on the entire subscription
resource "azurerm_role_assignment" "spn_reader_subscription" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Reader"
  principal_id         = azuread_service_principal.main.object_id
}

# Contributor role on the Resource Group
resource "azurerm_role_assignment" "spn_contributor_rg" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.main.object_id
}

# User Access Administrator role on the Resource Group
resource "azurerm_role_assignment" "spn_uaccess_rg" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "User Access Administrator"
  principal_id         = azuread_service_principal.main.object_id
  principal_type       = "ServicePrincipal"
}

# ========================
# Key Vault Creation
# ========================

resource "azurerm_key_vault" "main" {
  name                = local.keyvault_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id          = data.azurerm_client_config.current.tenant_id
  
  # SKU padrão: standard
  sku_name = "standard"

  # Key Vault configuration - configurações padrão otimizadas
  enabled_for_deployment          = false
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  
  # Soft delete configuration - valores padrão
  soft_delete_retention_days = 7
  purge_protection_enabled   = false

  # Network ACLs - configuração segura padrão
  network_acls {
    bypass         = "AzureServices"
    default_action = "Deny"
  }

  tags = local.final_tags

  depends_on = [azurerm_resource_group.main]
}

# ========================
# Key Vault Access Policies
# ========================

# Access policy for the current user/service principal (bootstrap)
resource "azurerm_key_vault_access_policy" "current_user" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  # Permissões administrativas completas
  key_permissions = [
    "Backup", "Create", "Decrypt", "Delete", "Encrypt", "Get", "Import", 
    "List", "Purge", "Recover", "Restore", "Sign", "UnwrapKey", 
    "Update", "Verify", "WrapKey", "Release", "Rotate", "GetRotationPolicy", "SetRotationPolicy"
  ]
  
  secret_permissions = [
    "Backup", "Delete", "Get", "List", "Purge", "Recover", "Restore", "Set"
  ]
  
  certificate_permissions = [
    "Backup", "Create", "Delete", "DeleteIssuers", "Get", "GetIssuers", 
    "Import", "List", "ListIssuers", "ManageContacts", "ManageIssuers", 
    "Purge", "Recover", "Restore", "SetIssuers", "Update"
  ]

  depends_on = [azurerm_key_vault.main]
}

# Access policy for the created Service Principal
resource "azurerm_key_vault_access_policy" "service_principal" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azuread_service_principal.main.object_id

  # Permissões para a Service Principal
  key_permissions = [
    "Get", "List", "Create", "Delete", "Update", "Decrypt", "Encrypt", "Sign", "Verify"
  ]
  
  secret_permissions = [
    "Get", "List", "Set", "Delete"
  ]
  
  certificate_permissions = [
    "Get", "List", "Create", "Delete", "Update"
  ]

  depends_on = [azurerm_key_vault.main, azuread_service_principal.main]
}

# ========================
# Key Vault Secrets - Store SPN Credentials
# ========================

# Store Service Principal Client ID
resource "azurerm_key_vault_secret" "spn_client_id" {
  name         = "spn-client-id"
  value        = azuread_application.main.client_id
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.current_user]
}

# Store Service Principal Client Secret
resource "azurerm_key_vault_secret" "spn_client_secret" {
  name         = "spn-client-secret"
  value        = azuread_service_principal_password.main.value
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.current_user]
}

# Store Tenant ID
resource "azurerm_key_vault_secret" "tenant_id" {
  name         = "tenant-id"
  value        = data.azurerm_client_config.current.tenant_id
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.current_user]
}
