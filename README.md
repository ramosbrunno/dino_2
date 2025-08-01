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

A ingestão é iniciada por meio de uma chamada à CLI do DINO, que recebe os seguintes parâmetros obrigatórios:
 - --target-schema: schema destino da ingestão
 - --table-name: nome lógico da entidade a ser processada
 - --file-path: caminho completo do arquivo a ser ingerido no storage RAW
 - --delimiter: delimitador utilizado no arquivo de origem
 - --is-automated: true, realiza ingestão assim que o arquivo é colocado no diretório sem a necessidade de schedule de job

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





