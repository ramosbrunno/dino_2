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
   <a href=""><img src="https://img.shields.io/badge/npm-10.8.2-blue" alt="python version"></a>
  <a href=""><img src="https://img.shields.io/badge/python-3.12.6-green" alt="python version"></a>
</p>

## Introdução

DINO é uma SDK para ingestão de arquivos manuais, criado para solucionar um problema recorrente em áreas de negócio. O objetivo principal é otimizar o processo de ingestão de arquivos em ambientes de big data cloud, oferecendo uma solução escalável e amigável, mas mantendo toda a governança dos dados.


## Contexto

Em muitos projetos de dados, é comum a necessidade de ingestão de arquivos provenientes de áreas de negócio ou fornecedores externos que não seguem uma periodicidade fixa — podendo variar de uma vez por mês a diversas vezes ao dia. Esses arquivos, geralmente em formatos como CSV, Excel ou JSON, são movimentados manualmente para diretórios de rede compartilhados, exigindo esforço operacional constante e propenso a erros.

Esse tipo de cenário é conhecido como ingestão ad hoc, sendo comum em empresas que ainda estão em processo de modernização do seu pipeline de dados. Segundo práticas de mercado, conforme descrito pela Microsoft e pela Databricks, esse tipo de ingestão pode ser tratado de forma mais eficiente com pipelines automatizados e interfaces que permitam ao usuário final realizar o upload dos arquivos com validação, versionamento e rastreabilidade.

Além disso, é importante destacar que nem todos os dados ingeridos têm como destino final uma tabela — muitos arquivos são utilizados como parâmetros de entrada para processamento, configurações temporárias ou dados de controle, exigindo maior flexibilidade na arquitetura de ingestão.

Este projeto nasce como uma proposta para automatizar esse fluxo, reduzindo dependência de times técnicos, promovendo rastreabilidade e padronização, e possibilitando a governança de dados mesmo em cargas esporádicas.


## Proposta

Proposta
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


