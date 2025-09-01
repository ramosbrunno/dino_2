# SQL Database Module Variables

variable "projeto" {
  description = "Nome do projeto (será usado como base para nomenclatura dos recursos)"
  type        = string
}

variable "ambiente" {
  description = "Ambiente do projeto (dev, staging, prod)"
  type        = string
}

variable "location" {
  description = "Localização dos recursos no Azure"
  type        = string
}

variable "resource_group_name" {
  description = "Nome do Resource Group onde criar os recursos"
  type        = string
}

variable "key_vault_id" {
  description = "ID do Key Vault para armazenar secrets"
  type        = string
}

variable "tags" {
  description = "Tags adicionais para aplicar aos recursos"
  type        = map(string)
  default     = {}
}

# Optional SQL Database configurations
variable "sql_admin_username" {
  description = "Username do administrador SQL"
  type        = string
  default     = "sqladmin"
}

variable "sql_database_sku" {
  description = "SKU do SQL Database (Basic, S1, S2, P1, etc.)"
  type        = string
  default     = "Basic"
}

variable "enable_public_access" {
  description = "Habilitar acesso público ao SQL Server"
  type        = bool
  default     = true
}
