# Variables for Azure Resources Configuration - Modular Architecture

# ========================
# Azure Authentication Variables
# ========================

variable "subscription_id" {
  description = "Azure Subscription ID onde os recursos serão criados"
  type        = string
  sensitive   = true
  
  validation {
    condition     = can(regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", var.subscription_id))
    error_message = "Subscription ID deve estar no formato UUID válido."
  }
}

# ========================
# Core Project Variables
# ========================

variable "projeto" {
  description = "Nome do projeto (será usado como base para todos os recursos)"
  type        = string
  default     = "data-master"
  
  validation {
    condition     = length(var.projeto) >= 3 && length(var.projeto) <= 20 && can(regex("^[a-z0-9-]+$", var.projeto))
    error_message = "O nome do projeto deve ter entre 3 e 20 caracteres, apenas letras minúsculas, números e hífens."
  }
}

variable "ambiente" {
  description = "Ambiente do projeto (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.ambiente)
    error_message = "Ambiente deve ser 'dev', 'staging' ou 'prod'."
  }
}

variable "location" {
  description = "Localização dos recursos no Azure"
  type        = string
  default     = "East US"
  
  validation {
    condition = contains([
      "East US", "East US 2", "West US", "West US 2", "West US 3",
      "Central US", "North Central US", "South Central US", "West Central US",
      "Brazil South", "Canada Central", "Canada East",
      "North Europe", "West Europe", "UK South", "UK West",
      "France Central", "Germany West Central", "Switzerland North",  
      "Norway East", "Sweden Central"
    ], var.location)
    error_message = "A localização deve ser uma região válida do Azure."
  }
}

variable "tags" {
  description = "Tags adicionais para aplicar aos recursos (serão mescladas com tags padrão)"
  type        = map(string)
  default     = {}
}

# ========================
# Module Control Variables
# ========================

variable "enable_databricks" {
  description = "Se deve criar o Azure Databricks workspace"
  type        = bool
  default     = false
}

# ========================
# Databricks Module Variables
# ========================

variable "databricks_sku" {
  description = "SKU do Azure Databricks (standard, premium, trial)"
  type        = string
  default     = "standard"
  
  validation {
    condition     = contains(["standard", "premium", "trial"], var.databricks_sku)
    error_message = "SKU deve ser 'standard', 'premium' ou 'trial'."
  }
}

variable "databricks_public_network_access" {
  description = "Se o acesso à rede pública deve ser habilitado no Databricks"
  type        = bool
  default     = true
}

variable "databricks_no_public_ip" {
  description = "Se deve usar Secure Cluster Connectivity (sem IP público)"
  type        = bool
  default     = false
}

variable "databricks_store_secrets" {
  description = "Se deve armazenar informações do Databricks no Key Vault"
  type        = bool
  default     = true
}
