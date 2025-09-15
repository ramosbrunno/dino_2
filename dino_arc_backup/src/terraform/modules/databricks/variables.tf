# Databricks Module Variables - Premium Configuration

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

variable "service_principal_object_id" {
  description = "Object ID do Service Principal para configurar permissões"
  type        = string
}

variable "tags" {
  description = "Tags adicionais para aplicar aos recursos"
  type        = map(string)
  default     = {}
}
