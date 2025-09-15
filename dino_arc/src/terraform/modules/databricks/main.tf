# Databricks Module - Azure Databricks Workspace Premium with Unity Catalog
# This module creates Azure Databricks workspace with Premium SKU, Unity Catalog, and Serverless configurations

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Generate random token for Databricks API (simulated for configuration)
resource "random_password" "databricks_token" {
  length  = 32
  special = false
  upper   = true
  lower   = true
  numeric = true
}

# Generate random ID for unique naming
resource "random_id" "storage" {
  byte_length = 4
}

# Local values for resource naming and configuration
locals {
  # Nomenclatura descritiva: projeto-ambiente-tipo-funcionalidade
  databricks_workspace_name = "${var.projeto}-${var.ambiente}-dbw"
  
  # Storage account name with length validation (max 24 chars, lowercase only)
  base_storage_name = lower("${replace(var.projeto, "-", "")}${var.ambiente}sauc")
  unity_catalog_storage = length(local.base_storage_name) > 24 ? "${substr(replace(var.projeto, "-", ""), 0, min(length(replace(var.projeto, "-", "")), 10))}${var.ambiente}${random_id.storage.hex}" : local.base_storage_name
  
  # Tags padrão para o módulo Databricks
  default_tags = {
    Project     = var.projeto
    Environment = var.ambiente
    ManagedBy   = "terraform"
    CreatedBy   = "dino-arc-cli"
    Module      = "databricks"
    SKU         = "premium"
    Features    = "unity-catalog,serverless"
  }
  
  # Merge das tags padrão com tags customizadas
  final_tags = merge(local.default_tags, var.tags)
}

# ========================
# Storage Account for Databricks (DBFS Root) - REMOVIDO
# ========================
# O Azure criará automaticamente o storage account do DBFS
# Mantemos apenas o storage do Unity Catalog

# ========================
# Storage Account for Unity Catalog
# ========================

resource "azurerm_storage_account" "unity_catalog" {
  name                     = local.unity_catalog_storage
  resource_group_name      = var.resource_group_name
  location                = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # Configurações necessárias para Unity Catalog
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true
  is_hns_enabled                  = true  # Necessário para Unity Catalog
  
  # Network rules
  network_rules {
    default_action = "Allow"
    bypass         = ["AzureServices"]
  }

  tags = merge(local.final_tags, {
    Purpose = "unity-catalog"
  })
}

# Storage Container for Unity Catalog
resource "azurerm_storage_container" "unity_catalog" {
  name                  = "unity-catalog"
  storage_account_name  = azurerm_storage_account.unity_catalog.name
  container_access_type = "private"
}

# Data sources for security groups (disabled for now)
# Uncomment and create the group manually if needed
# data "azuread_group" "metastore_admins" {
#   display_name     = "metastore_admins"
#   security_enabled = true
# }

# ========================
# Azure Databricks Workspace Premium
# ========================

resource "azurerm_databricks_workspace" "main" {
  name                = local.databricks_workspace_name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "premium"  # Always Premium for Unity Catalog

  # Configurações de rede para acesso à internet e Serverless
  public_network_access_enabled = true   # Permitir acesso à internet
  
  # Configurações customizadas para Premium
  custom_parameters {
    no_public_ip                                         = false  # Permitir IP público para Serverless
    # storage_account_name removido - deixar Azure decidir automaticamente
    storage_account_sku_name                            = "Standard_LRS"
    virtual_network_id                                  = null    # Sem VNet customizada para simplicidade
    public_subnet_name                                  = null
    private_subnet_name                                 = null
    public_subnet_network_security_group_association_id = null
    private_subnet_network_security_group_association_id = null
  }

  tags = local.final_tags

  depends_on = [azurerm_storage_account.unity_catalog]
}

# ========================
# Key Vault Secrets for Databricks (Always Store)
# ========================

# Store Databricks Workspace URL
resource "azurerm_key_vault_secret" "databricks_workspace_url" {
  name         = "databricks-workspace-url"
  value        = azurerm_databricks_workspace.main.workspace_url
  key_vault_id = var.key_vault_id

  lifecycle {
    ignore_changes = [value]
  }

  # Garantir que Key Vault e workspace estão prontos
  depends_on = [azurerm_databricks_workspace.main]

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "databricks"
    Type        = "workspace-url"
  }
}

# Store Databricks Workspace ID
resource "azurerm_key_vault_secret" "databricks_workspace_id" {
  name         = "databricks-workspace-id"
  value        = azurerm_databricks_workspace.main.workspace_id
  key_vault_id = var.key_vault_id

  lifecycle {
    ignore_changes = [value]
  }

  # Garantir que Key Vault e workspace estão prontos
  depends_on = [azurerm_databricks_workspace.main]

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "databricks"
    Type        = "workspace-id"
  }
}

# Store Unity Catalog Storage Account Name
resource "azurerm_key_vault_secret" "unity_catalog_storage_name" {
  name         = "unity-catalog-storage-name"
  value        = azurerm_storage_account.unity_catalog.name
  key_vault_id = var.key_vault_id

  lifecycle {
    ignore_changes = [value]
  }

  # Garantir que storage account está pronto
  depends_on = [azurerm_storage_account.unity_catalog]

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "unity-catalog"
    Type        = "storage-name"
  }
}

# Store Unity Catalog Storage Account Key
resource "azurerm_key_vault_secret" "unity_catalog_storage_key" {
  name         = "unity-catalog-storage-key"
  value        = azurerm_storage_account.unity_catalog.primary_access_key
  key_vault_id = var.key_vault_id

  lifecycle {
    ignore_changes = [value]
  }

  # Garantir que storage account está pronto
  depends_on = [azurerm_storage_account.unity_catalog]

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "unity-catalog"
    Type        = "storage-key"
  }
}

# ========================
# Unity Catalog Access Connector
# ========================

# Use the Databricks-managed access connector instead of creating a custom one
# The managed connector is created automatically in the databricks managed resource group
data "azurerm_databricks_workspace" "managed_rg" {
  name                = azurerm_databricks_workspace.main.name
  resource_group_name = azurerm_databricks_workspace.main.resource_group_name
}

# Find the managed access connector in the Databricks managed resource group
# Note: This will be available after workspace creation
# data "azurerm_databricks_access_connector" "managed" {
#   name                = "databricks-access-connector"
#   resource_group_name = azurerm_databricks_workspace.main.managed_resource_group_name
# }

# Grant Dino SPN Storage Blob Data Contributor on Unity Catalog storage directly

# ========================
# Role Assignments for Service Principal
# ========================

# ========================
# Role Assignments for Service Principal - COMENTADO
# ========================
# Como vamos usar apenas a SPN Dino, não precisamos de role assignments para a SPN criada

# Grant user admin access to Databricks workspace (temporarily disabled)
# TODO: Enable after confirming user exists in Azure AD
# data "azuread_user" "admin_user" {
#   user_principal_name = var.admin_user_email
# }

# resource "azurerm_role_assignment" "admin_user_databricks" {
#   scope                = azurerm_databricks_workspace.main.id
#   role_definition_name = "Contributor"
#   principal_id         = data.azuread_user.admin_user.object_id
#   principal_type       = "User"
# }

# Grant metastore_admins group Contributor access to Databricks workspace (disabled)
# Uncomment when metastore_admins group is created
# resource "azurerm_role_assignment" "metastore_admins_databricks" {
#   scope                = azurerm_databricks_workspace.main.id
#   role_definition_name = "Contributor"
#   principal_id         = data.azuread_group.metastore_admins.object_id
#   principal_type       = "Group"
# }

# Grant Service Principal Contributor access to Databricks workspace - COMENTADO
# resource "azurerm_role_assignment" "spn_databricks_contributor" {
#   scope                = azurerm_databricks_workspace.main.id
#   role_definition_name = "Contributor"
#   principal_id         = var.service_principal_object_id
#   principal_type       = "ServicePrincipal"
# }

# Grant Service Principal Storage Blob Data Contributor on Unity Catalog storage - COMENTADO
# resource "azurerm_role_assignment" "spn_unity_catalog_storage" {
#   scope                = azurerm_storage_account.unity_catalog.id
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = var.service_principal_object_id
#   principal_type       = "ServicePrincipal"
# }

# Role assignment para Databricks storage removida - Azure gerencia automaticamente

# ========================
# Unity Catalog Configuration (Databricks Resources)
# ========================

# NOTE: Unity Catalog resources are configured via the Databricks provider
# These resources require the Databricks workspace to be fully operational
# For now, we'll document the manual steps needed:

# Manual Unity Catalog Setup Steps:
# 1. Create metastore (via Databricks Account Console or API)
# 2. Assign metastore to workspace
# 3. Create catalog with storage location: abfss://unity-catalog@${azurerm_storage_account.unity_catalog.name}.dfs.core.windows.net/
# 4. Grant ALL PRIVILEGES on catalog to user: brunno.ramos@live.com or metastore_admins group

# Future: Add databricks_metastore, databricks_catalog, and databricks_grants resources
# when workspace is fully provisioned and Unity Catalog is enabled
