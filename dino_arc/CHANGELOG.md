# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-08

### Added
- **CLI Global**: Comando `dino-arc` disponível após instalação via pip
- **Instalação Simplificada**: Scripts `install.sh` e `install.bat` para instalação automática
- **Package Distribution**: Configuração completa do setup.py para distribuição pip
- **MANIFEST.in**: Inclusão automática de todos os arquivos necessários no pacote
- **Infraestrutura Completa**: Terraform modular com Foundation e Databricks Premium
- **Unity Catalog**: Configuração automática do Unity Catalog após deploy
- **Databricks Premium**: SKU Premium com todos os recursos habilitados
- **Serverless Computing**: Suporte completo a Serverless SQL e Compute
- **Autenticação Service Principal**: Autenticação via Azure Service Principal
- **Configuração Automática**: Scripts Python para configuração pós-deploy do Databricks
- **Testes Abrangentes**: Suite de testes unitários para todos os componentes
- **Documentação Completa**: README detalhado com exemplos de uso

### Features
- Criação automática de Resource Group, Storage Account, Key Vault
- Deploy do Azure Databricks Premium com Unity Catalog
- Configuração automática de workspace Databricks
- Scripts de configuração para Unity Catalog e Serverless
- CLI com validação de parâmetros e feedback detalhado
- Suporte a múltiplos ambientes (dev, staging, prod)
- Integração completa Azure + Databricks

### Technical Details
- **Terraform**: Versão ≥1.0 com provedores Azure, AzureAD e Random
- **Python**: 3.8+ com dependências Azure SDK e python-terraform
- **Packaging**: setuptools com entry_points para comando global
- **Testing**: unittest com cobertura abrangente
- **Documentation**: Markdown com exemplos práticos

### Installation Methods
1. **Global CLI** (Recomendado): `pip install -e .` + comando `dino-arc`
2. **Traditional**: `python src/cli.py` para desenvolvimento
3. **Automated**: Scripts `install.sh`/`install.bat` para setup automático

### Network Security
- Network Watcher desabilitado em todos os recursos
- Acesso direto à internet para Databricks (sem Private Link)
- Configuração otimizada para Serverless computing

### Breaking Changes
- Removidos parâmetros opcionais da infraestrutura
- Sempre cria todos os componentes (Foundation + Databricks)
- Migração de autenticação `az login` para Service Principal

## [0.2.0] - 2025-01-07

### Added
- Terraform modular com módulos Foundation e Databricks
- Suporte a parâmetros opcionais para criação seletiva
- Scripts básicos de configuração Databricks

### Changed
- Estrutura modular do projeto
- Separação clara entre Foundation e Databricks

## [0.1.0] - 2025-01-06

### Added
- Versão inicial do projeto
- CLI básico com Terraform
- Criação de recursos Azure básicos
