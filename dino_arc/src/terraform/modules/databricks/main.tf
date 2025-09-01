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

# Generate random string for Unity Catalog storage naming
resource "random_string" "unique_suffix" {
  length  = 4
  special = false
  upper   = false
  lower   = false
  numeric = true
}

# Get current client config
data "azurerm_client_config" "current" {}

# Local values for resource naming and configuration
locals {
  # Nomenclatura descritiva: projeto-ambiente-tipo-funcionalidade
  databricks_workspace_name = "${var.projeto}-${var.ambiente}-dbw"
  
  # Apenas Unity Catalog storage (DBFS será criado automaticamente pelo Azure)
  projeto_clean = replace(var.projeto, "-", "")
  unity_catalog_storage     = "${local.projeto_clean}${var.ambiente}sauc${random_string.unique_suffix.result}"
  
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
# Storage Account for Unity Catalog (apenas)
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
  
  # Configurações customizadas para Premium - SEM storage account customizado
  custom_parameters {
    no_public_ip                                         = false  # Permitir IP público para Serverless
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
# Configuração Pós-Criação
# ========================

# NOTA: As configurações do Unity Catalog, serverless e usuários administradores
# serão feitas em uma segunda fase usando o provider databricks após a criação
# do workspace, para evitar dependências circulares.
#
# Configurações pendentes:
# 1. Unity Catalog metastore: ${var.projeto}-metastore
# 2. Serverless computing habilitado
# 3. Usuários admin: brunno.ramos_live.com#EXT#@brunnoramoslive.onmicrosoft.com, brunno.ramos@brunnoramoslive.onmicrosoft.com

# ========================
# Key Vault Secrets for Databricks (Always Store)
# ========================

# Store Databricks Workspace URL
resource "azurerm_key_vault_secret" "databricks_workspace_url" {
  name         = "databricks-workspace-url"
  value        = azurerm_databricks_workspace.main.workspace_url
  key_vault_id = var.key_vault_id

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

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "unity-catalog"
    Type        = "storage-key"
  }
}

# ========================
# Role Assignments for Service Principal
# ========================

# Grant Service Principal Contributor access to Databricks workspace
resource "azurerm_role_assignment" "spn_databricks_contributor" {
  scope                = azurerm_databricks_workspace.main.id
  role_definition_name = "Contributor"
  principal_id         = var.service_principal_object_id
  principal_type       = "ServicePrincipal"
}

# Grant Service Principal Storage Blob Data Contributor on Unity Catalog storage
resource "azurerm_role_assignment" "spn_unity_catalog_storage" {
  scope                = azurerm_storage_account.unity_catalog.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.service_principal_object_id
  principal_type       = "ServicePrincipal"
}
