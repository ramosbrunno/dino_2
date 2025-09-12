# 🎯 DINO SDK v1.1.6 - GUIA DE USO COMPLETO

## ❌ PROBLEMA RESOLVIDO: ModuleNotFoundError

O erro `ModuleNotFoundError: No module named 'dino_scope_manager'` ocorre porque você precisa **instalar o wheel** no Databricks primeiro.

---

## 🚀 SOLUÇÃO COMPLETA

### **PASSO 1: Instalar o Wheel no Databricks**

```python
# Cole este código em uma célula do seu notebook Databricks
%pip install /FileStore/shared_uploads/your_email/dino_sdk-1.1.6-py3-none-any.whl

# OU se você fez upload para DBFS
%pip install /dbfs/FileStore/wheels/dino_sdk-1.1.6-py3-none-any.whl
```

### **PASSO 2: Reiniciar o Kernel**

```python
# Reiniciar o kernel para carregar o pacote
dbutils.library.restartPython()
```

### **PASSO 3: Usar a Função Simplificada**

```python
# Agora a importação vai funcionar
from dino_scope_manager import dino_create_keyvault_scope

# Usar com seus parâmetros específicos
success = dino_create_keyvault_scope(
    subscription_id="bfb09176-b505-4a45-b6a9-d17bd8dc577e",
    resource_group="data-master-dev-rsg",
    tenant_id="94c7139f-16a8-4733-86c1-c5f67366ec1f",
    keyvault_name="data-master-dev-akv-1g67"
)

if success:
    print("✅ Secret Scope criado com sucesso!")
    print("🔗 Agora você pode usar: dbutils.secrets.get('data-master-dev-akv-1g67-scope', 'secret-name')")
else:
    print("❌ Erro ao criar Secret Scope")
```

---

## 📋 PARÂMETROS DA FUNÇÃO

### `dino_create_keyvault_scope()`

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `subscription_id` | str | ✅ | ID da subscription Azure |
| `resource_group` | str | ✅ | Nome do resource group |
| `tenant_id` | str | ✅ | ID do tenant Azure |
| `keyvault_name` | str | ✅ | Nome do Key Vault |
| `scope_name` | str | ❌ | Nome do scope (opcional) |
| `force_databricks` | bool | ❌ | Forçar modo Databricks (padrão: True) |

### **Exemplo com Scope Name Personalizado**

```python
success = dino_create_keyvault_scope(
    subscription_id="bfb09176-b505-4a45-b6a9-d17bd8dc577e",
    resource_group="data-master-dev-rsg",
    tenant_id="94c7139f-16a8-4733-86c1-c5f67366ec1f",
    keyvault_name="data-master-dev-akv-1g67",
    scope_name="meu-projeto-secrets"  # Nome personalizado
)
```

---

## 🔧 COMO FAZER UPLOAD DO WHEEL

### **Opção 1: Upload via Interface Databricks**

1. Baixe o wheel: `dino_sdk-1.1.6-py3-none-any.whl`
2. No Databricks, vá em **Data** → **Create Table**
3. **Upload file** → Selecione o `.whl`
4. Copie o caminho do arquivo (ex: `/FileStore/shared_uploads/...`)

### **Opção 2: Upload via DBFS**

```python
# Fazer upload via código
dbutils.fs.cp("file:/local/path/dino_sdk-1.1.6-py3-none-any.whl", 
              "/dbfs/FileStore/wheels/dino_sdk-1.1.6-py3-none-any.whl")
```

---

## 🧪 TESTE COMPLETO

```python
# 1. Instalar
%pip install /path/to/dino_sdk-1.1.6-py3-none-any.whl

# 2. Reiniciar
dbutils.library.restartPython()

# 3. Testar importação
try:
    from dino_scope_manager import dino_create_keyvault_scope
    print("✅ Importação funcionou!")
except ImportError as e:
    print(f"❌ Erro de importação: {e}")

# 4. Listar scopes existentes (opcional)
scopes = dbutils.secrets.listScopes()
print("📋 Scopes existentes:")
for scope in scopes:
    print(f"   • {scope.name}")

# 5. Criar novo scope
success = dino_create_keyvault_scope(
    subscription_id="bfb09176-b505-4a45-b6a9-d17bd8dc577e",
    resource_group="data-master-dev-rsg", 
    tenant_id="94c7139f-16a8-4733-86c1-c5f67366ec1f",
    keyvault_name="data-master-dev-akv-1g67"
)

# 6. Verificar resultado
if success:
    print("🎉 Secret Scope criado!")
    
    # Testar acesso (se houver secrets no Key Vault)
    try:
        # Substitua 'your-secret-name' por um secret real do seu Key Vault
        secret_value = dbutils.secrets.get("data-master-dev-akv-1g67-scope", "your-secret-name")
        print("✅ Acesso ao secret funcionando!")
    except Exception as e:
        print(f"ℹ️  Secret Scope criado, mas não há secrets para testar: {e}")
```

---

## 🔍 TROUBLESHOOTING

### **Erro: ModuleNotFoundError**
✅ **Solução**: Instalar o wheel e reiniciar o kernel

### **Erro: Permissões no Key Vault**
✅ **Solução**: Verificar se o Service Principal tem acesso ao Key Vault

### **Erro: Workspace não tem acesso ao Azure**
✅ **Solução**: Configurar networking/firewall rules

### **Erro: API compatibility**
✅ **Solução**: O wheel já inclui fallback automático para todas as versões do databricks-sdk

---

## 🎯 RESULTADO ESPERADO

Quando tudo funcionar corretamente, você verá:

```
🎯 DINO Create KeyVault Scope - Função Simplificada
=======================================================
🔧 Subscription ID: bfb09176-b505-4a45-b6a9-d17bd8dc577e
🏢 Resource Group: data-master-dev-rsg
🔑 Key Vault: data-master-dev-akv-1g67
🏢 Tenant ID: 94c7139f-16a8-4733-86c1-c5f67366ec1f
📋 Scope Name: data-master-dev-akv-1g67-scope

🔐 DINO Secret Scope Manager v1.1.6
=============================================
🔧 Criando Secret Scope: data-master-dev-akv-1g67-scope
🗂️  Key Vault: data-master-dev-akv-1g67
✅ Cliente Databricks conectado: https://your-workspace.azuredatabricks.net
🔑 Key Vault Resource ID: /subscriptions/bfb09176-b505-4a45-b6a9-d17bd8dc577e/resourceGroups/data-master-dev-rsg/providers/Microsoft.KeyVault/vaults/data-master-dev-akv-1g67
🌐 Key Vault DNS Name: https://data-master-dev-akv-1g67.vault.azure.net/
🏢 Tenant ID: 94c7139f-16a8-4733-86c1-c5f67366ec1f
✅ Secret scope criada via api_client.do (ou requests)
✅ Secret Scope 'data-master-dev-akv-1g67-scope' criado com sucesso!
🔗 Conectado ao Key Vault: data-master-dev-akv-1g67
```

---

## 📞 SUPORTE

Se ainda houver problemas:

1. ✅ Confirme que está executando em um **notebook Databricks** (não local)
2. ✅ Verifique se tem **permissões de admin** no workspace
3. ✅ Confirme que o **Key Vault existe** e é acessível
4. ✅ Verifique se o **Service Principal** está configurado corretamente

O DINO SDK v1.1.6 está pronto para produção! 🚀
