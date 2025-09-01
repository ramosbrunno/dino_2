# SQL Database Module - Azure SQL Database for Dino SDK Pipeline Logging
# This module creates Azure SQL Database with basic configuration for storing pipeline logs

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

# Generate random password for SQL admin
resource "random_password" "sql_admin_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Generate random suffix for unique naming (4 digits)
resource "random_string" "sql_suffix" {
  length  = 4
  special = false
  upper   = false
  lower   = false
  numeric = true
}

# Get current client config to access subscription_id for unique naming
data "azurerm_client_config" "current" {}

# Local values for resource naming and configuration
locals {
  # Nomenclatura seguindo padrão consistente
  # SQL Server pode manter hífen por ser permitido
  sql_server_name   = "${var.projeto}-${var.ambiente}-sql-${random_string.sql_suffix.result}"
  sql_database_name = "${var.projeto}-${var.ambiente}-db-logs"
  
  # Tags padrão para o módulo SQL Database
  default_tags = {
    Project     = var.projeto
    Environment = var.ambiente
    ManagedBy   = "terraform"
    CreatedBy   = "dino-arc-cli"
    Module      = "sql-database"
    Purpose     = "pipeline-logging"
  }
  
  # Merge das tags padrão com as tags fornecidas pelo usuário
  final_tags = merge(local.default_tags, var.tags)
}

# ========================
# Azure SQL Server
# ========================

resource "azurerm_mssql_server" "main" {
  name                         = local.sql_server_name
  resource_group_name          = var.resource_group_name
  location                     = var.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_username
  administrator_login_password = random_password.sql_admin_password.result
  
  # Security configurations
  public_network_access_enabled = var.enable_public_access
  minimum_tls_version           = "1.2"
  
  tags = local.final_tags
}

# ========================
# Azure SQL Database
# ========================

resource "azurerm_mssql_database" "main" {
  name           = local.sql_database_name
  server_id      = azurerm_mssql_server.main.id
  collation      = "SQL_Latin1_General_CP1_CI_AS"
  license_type   = "LicenseIncluded"
  sku_name       = var.sql_database_sku
  zone_redundant = false

  tags = local.final_tags
}

# ========================
# SQL Server Firewall Rules
# ========================

# Allow Azure services to access SQL Server
resource "azurerm_mssql_firewall_rule" "azure_services" {
  name             = "AllowAzureServices"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "0.0.0.0"
}

# Allow public access (can be configured)
resource "azurerm_mssql_firewall_rule" "public_access" {
  count            = var.enable_public_access ? 1 : 0
  name             = "AllowAllIPs"
  server_id        = azurerm_mssql_server.main.id
  start_ip_address = "0.0.0.0"
  end_ip_address   = "255.255.255.255"
}

# ========================
# Key Vault Secrets for SQL Database
# ========================

# Store SQL Server name
resource "azurerm_key_vault_secret" "sql_server_name" {
  name         = "sql-server-name"
  value        = azurerm_mssql_server.main.name
  key_vault_id = var.key_vault_id

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "sql-database"
    Type        = "server-name"
  }
}

# Store SQL Database name
resource "azurerm_key_vault_secret" "sql_database_name" {
  name         = "sql-database-name"
  value        = azurerm_mssql_database.main.name
  key_vault_id = var.key_vault_id

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "sql-database"
    Type        = "database-name"
  }
}

# Store SQL Connection String
resource "azurerm_key_vault_secret" "sql_connection_string" {
  name         = "sql-connection-string"
  value        = "Server=tcp:${azurerm_mssql_server.main.fully_qualified_domain_name},1433;Initial Catalog=${azurerm_mssql_database.main.name};Persist Security Info=False;User ID=${var.sql_admin_username};Password=${random_password.sql_admin_password.result};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
  key_vault_id = var.key_vault_id

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "sql-database"
    Type        = "connection-string"
  }
}

# Store SQL Admin Password
resource "azurerm_key_vault_secret" "sql_admin_password" {
  name         = "sql-admin-password"
  value        = random_password.sql_admin_password.result
  key_vault_id = var.key_vault_id

  tags = {
    Project     = var.projeto
    Environment = var.ambiente
    Resource    = "sql-database"
    Type        = "admin-password"
  }
}
