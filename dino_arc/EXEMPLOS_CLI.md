# Exemplos de Uso - Dino ARC CLI

Este documento contém exemplos práticos de como usar a CLI do Dino ARC para criar infraestrutura completa no Azure com Databricks Premium, Unity Catalog e Serverless.

## 🚀 Deploy Completo em Uma Única Execução

A partir da versão atual, o **Dino ARC CLI** implanta automaticamente **toda a infraestrutura** e **configura o Databricks** em uma única execução, incluindo:

- ✅ **Foundation**: Resource Group + Key Vault + Service Principal
- ✅ **Databricks Premium**: Workspace com SKU Premium
- ✅ **Unity Catalog**: Metastore + Catalog + Schemas (bronze, silver, gold, workspace)
- ✅ **Serverless Compute**: Habilitado para todo o workspace
- ✅ **SQL Warehouse Serverless**: Criado e configurado automaticamente

---

## 📋 Parâmetros da CLI

### Parâmetros Obrigatórios

```bash
--client-id         # Azure Client ID do Service Principal
--client-secret     # Azure Client Secret do Service Principal  
--tenant_id         # Azure Tenant ID
--action           # Ação: init, plan, apply, destroy
--projeto          # Nome do projeto (base para todos os recursos)
```

### Parâmetros Opcionais

```bash
--ambiente         # Ambiente: dev, staging, prod (padrão: dev)
--location         # Região do Azure (padrão: East US)
```

---

## 🛠️ Exemplos Práticos

### 1. Inicializar Terraform (Primeira Vez)

```bash
python cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action init \
  --projeto "data-platform"
```

### 2. Visualizar Plano de Implantação

```bash
python cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action plan \
  --projeto "data-platform" \
  --ambiente "dev" \
  --location "East US"
```

### 3. 🎯 Deploy Completo (Recomendado)

```bash
python cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "data-platform" \
  --ambiente "prod" \
  --location "East US"
```

**O que acontece automaticamente:**
1. ✅ Terraform aplica toda a infraestrutura
2. ⏳ Aguarda 60 segundos para recursos ficarem prontos
3. 🔧 Configura Unity Catalog automaticamente
4. 📚 Cria Catalog: `data-platform_prod`
5. 🗂️ Cria Schemas: `bronze`, `silver`, `gold`, `workspace`
6. ⚡ Habilita Serverless Compute
7. 🏭 Cria SQL Warehouse: `data-platform-prod-warehouse`
8. 🎊 Ambiente pronto para uso!

### 4. Destruir Infraestrutura

```bash
python cli.py \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action destroy \
  --projeto "data-platform" \
  --ambiente "dev"
```

---

## 🏗️ Recursos Criados Automaticamente

### Foundation (Sempre Criado)
```
📦 Resource Group: data-platform-dev-rsg
🔐 Key Vault: data-platform-dev-akv-[random]
👤 Service Principal: data-platform-dev-spn
```

### Databricks Premium (Sempre Criado)
```
🧮 Workspace: data-platform-dev-dbw-[random]
📊 DBFS Storage: dataplatformdevdbwsa[random]
🗄️ Unity Catalog Storage: dataplatformdevucsa[random]
```

### Unity Catalog (Configurado Automaticamente)
```
🗄️ Metastore: unity-catalog-east-us
📚 Catalog: data-platform_dev
🗂️ Schemas:
   - bronze (dados brutos)
   - silver (dados processados)  
   - gold (dados refinados)
   - workspace (dados de workspace)
```

### Serverless (Habilitado Automaticamente)
```
⚡ Serverless Compute: Habilitado
🏭 SQL Warehouse: data-platform-dev-warehouse
   - Tamanho: 2X-Small
   - Auto-stop: 10 minutos
   - Photon: Habilitado
   - Spot Instances: Otimização de custos
```

---

## 📊 Saída de Exemplo

### Deploy Bem-Sucedido
```bash
🚀 Criando infraestrutura completa para projeto 'data-platform' no ambiente 'prod' em 'East US'...
📦 Resource Group: data-platform-prod-rsg
🔐 Key Vault: data-platform-prod-akv-abc123
👤 Service Principal: data-platform-prod-spn
🧮 Databricks Premium: data-platform-prod-dbw-abc123
📊 Unity Catalog Storage: dataplatformprodsa123

✅ Infraestrutura completa criada com sucesso!
📋 Componentes implantados:
   🏛️  Foundation (Resource Group + Key Vault + Service Principal)
   🧮 Databricks Premium (Unity Catalog + Serverless)

⏳ Aguardando recursos ficarem prontos para configuração...

🔧 Configurando Databricks Unity Catalog e Serverless...
📋 Obtendo outputs do Terraform...
✅ Conectando ao Databricks: https://adb-1234567890123456.78.azuredatabricks.net

🗄️  Criando Unity Catalog Metastore...
✅ Unity Catalog Metastore criado: unity-catalog-east-us

🔗 Atribuindo Metastore ao Workspace...
✅ Metastore atribuído ao workspace com sucesso!

📚 Criando Catalog: data-platform_prod...
✅ Catalog criado: data-platform_prod

🗂️  Criando Schema: data-platform_prod.bronze...
✅ Schema criado: data-platform_prod.bronze
🗂️  Criando Schema: data-platform_prod.silver...
✅ Schema criado: data-platform_prod.silver
🗂️  Criando Schema: data-platform_prod.gold...
✅ Schema criado: data-platform_prod.gold
🗂️  Criando Schema: data-platform_prod.workspace...
✅ Schema criado: data-platform_prod.workspace

⚡ Habilitando Serverless Compute...
✅ Serverless Compute habilitado!

🏭 Criando SQL Warehouse Serverless: data-platform-prod-warehouse...
✅ SQL Warehouse Serverless criado: data-platform-prod-warehouse

🎉 Configuração do Databricks finalizada com sucesso!
📋 Recursos criados:
   🗄️  Metastore: unity-catalog-east-us
   📚 Catalog: data-platform_prod
   🗂️  Schemas: 4 criados (bronze, silver, gold, workspace)
   🏭 SQL Warehouse: data-platform-prod-warehouse
   ⚡ Serverless Compute: Habilitado

🎊 Deploy completo finalizado!
🚀 Seu ambiente Databricks Premium está pronto para uso:
   📊 Unity Catalog configurado com arquitetura medallion
   ⚡ Serverless Compute habilitado
   🏭 SQL Warehouse Serverless criado
   📚 Catalog: data-platform_prod
   🗂️  Schemas: bronze, silver, gold, workspace
```

---

## 🔧 Configuração Manual (Se Necessário)

Caso a configuração automática do Databricks falhe, você pode executar manualmente os scripts em `databricks_config/`:

### Python (Recomendado)
```bash
pip install requests

export DATABRICKS_WORKSPACE_URL="https://adb-xxx.azuredatabricks.net"
export DATABRICKS_ACCESS_TOKEN="dapi..."
export UNITY_CATALOG_STORAGE_ROOT="abfss://unity-catalog@storage.dfs.core.windows.net/"
export DATABRICKS_WORKSPACE_ID="1234567890123456"
export PROJETO="data-platform"
export AMBIENTE="prod"
export AZURE_REGION="East US"

python src/databricks_config/unity_catalog_setup.py
```

### Shell (Linux/MacOS)
```bash
chmod +x src/databricks_config/setup_databricks.sh
./src/databricks_config/setup_databricks.sh
```

### Batch (Windows)
```cmd
src\databricks_config\setup_databricks.bat
```

---

## 🚨 Troubleshooting

### Erro: "Unity Catalog Storage não encontrado"
- Verificar se o Terraform foi executado com sucesso
- Verificar se os outputs estão disponíveis: `terraform output`

### Erro: "Token de acesso inválido"
- O token é gerado automaticamente pelo Terraform
- Verificar se o workspace foi criado corretamente

### Erro: "Metastore já existe"
- Normal se executar novamente
- O script tentará usar o metastore existente

---

## 💡 Dicas

1. **Use ambientes separados**: `dev`, `staging`, `prod`
2. **Mantenha tokens seguros**: Nunca commitar no código
3. **Teste primeiro**: Use `--action plan` antes de `apply`
4. **Monitor custos**: Serverless Compute tem auto-stop de 10min
5. **Backup regular**: Configure backup do Key Vault

---

## 🔗 Links Úteis

- [Documentação do Azure Databricks](https://docs.microsoft.com/azure/databricks/)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/)
- [Serverless Compute](https://docs.databricks.com/compute/serverless.html)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)