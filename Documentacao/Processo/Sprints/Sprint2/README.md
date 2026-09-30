# Atlaz - Projeto **GeoRural DataHub**

# Documentação - Sprint 2

> Status da Sprint: Em andamento 🚧

---

## 🏅 Desafio

Estabelecer o fluxo inicial de entrada e preparação dos dados do **GeoRural DataHub**. Isso inclui o cadastro das fontes de dados, a importação dos arquivos para a Zona Bruta, a validação das informações recebidas e a padronização dos dados válidos para utilização nas etapas posteriores de cruzamento geoespacial e cálculo dos indicadores ambientais.

---

| Capacidade estimada da Equipe por Sprint:               | pontos (21)                                          |
| ------------------------------------------------------- | -------------------------------------------- |
| Meta da Sprint:                                         | User Stories de rank 1 e 2 (Total de 13 pontos)    |
| Previsão da Sprint (extras, sem compromisso de entrega) | User Story de rank 3 (Total de 5 pontos)           |

| Rank | Prioridade | User Story                                                                                                                                                                                                   | Estimativa | Sprint |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------ |
|   1   |    Alta    | Como Auditor, quero consultar o histórico das versões dos dados e indicadores e sua origem para que eu possa verificar como os resultados foram produzidos e comparar diferentes versões.                    |    8     |   2    |
|   2   |   Média    | Como Gestor, quero controlar o acesso às funcionalidades da aplicação de acordo com o perfil de cada usuário para que informações e operações importantes sejam protegidas contra acessos não autorizados.   |    5     |   2    |
|   3   |   Média    | Como Analista, quero consultar os indicadores ambientais dos imóveis rurais por meio de uma API para que eu possa utilizar os resultados da plataforma em outros sistemas.                                   |    5     |   3    |

---

## 📋 User Stories, DoD & DoR

Nesta seção, detalhamos as histórias de usuário e seus respectivos **DoD (Definition of Done)** e **DoR (Definition of Ready)**, que são os critérios específicos para considerar cada funcionalidade concluída.

### **US05 - Consultar o histórico das versões dos dados e indicadores e sua origem**

> **Como Auditor, quero consultar o histórico das versões dos dados e indicadores e sua origem para que eu possa verificar como os resultados foram produzidos e comparar diferentes versões.**

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

### **US06 - Controlar o acesso às funcionalidades da aplicação de acordo com o perfil de cada usuário.**

> **Como Gestor, quero controlar o acesso às funcionalidades da aplicação de acordo com o perfil de cada usuário para que informações e operações importantes sejam protegidas contra acessos não autorizados.**

- **Prioridade:** Média
    
- **Estimativa:** 5
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
  - Dados estiverem sendo tratados pelo AirFlow a partir da Zona Bruta.
  - Dados disponibilizados para consumo do front
  - Rastreamento do estado do tratamento

- **🏃‍ DoR (Definition of Ready):**

  - Receber os dados da zona bruta
  - AirFlow configurado em nuvem

---

### **US07  - Consultar os indicadores ambientais dos imóveis rurais por meio de uma API para que eu possa utilizar os resultados da plataforma em outros sistemas.**

> **Como Analista, quero consultar os indicadores ambientais dos imóveis rurais por meio de uma API para que eu possa utilizar os resultados da plataforma em outros sistemas.**

- **Prioridade:** Média
    
- **Estimativa:** 5
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**

  - Endpoints documentados no Swagger
  - Consumo de API retornando dados sobre um determinado imovel passado como parametro

- **🏃‍ DoR (Definition of Ready):**
    
    - Definição dos campos a serem retornados
 
---

## 🏃‍ DoR - Definition of Ready (Sprint 2)

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

Para o fechamento da Sprint 2, a equipe deve atender aos seguintes requisitos gerais:
* Pull Requests revisados e aprovados seguindo o fluxo do **GitHub Flow**.
* Integração contínua: Código consolidado na branch `main` sem quebras de build.
* Documentação técnica: README da sprint atualizado com o status final das entregas.

---

<!-- ## Mockup da aplicação
[🔗 Visualizar protótipo do GeoRural DataHub](https://github.com/user-attachments/files/31893625/georural_datahub_prototype_1.html)

---

# BurndownChart da Sprint
<img width="1167" height="479" alt="image" src="https://github.com/user-attachments/assets/2bd5bbfa-6007-4f0e-9f53-47d128966178" />


---
 # 🎥 Demonstração da aplicação

 > Clique na imagem abaixo para assistir ao vídeo da demonstração da Sprint.
[<img width="1428" height="705" alt="Demonstração da aplicação" src="https://github.com/user-attachments/assets/39af5bfd-e1bd-44b9-9248-85200090dd4b" />](https://youtu.be/QcErlgeITU0)

---
