# 🔐 DINO Secret Scope Setup - Guia Rápido

## 🎯 Próximos Passos para Resolver os Secrets

### ✅ **Sucesso Atual**
- ✅ Detecção de ambiente Databricks funcionando
- ✅ Extração de token admin funcionando  
- ✅ Workspace URL identificado corretamente
- ❌ Secrets não encontrados (esperado - scope não configurada)

### 🔧 **Passo 1: Verificar Scopes Existentes**
```python
from src import dino_list_scopes

# Ver todas as secret scopes
scopes = dino_list_scopes()
```

### 🔧 **Passo 2A: Criar Scope com Azure Key Vault (Recomendado)**
```python
from src import dino_create_keyvault_scope

# Substitua pelos seus valores reais do Azure
subscription_id = "sua-subscription-id-aqui"
resource_group = "seu-resource-group-aqui"  
tenant_id = "seu-tenant-id-aqui"

# Criar scope apontando para Key Vault
success = dino_create_keyvault_scope(
    subscription_id=subscription_id,
    resource_group=resource_group, 
    tenant_id=tenant_id
)
```

### 🔧 **Passo 2B: Criar Scope Databricks (Alternativa)**
```python
from src import dino_create_databricks_scope

# Criar scope usando storage interno do Databricks
success = dino_create_databricks_scope()
```

### 🔧 **Passo 3: Verificar Criação**
```python
from src import dino_check_scope

# Verificar se a scope foi criada
exists = dino_check_scope()
```

### 🔧 **Passo 4: Testar Novamente**
```python
from src import dino_quick_setup

# Testar depois da criação da scope
config = dino_quick_setup(force=True)
```

## 📋 **Informações Necessárias do Azure**

Para encontrar as informações necessárias:

### 1. **Subscription ID**
- No portal Azure → Subscriptions → copiar ID

### 2. **Resource Group** 
- No portal Azure → Resource groups → nome onde está o Key Vault

### 3. **Tenant ID**
- No portal Azure → Azure Active Directory → Properties → Tenant ID

### 4. **Key Vault Name**
- Já configurado: `dino-keyvault-dev`

## 🔐 **Permissões Necessárias**

### No Azure Key Vault:
- **Service Principal**: Permissões `Get`, `List` para secrets
- **Usuários/Grupos**: Permissões adequadas para acessar Key Vault

### No Databricks:
- **Workspace Admin**: Para criar secret scopes
- **Users Group**: Permissão `MANAGE` na scope (será configurada automaticamente)

## 🎯 **Fluxo Completo Recomendado**

```python
# 1. Verificar ambiente atual
from src import dino_simple_test
result = dino_simple_test()

# 2. Listar scopes existentes  
from src import dino_list_scopes
scopes = dino_list_scopes()

# 3. Criar scope (substitua pelos valores reais)
from src import dino_create_keyvault_scope
success = dino_create_keyvault_scope(
    subscription_id="12345678-1234-1234-1234-123456789012",
    resource_group="dino-resources",
    tenant_id="87654321-4321-4321-4321-210987654321"
)

# 4. Teste final
from src import dino_quick_setup
config = dino_quick_setup(force=True)
```

## 💡 **Troubleshooting**

### Se der erro de permissão:
1. Verificar se você é admin do workspace Databricks
2. Verificar permissões no Azure Key Vault
3. Verificar se o Service Principal tem acesso

### Se der erro de resource ID:
1. Verificar se Key Vault existe no resource group
2. Verificar subscription ID e tenant ID
3. Verificar se resource group está correto

### Se scope já existir:
- Usar `dino_list_scopes()` para ver scopes existentes
- Verificar se é do tipo correto (Azure Key Vault vs Databricks)

---
**🎯 Execute o Passo 1 primeiro para ver o status atual das scopes!**
