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

  # Databricks-specific configurations
  databricks_sku               = var.databricks_sku
  public_network_access_enabled = var.databricks_public_network_access
  no_public_ip                 = var.databricks_no_public_ip
  store_secrets_in_keyvault    = var.databricks_store_secrets

  depends_on = [module.foundation]
}
