# 🦕 DINO SDK v1.2.0 - Data Ingestion SDK for Databricks

SDK simplificado para automação de ingestão de dados no Databricks com Unity Catalog.

## 🎯 **Alterações da versão 1.2.0**

### ❌ **Funcionalidades Removidas:**
- Criação automática de Secret Scope
- Gerenciamento de Azure Key Vault
- Funcionalidades relacionadas ao `dino_keyvault` e `dino_scope_manager`

### ✅ **Nova Funcionalidade:**
- Criação simplificada de Schema no Unity Catalog
- Comando `dino-config setup` com parâmetros simplificados

## 🔧 **Configuração Manual Obrigatória**

**IMPORTANTE:** Antes de usar o DINO SDK, você deve criar manualmente o Secret Scope seguindo a documentação oficial da Microsoft:

📖 **Documentação:** https://learn.microsoft.com/en-us/azure/databricks/security/secrets/

### 📋 **Passos para criar Secret Scope:**

1. **Acesse o Databricks Workspace**
2. **Vá para Settings > Developer > Secret Scopes**
3. **Clique em "Create Secret Scope"**
4. **Configure:**
   - **Scope Name:** `{seu-projeto}-scope`
   - **Backend Type:** Azure Key Vault
   - **DNS Name:** `https://{seu-keyvault}.vault.azure.net/`
   - **Resource ID:** `/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.KeyVault/vaults/{keyvault-name}`

## 🚀 **Uso do DINO SDK v1.2.0**

### 1. **Instalação**
```bash
pip install dino-sdk==1.2.0
```

### 2. **Configuração Inicial**
```bash
dino-config setup \
  --project-name bronze \
  --storage-name mystorageaccount \
  --catalog-name vendas \
  --schema-name bronze
```

### 3. **Parâmetros do setup:**
- `--project-name`: Nome do projeto
- `--storage-name`: Nome do Storage Account para External Location
- `--catalog-name`: Nome do catálogo Unity Catalog
- `--schema-name`: Nome do schema destino (será criado se não existir)

### 4. **O que o setup faz:**
1. ✅ Verifica se o catálogo existe
2. ✅ Obtém external location do catálogo
3. ✅ Cria o schema no catálogo especificado usando a sintaxe:
   ```sql
   CREATE SCHEMA {catalogo}.{schema}
   MANAGED LOCATION '{external_location}/{catalogo}/{schema}/'
   ```
4. ✅ Gera arquivo de configuração YAML

### 5. **Exemplo de uso programático:**
```python
from src import create_unity_catalog_schema

# Criar schema no Unity Catalog
result = create_unity_catalog_schema(
    catalog_name="vendas",
    schema_name="bronze"
)
```

## 🔍 **Validação da Configuração**
```bash
dino-config validate --catalog-name vendas --schema-name bronze
```

## 📊 **Visualizar Configuração Atual**
```bash
dino-config show
```

## 🛠️ **Ingestão de Dados (inalterada)**
```bash
dino-ingest \
  --target-schema vendas.bronze \
  --table-name vendas_raw \
  --file-path /Volumes/vendas/default/raw/vendas.csv
```

## 📂 **Estrutura do Projeto**
```
dino_sdk/
├── src/
│   ├── __init__.py              # Funções principais
│   ├── cli.py                   # CLI de ingestão
│   ├── config_cli.py            # CLI de configuração
│   ├── config_manager.py        # Gerenciador de config
│   ├── programmatic_config.py   # Config programática
│   ├── ingestion_engine.py      # Engine de ingestão
│   ├── workflow_manager.py      # Gerenciador de workflows
│   ├── genie_assistant.py       # Integração com Genie
│   └── job_manager.py           # Gerenciador de jobs
├── tests/                       # Testes
└── setup.py                     # Configuração do pacote
```

## 🔄 **Migração da v1.1.6 para v1.2.0**

### **Funções Removidas:**
- `dino_create_keyvault_scope()` ❌
- `DinoKeyVaultConfig` ❌  
- `DinoSecretScopeManager` ❌

### **Novas Funções:**
- `create_unity_catalog_schema()` ✅

### **Comandos CLI Alterados:**
```bash
# ANTES (v1.1.6)
dino-config setup \
  --project-name bronze \
  --keyvault-name meu-keyvault \
  --catalog-name vendas \
  --schema-name bronze \
  --project-spn-id abc-123

# AGORA (v1.2.0)
dino-config setup \
  --project-name bronze \
  --storage-name mystorageaccount \
  --catalog-name vendas \
  --schema-name bronze
```

## 📞 **Suporte**

- **Repository:** https://github.com/ramosbrunno/dino_2
- **Issues:** https://github.com/ramosbrunno/dino_2/issues
- **Version:** 1.2.0
- **Author:** Data Master Team

---

**🎉 O DINO SDK v1.2.0 está focado na simplicidade e eficiência para criação de schemas no Unity Catalog!**
