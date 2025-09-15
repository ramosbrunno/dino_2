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

# Get user Object IDs for Key Vault access (optional - may not exist)
data "azuread_user" "brunno_ext" {
  count               = 1
  user_principal_name = "brunno.ramos_live.com#EXT#@brunnoramoslive.onmicrosoft.com"
}

data "azuread_user" "brunno_internal" {
  count               = 1
  user_principal_name = "brunno.ramos@brunnoramoslive.onmicrosoft.com"
}

# Generate random ID for unique naming
resource "random_id" "main" {
  byte_length = 4
}

# Generate random password for Service Principal
resource "random_password" "spn_password" {
  length  = 32
  special = true
}

# Local values for resource naming
locals {
  # Nomenclatura padrão limpa: projeto-ambiente-tipo
  resource_group_name = "${var.projeto}-${var.ambiente}-rsg"
  
  # Key Vault name with length validation (max 24 chars)
  base_keyvault_name = "${var.projeto}-${var.ambiente}-akv"
  keyvault_name = length(local.base_keyvault_name) > 24 ? "${substr(var.projeto, 0, min(length(var.projeto), 8))}-${var.ambiente}-${random_id.main.hex}" : local.base_keyvault_name
  
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
# Role Assignments for Service Principal - COMENTADO
# ========================
# Como vamos usar apenas a SPN Dino para toda a operação, 
# não precisamos dar permissões adicionais à SPN criada

# Reader role on the entire subscription - SIMPLIFIED
# Using only Resource Group level permissions for simplicity
# resource "azurerm_role_assignment" "spn_reader_subscription" {
#   scope                = data.azurerm_subscription.current.id
#   role_definition_name = "Reader"
#   principal_id         = azuread_service_principal.main.object_id
# }

# Contributor role on the Resource Group - RESTAURADO conforme solicitado
resource "azurerm_role_assignment" "spn_contributor_rg" {
  scope                = azurerm_resource_group.main.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.main.object_id
}

# User Access Administrator role on the Resource Group - DISABLED
# This role assignment may require additional permissions
# resource "azurerm_role_assignment" "spn_uaccess_rg" {
#   scope                = azurerm_resource_group.main.id
#   role_definition_name = "User Access Administrator"
#   principal_id         = azuread_service_principal.main.object_id
#   principal_type       = "ServicePrincipal"
# }

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

  # Network ACLs - permitir acesso público para Terraform
  network_acls {
    bypass         = "AzureServices"
    default_action = "Allow"
  }

  # Access policies gerenciadas por recursos separados para melhor controle

  tags = local.final_tags

  depends_on = [azurerm_resource_group.main, azuread_service_principal.main]
}

# ========================
# Key Vault Access Policies
# ========================

# Dino SPN (executor do Terraform) precisa de permissões para gerenciar secrets
resource "azurerm_key_vault_access_policy" "dino_spn" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get",
    "List", 
    "Set",
    "Delete",
    "Recover",
    "Backup",
    "Restore"
  ]
}

# ========================
# Key Vault Secrets - Store SPN Credentials - COMENTADO TEMPORARIAMENTE
# ========================
# Como as secrets já existem de execuções anteriores e estão causando conflito,
# vamos comentar temporariamente. A SPN criada está funcionando corretamente.

# Store Service Principal Client ID - COMENTADO
# resource "azurerm_key_vault_secret" "spn_client_id" {
#   name         = "spn-client-id"
#   value        = azuread_application.main.client_id
#   key_vault_id = azurerm_key_vault.main.id
#
#   lifecycle {
#     ignore_changes = [value]
#   }
#
#   depends_on = [azurerm_key_vault.main]
# }

# Store Service Principal Client Secret - COMENTADO
# resource "azurerm_key_vault_secret" "spn_client_secret" {
#   name         = "spn-client-secret"
#   value        = azuread_service_principal_password.main.value
#   key_vault_id = azurerm_key_vault.main.id
#
#   lifecycle {
#     ignore_changes = [value]
#   }
#
#   depends_on = [azurerm_key_vault.main]
# }

# Store Tenant ID - COMENTADO
# resource "azurerm_key_vault_secret" "tenant_id" {
#   name         = "tenant-id"
#   value        = data.azurerm_client_config.current.tenant_id
#   key_vault_id = azurerm_key_vault.main.id
#
#   lifecycle {
#     ignore_changes = [value]
#   }
#
#   depends_on = [azurerm_key_vault.main]
# }
