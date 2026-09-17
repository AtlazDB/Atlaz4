# Atlaz - Projeto **GeoRural DataHub**

# Documentação - Sprint 1

> Status da Sprint: Em andamento 🚧

---

## 🏅 Desafio

Estabelecer o fluxo inicial de entrada e preparação dos dados do **GeoRural DataHub**. Isso inclui o cadastro das fontes de dados, a importação dos arquivos para a Zona Bruta, a validação das informações recebidas e a padronização dos dados válidos para utilização nas etapas posteriores de cruzamento geoespacial e cálculo dos indicadores ambientais.

---

| Capacidade estimada da Equipe por Sprint:               | pontos (21)                                          |
| ------------------------------------------------------- | -------------------------------------------- |
| Meta da Sprint:                                         | User Stories de rank 1, 2 e 3 (Total de 21 pontos)    |
| Previsão da Sprint (extras, sem compromisso de entrega) | User Story de rank 4 (Total de 8 pontos)           |

| Rank | Prioridade | User Story                                                                                                                                                                                                   | Estimativa | Sprint |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------ |
| 1    | Alta       | Como Operador de Dados, quero cadastrar fontes de dados e importar seus arquivos para que os dados recebidos sejam armazenados de forma íntegra e possam ser utilizados pela aplicação.                      | 8          | 1      |
| 2    | Alta       | Como Operador de Dados, quero disponibilizar os dados territoriais do CAR após seu processamento inicial para que as informações dos imóveis rurais possam ser consultadas pela aplicação. | 8          | 1      |
| 3    | Alta       | Como Analista, quero consultar os imóveis rurais por meio de uma API para que suas informações territoriais possam ser consumidas pela aplicação.                      | 5          | 1      |
| 3    | Alta       | Como Analista, quero visualizar os imóveis rurais e suas divisões territoriais em um mapa para que eu possa localizar e analisar espacialmente os imóveis do Paraná.                      | 8          | 1      |

---

## 📋 User Stories, DoD & DoR

Nesta seção, detalhamos as histórias de usuário e seus respectivos **DoD (Definition of Done)** e **DoR (Definition of Ready)**, que são os critérios específicos para considerar cada funcionalidade concluída.

### **US01 - Cadastro de Fontes e Importação de Dados**

> **Como Operador de Dados, quero cadastrar fontes de dados e importar seus arquivos para que os dados recebidos sejam armazenados de forma íntegra e possam ser utilizados pela aplicação.**

- **Prioridade:** Alta
    
- **Estimativa:** 8
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
	- Cadastro de dados na Zona Bruta
	- Interface para inserção e visualização dos dados e logs
	- O dado precisa receber um hash no Oracle Storage
	- Rastreamento da inserção
 
- **🏃‍ DoR (Definition of Ready):**
    
    - Definição de armazenamento para o DataLake da Zona Bruta (Object Storage OCI)
    - Ambiente configurado
    - Protótipo da inserção
    - Protótipo de visualização do rastreamento da inserção
 
---

### **US02 - Consultadas pela aplicação**

> **Como Operador de Dados, quero disponibilizar os dados territoriais do CAR após seu processamento inicial para que as informações dos imóveis rurais possam ser consultadas pela aplicação.**

- **Prioridade:** Alta
    
- **Estimativa:** 8
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
  - Dados estiverem sendo tratados pelo AirFlow a partir da Zona Bruta.
  - Dados disponibilizados para consumo do front
  - Rastreamento do estado do tratamento

- **🏃‍ DoR (Definition of Ready):**

  - Receber os dados da zona bruta
  - AirFlow configurado em nuvem

---

### **US03 - Informações serem consumidas pela aplicação**

> **Como Analista, quero consultar os imóveis rurais por meio de uma API para que suas informações territoriais possam ser consumidas pela aplicação.**

- **Prioridade:** Alta
    
- **Estimativa:** 5
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**

  - Endpoints documentados no Swagger
  - Consumo de API retornando dados sobre um determinado imovel passado como parametro

- **🏃‍ DoR (Definition of Ready):**
    
    - Definição dos campos a serem retornados
 
---

### **US04 - visualizar os imóveis rurais e suas divisões territoriais em um mapa**

> **Como Analista, quero visualizar os imóveis rurais e suas divisões territoriais em um mapa para que eu possa localizar e analisar espacialmente os imóveis do Paraná.**

- **Prioridade:** Alta
    
- **Estimativa:** 8
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**

  	- Visualização em mapa do território
  	- Filtrar a partir de cod. `imovel/cidade`
  	- Visualização em tabela dos dados de cada imóvel

- **🏃‍ DoR (Definition of Ready):**
    
	- Prototipo (Design)
    - Definição da Tecnologia para envio de dados espaciais para renderização no front end (Ex.: Hibernate Spatial)
    - Definição Ferramenta para exibição dos dados geoespaciais pelo front-end (Ex.: Google Maps)
    - Definição de dados a serem exibidos

---

## 🏃‍ DoR - Definition of Ready (Sprint 1)

Estes critérios garantem que o time tem todos os insumos necessários para iniciar o desenvolvimento desta Sprint:

- **Clareza:** User Stories definidas com objetivos de negócio e critérios de aceitação básicos estabelecidos.
    
- **Fontes de dados:** Definição das fontes e conjuntos de dados que serão utilizados como entrada na Sprint.
    
- **Dados de entrada:** Disponibilização de pelo menos um conjunto de dados para realização do desenvolvimento e testes.

- **Regras:** Regras de validação e padronização necessárias definidas
    
- **Modelagem:** Estrutura inicial do banco de dados definida para o catálogo de fontes, dados importados e registros em Quarentena.
    
- **Ambiente:** Ambiente de desenvolvimento e infraestrutura necessários para execução da aplicação configurados.
    
- **Design:** Protótipo das interfaces necessárias para cadastro, importação e acompanhamento dos dados definido, quando aplicável.


---

## 🏆 Critérios de Conclusão da Sprint

Para o fechamento da Sprint 1, a equipe deve atender aos seguintes requisitos gerais:
* Pull Requests revisados e aprovados seguindo o fluxo do **GitHub Flow**.
* Integração contínua: Código consolidado na branch `main` sem quebras de build.
* Documentação técnica: README da sprint atualizado com o status final das entregas.

---

## Mockup da aplicação
[🔗 Visualizar protótipo do GeoRural DataHub](https://github.com/user-attachments/files/31893625/georural_datahub_prototype_1.html)

<!-- 
# BurndownChart

---
 # 🎥 Demonstração da aplicação

 > Clique na imagem abaixo para assistir ao vídeo da demonstração da Sprint. %-->

---
