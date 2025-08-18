<div align="center">
  <h1 align="center">
    DINO - Data Ingestion Non Optimized
    <br />
    <a href="">
      <img src="https://github.com/user-attachments/assets/98def47f-e7d9-46c5-8347-96ddd6addd8c" alt="DINO">
    </a>
  </h1>

</div>

<p align="center">
  <a href="#status" alt="Estado do Projeto"><img src="http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=flat" /></a>
  <a href=""><img src="https://img.shields.io/badge/python-3.12.6-green" alt="python version"></a>
</p>

## Introdução

DINO é a solução definitiva para democratizar a ingestão de arquivos, resolvendo um problema persistente para muitas áreas de negócio. Nosso objetivo é simplificar radicalmente o uso e garantir que as boas práticas sejam seguidas de forma organizada e controlada. Isso resulta em uma solução que não só é escalável e intuitiva, mas que também assegura a governança completa dos dados. Com o DINO, o processo se torna fácil de adotar para quem usa e simples de manter para a equipe técnica, entregando valor de forma consistente.


## Contexto

Em muitos projetos de dados, é comum a necessidade de ingestão de arquivos provenientes de áreas de negócio ou fornecedores externos que não seguem uma periodicidade fixa — podendo variar de uma vez por mês a diversas vezes ao dia. Esses arquivos, geralmente em formatos como CSV, Excel ou JSON, são movimentados manualmente para diretórios de rede compartilhados, exigindo esforço operacional constante e propenso a erros.

Esse tipo de cenário é conhecido como ingestão ad hoc, sendo comum em empresas que ainda estão em processo de modernização do seu pipeline de dados. Segundo práticas de mercado, conforme descrito pela Microsoft e pela Databricks, esse tipo de ingestão pode ser tratado de forma mais eficiente com pipelines automatizados e interfaces que permitam ao usuário final realizar o upload dos arquivos com validação, versionamento e rastreabilidade.

Além disso, é importante destacar que nem todos os dados ingeridos têm como destino final uma tabela — muitos arquivos são utilizados como parâmetros de entrada para processamento, configurações temporárias ou dados de controle, exigindo maior flexibilidade na arquitetura de ingestão.

Este projeto nasce como uma proposta para automatizar esse fluxo, reduzindo dependência de times técnicos, promovendo rastreabilidade e padronização, e possibilitando a governança de dados mesmo em cargas esporádicas.


## Proposta

Como solução para os desafios apresentados, propomos a criação de uma biblioteca PySpark especializada na ingestão de arquivos avulsos, com foco em simplicidade, reusabilidade e escalabilidade. A biblioteca será distribuída como um pacote Python e poderá ser executada a partir de uma CLI (Command Line Interface) intuitiva e configurável.

Essa abordagem tem como objetivo principal abstrair a complexidade técnica do processo de ingestão, permitindo que diferentes times consigam operar e manter o pipeline de forma padronizada, auditável e segura.

Principais funcionalidades:
- Execução via linha de comando com parâmetros simples e objetivos.
- Suporte a ingestão de arquivos CSV.
- Persistência em camadas de dados (raw/bronze) com particionamento inteligente.
- Validação de arquivos, com logs estruturados e controle de erros.
- Flexibilidade para ingestão de arquivos utilizados como tabelas ou como parâmetros.
- Versionamento e rastreabilidade dos dados ingeridos.

Benefícios esperados:
- Redução do esforço manual na ingestão de dados.
- Padronização do processo entre diferentes projetos e domínios.
- Facilidade de manutenção e evolução do pipeline.
- Aumento da confiabilidade e governança dos dados carregados.

A biblioteca foi projetada exclusivamente para o ambiente Databricks, aproveitando todo o potencial da plataforma, como o manuseio eficiente de arquivos em cloud storage, execução distribuída, notebooks integrados, jobs agendados e logs centralizados. Isso garante maior integração com os recursos nativos da plataforma e promove uma adoção mais fluida pelos times técnicos.


## Execução do Projeto

A execução do projeto DINO ocorre em duas etapas fundamentais e sequenciais, cada uma com seu SDK específico:

### 1. DINO ARC - Provisionamento de Infraestrutura

O primeiro passo é a execução do **DINO ARC** (Azure Resource Creation), responsável pelo provisionamento automático de toda a infraestrutura necessária no Azure. Esta etapa funcional abrange:

- Criação e configuração do ambiente Azure Databricks
- Provisionamento de Storage Accounts para as camadas de dados (RAW, Bronze, Silver, Gold)
- Configuração de Azure SQL Database para logs técnicos e metadados
- Integração com Azure Key Vault para gerenciamento seguro de credenciais
- Configuração de permissões e políticas de segurança via Azure Active Directory
- Setup automático de redes e conectividade entre os serviços

Para informações detalhadas sobre instalação, configuração e execução do DINO ARC, consulte o [README do DINO ARC](./dino_arc/README.md).

### 2. DINO SDK - Execução da Ingestão de Dados

Após o provisionamento da infraestrutura, o **DINO SDK** (Data Ingestion Non Optimized) é utilizado para realizar a ingestão propriamente dita. Esta etapa funcional engloba:

- Interface CLI intuitiva para execução de ingestões
- Motor de processamento de arquivos com suporte a múltiplos formatos
- Orquestração de workflows de dados automatizados
- Aplicação de regras de qualidade e validação de dados
- Geração automática de logs e relatórios de execução
- Suporte a execução em modo batch

Para informações detalhadas sobre instalação, configuração e exemplos de uso do DINO SDK, consulte o [README do DINO SDK](./dino_sdk/README.md).


## Arquitetura

### Visão Geral
A arquitetura da biblioteca foi projetada para ser leve, objetiva e totalmente integrada ao ecossistema do Azure Databricks. Ela promove a automação da ingestão de arquivos avulsos por meio de uma interface de linha de comando (CLI) simples e eficiente. O objetivo é abstrair a complexidade da leitura e persistência de dados em ambientes Spark, eliminando a necessidade de arquivos de configuração externos.

O processo de ingestão de dados acontece em um ambiente Databricks, provisionado automaticamente pelo nosso SDK ARC (Azure Resource Creation). Essa automação garante consistência e segurança na criação de recursos essenciais como Storage Accounts, SQL Databases, e integrações cruciais com Key Vault e Active Directory. Para a ingestão em si, nosso SDK DINO (Data Ingestion Non Optimized) cuida de tudo: a CLI do DINO pode ser executada tanto dentro quanto fora do ambiente Databricks, e o SDK assegura a criação e configuração completa do pipeline de ingestão, garantindo as melhores práticas.
<img width="1204" height="581" alt="image" src="https://github.com/user-attachments/assets/f648b409-888b-422e-8ad6-26aaecab61ec" />

### Arquitetura Técnica

O DINO é um componente de automação que orquestra a leitura e a gravação de dados em ambientes Databricks, operando sobre qualquer arquitetura: Medalhão ou Data Vault, por exemplo. A seguir, detalhamos seu funcionamento técnico na movimentação de arquivos da camada RAW para a Sandbox ou diretamente para a camada Bronze ou Landing Area.

<img width="1210" height="673" alt="image" src="https://github.com/user-attachments/assets/0c4c392d-ad6b-45d7-922b-dd6ef8f2b43a" />

<img width="1361" height="904" alt="image" src="https://github.com/user-attachments/assets/800aeb67-368d-417d-b352-d34aaec09ddb" />


#### Inicialização via CLI

A ingestão é iniciada por meio de uma chamada à CLI do DINO, que oferece uma interface intuitiva e configurável. A CLI recebe parâmetros essenciais que definem o esquema de destino, entidade a ser processada, localização do arquivo de origem e configurações de processamento, incluindo opções para execução automatizada ou sob demanda.

#### Resolução de Metadados
Com base no nome do schema e da tabela informados, o DINO realiza consultas ao catálogo de metadados internos para:
 - Verificar se o usuário possui permissão para criação de tabelas no schema especificado
 - Validar a existência prévia da tabela no catálogo
 - Confirmar se há permissão de escrita na tabela de destino


#### Leitura do Arquivo RAW
Com base no path fornecido, o DINO realiza a leitura do arquivo utilizando APIs nativas do Spark, com suporte para:
 - Leitura de arquivos particionados
 - Aplicação automática de inferência de schema (ou uso de schema definido)
 - Suporte a opções como delimitadores, encoding, multiline, etc.

#### Enriquecimento e Padronização
Antes da persistência, os dados passam pelas seguintes etapas:
 - Inclusão de colunas técnicas (ingestion_datetime, source_file)
 - Normalização de colunas (ex: remoção de acentos e espaços)

#### Escrita na Camada de Destino
Os dados são persistidos na camada de destino (Sandbox ou Bronze) em formato Delta Lake, utilizando Liquid Clustering com clusterização automática para otimizar performance e organização dos dados. O processo de escrita contempla:
 - Escrita idempotente, garantindo reprocessamentos seguros sem duplicidade
 - Criação automática de diretórios, conforme a estrutura do destino
 - Gerenciamento automático de schema, com suporte a schema evolution e schema enforcement para integridade e consistência estrutural dos dados

#### Geração de Logs Técnicos
Durante toda a execução, o DINO registra logs técnicos e operacionais em uma instância do Azure SQL Database, permitindo rastreabilidade e auditoria. Os principais eventos registrados incluem:
 - Status da execução: iniciado, concluído com sucesso ou com erro
 - Volume de dados: quantidade de registros lidos e gravados
 - Paths utilizados: caminhos de origem e destino dos arquivos
 - Tempo total de execução
 - Detalhamento de erros, quando houver, incluindo mensagens e stack trace (se aplicável)


## Melhorias do Projeto

O projeto DINO possui diversos pontos de evolução e melhorias que podem ser implementados em versões futuras para expandir suas capacidades e otimizar sua performance:

### Funcionalidades
- **Suporte a novos formatos de arquivo**: Extensão para formatos como Parquet, Avro, ORC e XML
- **Processamento em tempo real**: Implementação de streaming para ingestão contínua de dados
- **Interface gráfica**: Desenvolvimento de uma UI web para facilitar o uso por usuários não técnicos
- **Conectores nativos**: Integração direta com sistemas como SAP, Oracle, SQL Server e APIs REST
- **Validação avançada de dados**: Implementação de regras de qualidade de dados mais robustas
- **Suporte multi-cloud**: Expansão para AWS e Google Cloud Platform

### Performance e Escalabilidade
- **Processamento paralelo**: Otimização para processamento distribuído de múltiplos arquivos
- **Cache inteligente**: Implementação de estratégias de cache para melhorar performance
- **Compressão automática**: Otimização de armazenamento com compressão adaptativa
- **Auto-scaling**: Dimensionamento automático de recursos baseado no volume de dados

### Governança e Segurança
- **Data lineage**: Rastreamento completo da linhagem dos dados
- **Catalogação automática**: Integração com catálogos de dados empresariais
- **Criptografia avançada**: Implementação de criptografia end-to-end
- **Auditoria completa**: Logs detalhados para compliance e auditoria

### Operação e Monitoramento
- **Dashboard de monitoramento**: Interface para acompanhamento em tempo real das execuções
- **Alertas proativos**: Sistema de notificações para falhas e anomalias
- **Métricas de performance**: Coleta e análise de métricas operacionais
- **Backup e recuperação**: Estratégias automatizadas de backup e disaster recovery


## Referências do Projeto

Este projeto foi desenvolvido utilizando as melhores práticas e tecnologias de mercado. Abaixo estão as principais referências técnicas utilizadas:

### Plataformas e Serviços Cloud
- **[Azure Databricks](https://docs.microsoft.com/en-us/azure/databricks/)** - Plataforma de analytics unificada
- **[Azure Storage](https://docs.microsoft.com/en-us/azure/storage/)** - Serviços de armazenamento em nuvem
- **[Azure SQL Database](https://docs.microsoft.com/en-us/azure/azure-sql/)** - Banco de dados gerenciado
- **[Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/)** - Gerenciamento de chaves e segredos
- **[Azure Active Directory](https://docs.microsoft.com/en-us/azure/active-directory/)** - Serviços de identidade

### Tecnologias de Processamento de Dados
- **[Apache Spark](https://spark.apache.org/docs/latest/)** - Motor de processamento distribuído
- **[Delta Lake](https://docs.delta.io/latest/index.html)** - Camada de armazenamento para data lakes
- **[PySpark](https://spark.apache.org/docs/latest/api/python/)** - API Python para Apache Spark
- **[Liquid Clustering](https://docs.databricks.com/en/delta/clustering.html)** - Otimização de performance para Delta Lake

### Frameworks e Bibliotecas Python
- **[Python](https://docs.python.org/3/)** - Linguagem de programação principal
- **[Click](https://click.palletsprojects.com/)** - Framework para criação de CLIs
- **[PyTest](https://docs.pytest.org/)** - Framework de testes

### Infraestrutura como Código
- **[Terraform](https://www.terraform.io/docs)** - Provisionamento de infraestrutura
- **[Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)** - Provider Terraform para Azure

### Arquiteturas de Referência
- **[Microsoft Data Architecture Guide](https://docs.microsoft.com/en-us/azure/architecture/data-guide/)** - Guia de arquitetura de dados da Microsoft
- **[Databricks Lakehouse Platform](https://docs.databricks.com/lakehouse/index.html)** - Arquitetura Lakehouse
- **[Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)** - Padrão de arquitetura em camadas
- **[Data Vault 2.0](https://datavaultalliance.com/)** - Metodologia de modelagem de dados





