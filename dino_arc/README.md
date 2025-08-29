# DINO ARC

Ferramenta CLI para criação automatizada de infraestrutura Azure com Databricks Premium, Unity Catalog e Serverless Computing.

## Instalação

### 1. Criar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv dino_env

# Ativar ambiente virtual
# No Windows:
dino_env\Scripts\activate

# No Linux/Mac:
source dino_env/bin/activate
```

### 2. Instalar DINO ARC
```bash
pip install dist/dino_arc-2.0.0-py3-none-any.whl
```

### 3. Verificar Instalação
```bash
dino_arc --help
```

## Uso

### Criar Infraestrutura
```bash
dino_arc \
  --client-id "your-client-id" \
  --client-secret "your-client-secret" \
  --tenant_id "your-tenant-id" \
  --subscription-id "your-subscription-id" \
  --action apply \
  --projeto myapp \
  --ambiente dev
```

### Destruir Infraestrutura
```bash
dino_arc \
  --client-id "your-client-id" \
  --client-secret "your-client-secret" \
  --tenant_id "your-tenant-id" \
  --subscription-id "your-subscription-id" \
  --action destroy \
  --projeto myapp \
  --ambiente dev
```

### Ajuda
```bash
dino_arc --help
```

## O Que É Criado

- Resource Group do Azure
- Azure Key Vault
- Service Principal
- Azure SQL Database
- Databricks Premium Workspace
- Unity Catalog com Metastore
- Serverless Computing (habilitado automaticamente)

## Requisitos

- Python 3.8+
- Azure CLI configurado
- Credenciais de Service Principal do Azure

## Gerenciamento do Ambiente

### Desativar Ambiente Virtual
```bash
deactivate
```

### Reativar Ambiente Virtual (sessões futuras)
```bash
# No Windows:
dino_env\Scripts\activate

# No Linux/Mac:
source dino_env/bin/activate
```
