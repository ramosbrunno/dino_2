#!/bin/bash

# Script de configuração do Databricks Unity Catalog e Serverless
# Este script configura o ambiente Databricks após o deploy do Terraform

set -e

# Função para log colorido
log_info() {
    echo -e "\033[0;32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[0;33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Verificar variáveis de ambiente necessárias
check_environment() {
    log_info "Verificando variáveis de ambiente..."
    
    required_vars=(
        "DATABRICKS_WORKSPACE_URL"
        "DATABRICKS_ACCESS_TOKEN"
        "UNITY_CATALOG_STORAGE_ROOT"
        "DATABRICKS_WORKSPACE_ID"
        "PROJETO"
        "AMBIENTE"
        "AZURE_REGION"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "Variável de ambiente $var não encontrada!"
            exit 1
        fi
    done
    
    log_info "✅ Todas as variáveis de ambiente estão configuradas"
}

# Função para fazer requisições REST para Databricks
databricks_api() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    local url="${DATABRICKS_WORKSPACE_URL}/api/2.1/${endpoint}"
    
    if [[ -n "$data" ]]; then
        curl -s -X "$method" \
            -H "Authorization: Bearer $DATABRICKS_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url"
    else
        curl -s -X "$method" \
            -H "Authorization: Bearer $DATABRICKS_ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            "$url"
    fi
}

# Criar Unity Catalog Metastore
create_metastore() {
    log_info "🗄️  Criando Unity Catalog Metastore..."
    
    local metastore_name="unity-catalog-$(echo $AZURE_REGION | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"
    local metastore_data=$(cat <<EOF
{
    "name": "$metastore_name",
    "storage_root": "$UNITY_CATALOG_STORAGE_ROOT",
    "region": "$AZURE_REGION"
}
EOF
)
    
    local response=$(databricks_api "POST" "unity-catalog/metastores" "$metastore_data")
    local metastore_id=$(echo "$response" | jq -r '.metastore_id // empty')
    
    if [[ -n "$metastore_id" ]]; then
        log_info "✅ Unity Catalog Metastore criado: $metastore_name"
        echo "$metastore_id" > /tmp/metastore_id
        return 0
    else
        log_error "❌ Erro ao criar Metastore: $response"
        return 1
    fi
}

# Atribuir Metastore ao Workspace
assign_metastore() {
    log_info "🔗 Atribuindo Metastore ao Workspace..."
    
    local metastore_id=$(cat /tmp/metastore_id)
    local assignment_data=$(cat <<EOF
{
    "metastore_id": "$metastore_id",
    "default_catalog_name": "main"
}
EOF
)
    
    local response=$(databricks_api "PUT" "unity-catalog/workspaces/$DATABRICKS_WORKSPACE_ID/metastore" "$assignment_data")
    
    if [[ $(echo "$response" | jq -r '.error_code // empty') == "" ]]; then
        log_info "✅ Metastore atribuído ao workspace com sucesso!"
        return 0
    else
        log_error "❌ Erro ao atribuir Metastore: $response"
        return 1
    fi
}

# Criar Catalog
create_catalog() {
    local catalog_name="${PROJETO}_${AMBIENTE}"
    log_info "📚 Criando Catalog: $catalog_name..."
    
    local catalog_data=$(cat <<EOF
{
    "name": "$catalog_name",
    "comment": "Catalog principal para $PROJETO em $AMBIENTE"
}
EOF
)
    
    local response=$(databricks_api "POST" "unity-catalog/catalogs" "$catalog_data")
    
    if [[ $(echo "$response" | jq -r '.name // empty') == "$catalog_name" ]]; then
        log_info "✅ Catalog criado: $catalog_name"
        echo "$catalog_name" > /tmp/catalog_name
        return 0
    else
        log_error "❌ Erro ao criar Catalog: $response"
        return 1
    fi
}

# Criar Schemas
create_schemas() {
    local catalog_name=$(cat /tmp/catalog_name)
    local schemas=("bronze" "silver" "gold" "workspace")
    
    for schema_name in "${schemas[@]}"; do
        log_info "🗂️  Criando Schema: ${catalog_name}.${schema_name}..."
        
        local schema_data=$(cat <<EOF
{
    "name": "$schema_name",
    "catalog_name": "$catalog_name",
    "comment": "Schema $schema_name para arquitetura medallion"
}
EOF
)
        
        local response=$(databricks_api "POST" "unity-catalog/schemas" "$schema_data")
        
        if [[ $(echo "$response" | jq -r '.name // empty') == "$schema_name" ]]; then
            log_info "✅ Schema criado: ${catalog_name}.${schema_name}"
        else
            log_warn "⚠️  Schema ${catalog_name}.${schema_name} pode já existir ou houve erro: $response"
        fi
    done
}

# Habilitar Serverless Compute
enable_serverless() {
    log_info "⚡ Habilitando Serverless Compute..."
    
    local serverless_config=$(cat <<EOF
{
    "enableServerlessCompute": "true",
    "enableAutomaticClusterUpdate": "true"
}
EOF
)
    
    local response=$(databricks_api "PATCH" "workspace-conf" "$serverless_config")
    log_info "✅ Configuração Serverless aplicada"
}

# Criar SQL Warehouse Serverless
create_sql_warehouse() {
    local warehouse_name="${PROJETO}-${AMBIENTE}-warehouse"
    log_info "🏭 Criando SQL Warehouse Serverless: $warehouse_name..."
    
    local warehouse_data=$(cat <<EOF
{
    "name": "$warehouse_name",
    "cluster_size": "2X-Small",
    "min_num_clusters": 1,
    "max_num_clusters": 1,
    "auto_stop_mins": 10,
    "enable_photon": true,
    "enable_serverless_compute": true,
    "warehouse_type": "PRO",
    "spot_instance_policy": "COST_OPTIMIZED"
}
EOF
)
    
    local response=$(databricks_api "POST" "sql/warehouses" "$warehouse_data")
    local warehouse_id=$(echo "$response" | jq -r '.id // empty')
    
    if [[ -n "$warehouse_id" ]]; then
        log_info "✅ SQL Warehouse Serverless criado: $warehouse_name"
        echo "$warehouse_id" > /tmp/warehouse_id
        return 0
    else
        log_error "❌ Erro ao criar SQL Warehouse: $response"
        return 1
    fi
}

# Função principal
main() {
    log_info "🚀 Iniciando configuração do Databricks Unity Catalog e Serverless..."
    log_info "Projeto: $PROJETO | Ambiente: $AMBIENTE | Região: $AZURE_REGION"
    
    # Verificar ambiente
    check_environment
    
    # Executar configurações
    if create_metastore; then
        log_info "⏳ Aguardando propagação da configuração do Metastore..."
        sleep 30
        
        if assign_metastore; then
            log_info "⏳ Aguardando propagação da atribuição..."
            sleep 30
            
            create_catalog
            create_schemas
        fi
    fi
    
    # Configurar Serverless
    enable_serverless
    create_sql_warehouse
    
    # Resumo
    log_info "🎉 Configuração do Databricks finalizada!"
    log_info "📋 Resumo:"
    log_info "   - Unity Catalog Metastore: Criado"
    log_info "   - Catalog: ${PROJETO}_${AMBIENTE}"
    log_info "   - Schemas: bronze, silver, gold, workspace"
    log_info "   - SQL Warehouse: ${PROJETO}-${AMBIENTE}-warehouse"
    log_info "   - Serverless Compute: Habilitado"
}

# Executar se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
