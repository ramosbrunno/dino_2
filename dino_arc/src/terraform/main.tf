# Main Terraform Configuration - Modular Architecture
# This file orchestrates the deployment of multiple modules

terraform {
  required_version = ">= 1.0"
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

# Configure the Azure Provider
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
  
  # Usar subscription_id se fornecida via variável
  subscription_id = var.subscription_id
  
  # Configuração de timeouts para evitar problemas de estado
  skip_provider_registration = false
}

# Configure the Azure AD Provider
provider "azuread" {}

# ========================
# Foundation Module
# ========================
# Creates Resource Group, Service Principal, and Key Vault

module "foundation" {
  source = "./modules/foundation"

  # Pass variables to the foundation module
  projeto   = var.projeto
  ambiente  = var.ambiente
  location  = var.location
  tags      = var.tags
}

# ========================
# Databricks Module (Optional)
# ========================
# Creates Azure Databricks workspace when enabled

module "databricks" {
  count  = var.enable_databricks ? 1 : 0
  source = "./modules/databricks"

  # Pass variables to the databricks module
  projeto   = var.projeto
  ambiente  = var.ambiente
  location  = var.location
  tags      = var.tags

  # Dependencies from foundation module
  resource_group_name           = module.foundation.resource_group_name
  key_vault_id                 = module.foundation.key_vault_id
  service_principal_object_id   = module.foundation.service_principal_object_id

  depends_on = [module.foundation]
}

# ========================
# SQL Database Module (for Dino SDK Pipeline Logging)
# ========================
# Creates Azure SQL Database for storing Dino SDK pipeline logs

module "sql_database" {
  count  = var.enable_sql_database ? 1 : 0
  source = "./modules/sql_database"

  # Basic parameters
  projeto  = var.projeto
  ambiente = var.ambiente
  location = var.location

  # Dependencies from foundation module
  resource_group_name = module.foundation.resource_group_name
  key_vault_id       = module.foundation.key_vault_id

  # Tags
  tags = var.tags

  depends_on = [module.foundation]
}
