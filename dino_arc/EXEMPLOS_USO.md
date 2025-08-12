# 🚀 Exemplos de Uso do Dino ARC CLI

Este arquivo contém exemplos práticos de como usar o **Dino ARC CLI** após a instalação.

## 📋 Pré-requisitos

Antes de usar os comandos, certifique-se de ter:

1. **Service Principal criado no Azure** com as seguintes informações:
   - `CLIENT_ID` (Application ID)
   - `CLIENT_SECRET` (Secret criado)
   - `TENANT_ID` (Directory ID)
   - `SUBSCRIPTION_ID` (Subscription onde recursos serão criados)

2. **Permissões necessárias** para o Service Principal:
   - Contributor no Subscription ou Resource Group
   - User Access Administrator (para Unity Catalog)

## 🛠️ Instalação

```bash
# Clonar repositório
git clone https://github.com/ramosbrunno/dino_2.git
cd dino_2/dino_arc

# Instalar automaticamente (Windows)
install.bat

# Instalar automaticamente (Linux/Mac)
chmod +x install.sh
./install.sh

# Verificar instalação
dino-arc --help
```

## 🎯 Exemplos Práticos

> **💡 Dica**: O comando `init` é executado automaticamente antes de `plan`, `apply` e `destroy`. Você não precisa executá-lo manualmente, a menos que queira apenas inicializar o Terraform sem fazer outras operações.

### 1. Projeto de Analytics Completo

```bash
# Criar infraestrutura completa (init executado automaticamente)
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action apply \
  --projeto "analytics-corp" \
  --ambiente "dev" \
  --location "East US"

# Visualizar plano antes de aplicar (opcional)
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --subscription-id "11111111-2222-3333-4444-555555555555" \
  --action plan \
  --projeto "analytics-corp" \
  --ambiente "dev" \
  --location "East US"
```

### 2. Ambiente de Produção

```bash
# Criar ambiente de produção
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "data-platform" \
  --ambiente "prod" \
  --location "West Europe"
```

### 3. Múltiplos Ambientes

```bash
# Desenvolvimento
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "data-lake" \
  --ambiente "dev" \
  --location "East US"

# Staging
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "data-lake" \
  --ambiente "staging" \
  --location "East US"

# Produção
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action apply \
  --projeto "data-lake" \
  --ambiente "prod" \
  --location "East US"
```

### 4. Limpeza de Recursos

```bash
# Remover ambiente de desenvolvimento
dino-arc \
  --client-id "12345678-1234-1234-1234-123456789012" \
  --client-secret "sua-client-secret-aqui" \
  --tenant_id "87654321-4321-4321-4321-210987654321" \
  --action destroy \
  --projeto "analytics-corp" \
  --ambiente "dev"

# Remover todos os ambientes (cuidado!)
for ambiente in dev staging prod; do
  dino-arc \
    --client-id "12345678-1234-1234-1234-123456789012" \
    --client-secret "sua-client-secret-aqui" \
    --tenant_id "87654321-4321-4321-4321-210987654321" \
    --action destroy \
    --projeto "data-platform" \
    --ambiente "$ambiente"
done
```

## 📊 Recursos Criados Automaticamente

Cada execução `--action apply` cria:

### 🏗️ Foundation Infrastructure
- **Resource Group**: `rg-{projeto}-{ambiente}`
- **Storage Account**: `sa{projeto}{ambiente}001` (ADLS Gen2)
- **Key Vault**: `kv-{projeto}-{ambiente}`
- **Storage Containers**: raw, processed, curated

### 🧮 Databricks Premium
- **Workspace**: `databricks-{projeto}-{ambiente}`
- **SKU**: Premium (Unity Catalog + Serverless)
- **Managed Resource Group**: Criado automaticamente
- **Unity Catalog**: Configurado automaticamente
- **Serverless SQL**: Habilitado
- **Serverless Compute**: Configurado

### 🔐 Configurações de Segurança
- Service Principal com permissões adequadas
- Key Vault com políticas de acesso
- Storage com autenticação Azure AD
- Unity Catalog com governance

## 🎛️ Variáveis de Ambiente (Opcional)

Para evitar repetir credenciais:

```bash
# Windows (cmd)
set AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
set AZURE_CLIENT_SECRET=sua-client-secret-aqui
set AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
set AZURE_SUBSCRIPTION_ID=11111111-2222-3333-4444-555555555555

# Linux/Mac (bash)
export AZURE_CLIENT_ID="12345678-1234-1234-1234-123456789012"
export AZURE_CLIENT_SECRET="sua-client-secret-aqui"
export AZURE_TENANT_ID="87654321-4321-4321-4321-210987654321"
export AZURE_SUBSCRIPTION_ID="11111111-2222-3333-4444-555555555555"

# Usar sem repetir credenciais
dino-arc --action apply --projeto "analytics" --ambiente "dev"
```

## 🐛 Troubleshooting

### Problema: "dino-arc command not found"
```bash
# Verificar instalação
pip list | grep dino-arc

# Reinstalar se necessário
cd dino_arc
pip install -e . --force-reinstall
```

### Problema: "Authentication failed"
```bash
# Verificar credenciais
dino-arc --action init --projeto "test" --client-id "..." --client-secret "..." --tenant_id "..."

# Verificar permissões do Service Principal no Azure Portal
```

### Problema: "Terraform not found"
```bash
# Instalar Terraform
# Windows: https://www.terraform.io/downloads.html
# Linux: sudo apt-get install terraform
# Mac: brew install terraform
```

## 📚 Próximos Passos

Após a criação bem-sucedida:

1. **Acesse o Databricks Workspace** via Azure Portal
2. **Configure Unity Catalog** (já configurado automaticamente)
3. **Crie seus primeiros clusters Serverless**
4. **Configure notebooks e jobs**
5. **Explore os dados no Storage Account criado**

## 🔗 Links Úteis

- [Documentação Terraform Azure](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Databricks Documentation](https://docs.microsoft.com/en-us/azure/databricks/)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Service Principal Setup](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
