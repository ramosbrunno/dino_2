# Foundation Module Variables

variable "projeto" {
  description = "Nome do projeto (será usado como base para todos os recursos)"
  type        = string
  
  validation {
    condition     = length(var.projeto) >= 3 && length(var.projeto) <= 20 && can(regex("^[a-z0-9-]+$", var.projeto))
    error_message = "O nome do projeto deve ter entre 3 e 20 caracteres, apenas letras minúsculas, números e hífens."
  }
}

variable "ambiente" {
  description = "Ambiente do projeto (dev, staging, prod)"
  type        = string
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.ambiente)
    error_message = "Ambiente deve ser 'dev', 'staging' ou 'prod'."
  }
}

variable "location" {
  description = "Localização dos recursos no Azure"
  type        = string
  
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
