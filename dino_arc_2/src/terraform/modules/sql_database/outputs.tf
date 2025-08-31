# SQL Database Module Outputs

output "sql_server_name" {
  description = "Nome do SQL Server criado"
  value       = azurerm_mssql_server.main.name
}

output "sql_server_fqdn" {
  description = "FQDN do SQL Server"
  value       = azurerm_mssql_server.main.fully_qualified_domain_name
}

output "sql_database_name" {
  description = "Nome do SQL Database criado"
  value       = azurerm_mssql_database.main.name
}

output "sql_database_id" {
  description = "ID do SQL Database"
  value       = azurerm_mssql_database.main.id
}

output "sql_server_id" {
  description = "ID do SQL Server"
  value       = azurerm_mssql_server.main.id
}

output "sql_admin_username" {
  description = "Username do administrador SQL"
  value       = var.sql_admin_username
}

# Note: Password is stored in Key Vault for security
output "sql_connection_info" {
  description = "Informações de conexão SQL (password no Key Vault)"
  value = {
    server_name   = azurerm_mssql_server.main.name
    server_fqdn   = azurerm_mssql_server.main.fully_qualified_domain_name
    database_name = azurerm_mssql_database.main.name
    admin_user    = var.sql_admin_username
    note          = "Password and connection string stored in Key Vault"
  }
}
