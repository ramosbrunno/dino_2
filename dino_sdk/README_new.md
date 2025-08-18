# 🦕 Dino SDK

**Data Ingestion SDK for Databricks** - SDK simplificado para ingestão de dados no Databricks com suporte híbrido batch/streaming.

## ✨ Características

- ✅ **CLI Unificada**: Comando `dino-ingest` com parâmetros intuitivos
- ✅ **Modo Híbrido**: Suporte a batch e streaming com Auto Loader
- ✅ **Chegada de Arquivos**: Streaming automático com `--is-automated`
- ✅ **Unity Catalog**: Integração completa com schemas existentes
- ✅ **Genie Assistant**: Configuração automática para consultas inteligentes

## 🚀 Instalação

```bash
cd dino_sdk
pip install -e .
```

## 📝 Uso

### Ingestão Batch
```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name clientes \
  --file-path /tmp/dados/clientes.csv \
  --delimiter ',' \
  --has-genie
```

### Ingestão Streaming (Auto Loader)
```bash
dino-ingest \
  --target-schema vendas_db \
  --table-name pedidos \
  --file-path /mnt/landing/pedidos/ \
  --delimiter ',' \
  --is-automated \
  --has-genie
```

## 📂 Estrutura do Projeto

```
dino_sdk/
├── cli.py                 # Interface de linha de comando
├── ingestion_engine.py    # Motor de ingestão híbrido
├── workflow_manager.py    # Gerador de workflows
├── genie_assistant.py     # Integração com Genie
├── __init__.py           # Módulo principal
├── requirements.txt      # Dependências
├── setup.py             # Configuração de instalação
├── README.md            # Documentação
└── tests/               # Testes unitários
```

## 🎯 Parâmetros da CLI

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--target-schema` | ✅ | Schema de destino (deve existir) |
| `--table-name` | ✅ | Nome da tabela a ser criada |
| `--file-path` | ✅ | Caminho dos arquivos |
| `--delimiter` | ❌ | Delimitador CSV (padrão: `,`) |
| `--is-automated` | ❌ | Ativa modo streaming |
| `--has-genie` | ❌ | Configura Genie Assistant |

## 🔄 Modo Streaming

Quando `--is-automated` é usado:
- Ativa **Auto Loader** com notificações de arquivo
- Monitora diretório continuamente
- Processa novos arquivos automaticamente
- Gera workflow JSON para Databricks

## 📊 Arquivos Gerados

- `workflow_dino_auto_ingestion_[schema]_[table].json` - Workflow para Databricks
- `[table]_batch_ingestion.py` ou `[table]_streaming_ingestion.py` - Código Databricks
- `genie_config_[table].json` - Configuração Genie (se `--has-genie`)

## 🛠️ Desenvolvimento

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Executar testes
python -m pytest tests/

# Verificar estrutura
dino-ingest --help
```

## 📋 Requisitos

- Python 3.8+
- Databricks CLI configurado
- Acesso ao Unity Catalog
- Schema de destino pré-existente

---

🦕 **Dino SDK** - Simplificando a ingestão de dados no Databricks!
