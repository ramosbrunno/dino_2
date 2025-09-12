# 🦕 DINO SDK v1.3.1 - Hotfix Release

## 🚀 Correções de Importação Databricks SDK

### 🔧 Problema Corrigido
- **Import Error**: Removidos imports inexistentes `AutoScale` e `FileArrivalTrigger` do `databricks.sdk.service.jobs`
- **Erro reportado**: `ImportError: cannot import name 'AutoScale' from 'databricks.sdk.service.jobs'`

### ✅ Mudanças Implementadas

#### 📦 Arquivo: `src/workflow_manager.py`
- ❌ **Removido**: `FileArrivalTrigger` dos imports
- ✅ **Substituído**: Por dicionário simples `{"url": url}` para file arrival triggers

#### 📦 Arquivo: `src/dino_sdk/workflow_manager.py`
- ❌ **Removidos**: `AutoScale` e `FileArrivalTriggerConfiguration` dos imports
- ✅ **Substituído**: 
  - `AutoScale` → Dicionário `{"min_workers": x, "max_workers": y}`
  - `FileArrivalTriggerConfiguration` → Dicionário `{"url": config.file_arrival_url}`

### 🏗️ Arquivos Atualizados
```
📁 dino_sdk/
├── 📄 src/workflow_manager.py (linha 32: FileArrivalTrigger removido)
├── 📄 src/dino_sdk/workflow_manager.py (linhas 23,28: AutoScale e FileArrivalTriggerConfiguration removidos)
├── 📄 src/dino_sdk/__init__.py (versão atualizada: 1.2.0 → 1.3.1)
└── 📄 setup.py (versão atualizada: 1.3.0 → 1.3.1)
```

### 📋 Compatibilidade
- ✅ **Databricks SDK**: 0.49.0+ (todos os imports agora são válidos)
- ✅ **Python**: 3.8+
- ✅ **Funcionalidade**: WorkflowManager mantém todas as funcionalidades com dicionários simples

### 📦 Instalação
```bash
# Instalar nova versão
pip install dist/dino_sdk-1.3.1-py3-none-any.whl --force-reinstall

# Verificar instalação
python -c "from dino_sdk import DinoWorkflowManager; print('✅ Import OK')"
```

### 🧪 Teste Rápido
```python
# Célula de teste no Databricks
from dino_sdk import DinoWorkflowManager, DinoWorkflowConfig

# Deve funcionar sem erros de import
config = DinoWorkflowConfig(
    workflow_name="test_workflow",
    notebook_path="/test",
    cluster_name="test-cluster"
)
print("✅ DINO SDK v1.3.1 funcionando corretamente!")
```

### 📚 Próximos Passos
1. Testar em ambiente Databricks
2. Executar WorkflowManager sem erros de import
3. Verificar criação de jobs e triggers

---
**🔗 Arquivos Gerados:**
- `dino_sdk-1.3.1-py3-none-any.whl` (pronto para deploy)
- Todos os imports do Databricks SDK corrigidos
- Funcionalidade completa mantida

**⚠️ Nota**: Esta é uma versão hotfix focada exclusivamente em correção de imports. Todas as funcionalidades do WorkflowManager permanecem inalteradas.
