# Main Terraform Configuration - Complete Infrastructure
# This file orchestrates the deployment of all modules

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
    # Disable Network Watcher automatic creation
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  
  # Disable automatic Network Watcher creation
  skip_provider_registration = false
}

# Configure the Azure AD Provider
provider "azuread" {}

# ========================
# Foundation Module (Always Created)
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
# Databricks Module (Always Created)
# ========================
# Creates Azure Databricks workspace with Premium SKU and Unity Catalog

module "databricks" {
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
  public_network_access_enabled = var.databricks_public_network_access
  no_public_ip                 = var.databricks_no_public_ip
  store_secrets_in_keyvault    = var.databricks_store_secrets

  depends_on = [module.foundation]
}
