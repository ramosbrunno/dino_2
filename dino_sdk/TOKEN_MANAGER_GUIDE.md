# 🔑 Token Manager - DINO SDK v1.1.4

## 📋 **Resumo**
O **Token Manager** é um componente isolado do DINO SDK v1.1.4 que permite criar e gerenciar tokens Databricks de forma independente, evitando problemas complexos de autenticação no módulo principal.

## 🎯 **Problema Resolvido**
- ✅ **Isolamento**: Separa criação de tokens da lógica principal do Key Vault
- ✅ **Debug Facilitado**: Permite testar autenticação independentemente
- ✅ **Múltiplos Métodos**: Suporta diferentes formas de autenticação
- ✅ **Comando Simples**: Interface CLI clara e intuitiva

## 🚀 **Como Usar**

### **1. Instalação**
```bash
# Instalar DINO SDK v1.1.4
pip install dist/dino_sdk-1.1.4-py3-none-any.whl --force-reinstall
```

### **2. Verificar Métodos Disponíveis**
```bash
# Via comando CLI
dino-token list-auth

# Ou diretamente
cd src
python token_cli.py list-auth
```

**Saída esperada:**
```
🔍 MÉTODOS DE AUTENTICAÇÃO DISPONÍVEIS
==================================================
📊 Resumo:
   ✅ Métodos disponíveis: X/5

🔧 INSTRUÇÕES DE CONFIGURAÇÃO:
1️⃣ Opção 1 - Token existente:...
```

### **3. Configurar Credenciais**

#### **Opção A: Token Existente**
```bash
export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
export DATABRICKS_TOKEN=dapi1234567890abcdef...
```

#### **Opção B: Service Principal**
```bash
export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT_ID=your-tenant-id
```

#### **Opção C: Azure CLI**
```bash
az login
# Em seguida use --workspace na criação do token
```

### **4. Criar Token**

#### **Automático (recomendado)**
```bash
# Tenta todos os métodos disponíveis
dino-token get-token

# Ou diretamente
cd src
python token_cli.py get-token
```

#### **Método Específico**
```bash
# Via variáveis de ambiente
dino-token get-token --method env-vars

# Via Azure CLI
dino-token get-token --method azure-cli --workspace https://workspace.azuredatabricks.net

# Com duração customizada (8 horas)
dino-token get-token --hours 8
```

#### **Formatos de Saída**
```bash
# Formato texto (padrão)
dino-token get-token

# Formato JSON
dino-token get-token --output json

# Formato para export
dino-token get-token --output env
```

## 📊 **Exemplos de Saída**

### **Sucesso - Formato Texto**
```
🎉 TOKEN CRIADO COM SUCESSO!
==================================================
📋 Token ID: 12345678-abcd-efgh-ijkl-1234567890ab
🔑 Access Token: dapi1234567890abcdef...
🌐 Workspace: https://workspace.azuredatabricks.net
⏰ Expira em: 2025-09-03T09:00:00
👤 Criado por: user@company.com

💡 Para usar este token:
   export DATABRICKS_HOST=https://workspace.azuredatabricks.net
   export DATABRICKS_TOKEN=dapi1234567890abcdef...
```

### **Sucesso - Formato JSON**
```json
{
  "token_id": "12345678-abcd-efgh-ijkl-1234567890ab",
  "access_token": "dapi1234567890abcdef...",
  "expires_at": "2025-09-03T09:00:00",
  "workspace_url": "https://workspace.azuredatabricks.net",
  "created_by": "user@company.com",
  "auth_method": "azure-cli",
  "lifetime_hours": 1
}
```

### **Sucesso - Formato ENV**
```bash
export DATABRICKS_HOST=https://workspace.azuredatabricks.net
export DATABRICKS_TOKEN=dapi1234567890abcdef...
```

## 🔧 **Teste e Depuração**

### **Simulação Local**
```bash
# Testar funcionamento sem credenciais reais
cd src
python test_token_simulation.py
```

**Saída esperada:**
```
🧪 SIMULADOR DE TOKEN - DINO SDK v1.1.4
🎭 TOKEN SIMULADO CRIADO!
🎉 SUCESSO: Token Manager v1.1.4 funcionando!
```

### **Verificação de Status**
```bash
# Verificar quais métodos estão configurados
cd src
python token_manager.py
```

## ⚠️ **Solução de Problemas**

### **Erro: "Nenhum método de autenticação configurado"**
```bash
# Verificar variáveis de ambiente
echo $DATABRICKS_HOST
echo $DATABRICKS_TOKEN

# Configurar se necessário
export DATABRICKS_HOST=https://workspace.azuredatabricks.net
export DATABRICKS_TOKEN=your-token
```

### **Erro: "Azure CLI não autenticado"**
```bash
# Fazer login no Azure
az login

# Verificar conta ativa
az account show
```

### **Erro: "Databricks CLI não configurado"**
```bash
# Instalar Databricks CLI
pip install databricks-cli

# Configurar
databricks configure --token
```

### **Erro: "cannot configure default credentials"**
```bash
# Este erro é esperado sem credenciais válidas
# Configure uma das opções acima
```

## 🎯 **Integração com Key Vault**

### **Usar Token Criado**
```bash
# 1. Criar token
dino-token get-token --output env > token_config.sh

# 2. Carregar configuração
source token_config.sh

# 3. Usar no Key Vault
python -c "
from src.keyvault_config import KeyVaultConfigManager
config = KeyVaultConfigManager()
secrets = config.load_secrets_from_scope()
print('✅ Secrets carregados:', len(secrets))
"
```

### **Pipeline Automatizado**
```bash
#!/bin/bash
# Script de pipeline

# Configurar credenciais
export DATABRICKS_HOST=https://workspace.azuredatabricks.net
export DATABRICKS_TOKEN=existing-token

# Criar token temporário
dino-token get-token --hours 2 --output env > .databricks_env

# Carregar token temporário
source .databricks_env

# Executar processo
python your_databricks_script.py

# Limpar arquivo temporário
rm .databricks_env
```

## 📈 **Benefícios**

### **Para Desenvolvimento**
- ✅ **Teste Isolado**: Verificar autenticação independentemente
- ✅ **Debug Fácil**: Logs claros sobre métodos tentados
- ✅ **Múltiplas Opções**: Fallback automático entre métodos

### **Para Produção**
- ✅ **Tokens Temporários**: Reduz exposição de credenciais
- ✅ **Automação**: Criação programática de tokens
- ✅ **Auditoria**: Logs de criação e uso

### **Para CI/CD**
- ✅ **Service Principal**: Autenticação não-interativa
- ✅ **Tokens de Curta Duração**: Maior segurança
- ✅ **Scripts Automatizados**: Integração fácil em pipelines

## 🎊 **Conclusão**

O **Token Manager v1.1.4** resolve o problema de autenticação complexa fornecendo:

1. **Interface Simples**: Comando `dino-token get-token`
2. **Múltiplos Métodos**: Auto-detecção de credenciais disponíveis
3. **Debug Facilitado**: Logs claros sobre o que está funcionando
4. **Integração Limpa**: Tokens criados funcionam com Key Vault

**Use este módulo para:**
- 🔍 **Diagnosticar** problemas de autenticação
- 🔑 **Criar tokens** temporários para desenvolvimento
- 🚀 **Automatizar** processos de CI/CD
- 🧪 **Testar** conectividade antes de usar o Key Vault principal

---

**Próximo passo:** Teste em ambiente Databricks real para validar funcionamento completo!
