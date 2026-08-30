<img width="1074" height="196" alt="Captura de tela 2026-08-30 162135" src="https://github.com/user-attachments/assets/742050b7-d47e-4643-b9cc-ec2421e037af" />


# GeoRural DataHub
<p align="center">
  | <a href="#desafio"> Desafio</a> |
  <a href="#solucao"> Solução</a> |    
  <a href="#backlog"> Backlog do Produto</a> |  
  <a href="#sprint"> Cronograma de Sprints</a> |  
  <a href="#tecnologias">Tecnologias</a> |
  <a href="#estrutura">Estrutura do Projeto</a> |
  <a href="#docs">Documentação</a> |
  <a href="#equipe"> Equipe</a> |
</p>

## 🏅 Desafio <a id="desafio"></a>

A Visiona atua em projetos que utilizam informações territoriais, ambientais e geoespaciais para apoiar processos de análise, planejamento e tomada de decisão. Em diversos cenários, informações relacionadas a imóveis rurais são obtidas de diferentes fontes de dados, públicas ou privadas, contendo registros cadastrais, informações geográficas e indicadores produzidos ao longo do tempo. Atualmente, a diversidade de formatos, níveis de qualidade e atualizações periódicas dificulta a rastreabilidade e a auditabilidade dos dados. Não é simples identificar quais fontes, versões e regras de negócio participaram do cálculo de um indicador específico, gerando desafios de transparência e confiabilidade.

## 🏅 Solução <a id="solucao"></a>

Desenvolvimento do **GeoRural DataHub**, uma plataforma web com **Spring Boot** no back-end e **Vue.js** no front-end. A solução centraliza o controle, validação e governança de dados territoriais em um banco de dados relacional **Oracle**, permitindo a gestão de lotes de ingestão, rastreabilidade completa (*data lineage*) de indicadores ambientais, controle de qualidade de registros rurais através de procedimentos em **PL/SQL** e visualização espacial interativa e reativa com suporte a dados em tempo real via **WebSocket**.

---

## 📋 Backlog do Produto <a id="backlog"></a>

| ID | Prioridade | User Story | Est. (h) | Sprint | Status |
| :--: | :---: | --- | :---: | :---: | :---: |
| **US01** | ... | .... | xx | x | ...✅⚙️ |
| **US02** | ... | .... | xx | x | ...✅⚙️ |
| **US0X** | ... | .... | xx | x | ...✅⚙️ |
---

## Cronograma das Sprints <a id="sprint"></a>

|    Sprint    | Início |   Fim   | Documentação | Status | 
| :----------: | :----: | :-----: | :----------: | :----: |
| 🔖 Sprint 1 | 07/09  | 27/09 |   [Sprint 1](./Documentacao/Processo/Sprints/Sprint1/README.md)             |  Em Andamento ⚙️     |
| 🔖 Sprint 2 | 05/10  | 25/10 |   [Sprint 2](./Documentacao/Processo/Sprints/Sprint2/README.md)             |  Em Andamento ⚙️     |
| 🔖 Sprint 3 | 02/11  | 22/11 |   [Sprint 3](./Documentacao/Processo/Sprints/Sprint3/README.md)             |  Em Andamento ⚙️     |

---
## 💻 Tecnologias <a id="tecnologias"></a>

<h4 align="center">
  <a href="https://www.oracle.com/java/"><img src="https://img.shields.io/badge/Java-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white"/></a>
  <a href="https://spring.io/projects/spring-boot"><img src="https://img.shields.io/badge/SpringBoot-6DB33F?style=for-the-badge&logo=springboot&logoColor=white"/></a>
  <a href="https://www.oracle.com/database/"><img src="https://img.shields.io/badge/Oracle_Spatial-F80000?style=for-the-badge&logo=oracle&logoColor=white"/></a>
  <a href="https://vuejs.org/"><img src="https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D"/></a>
  <a href="https://leafletjs.com/"><img src="https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white"/></a>
  <a href="https://www.chartjs.org/"><img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white"/></a>
  <a href="https://pinia.vuejs.org/"><img src="https://img.shields.io/badge/Pinia-FFE56E?style=for-the-badge&logo=vue.js&logoColor=black"/></a>
  <a href="https://github.com/"><img src="https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white"/></a>
</h4>

## 🏛️ Estrutura do Repositório <a id="estrutura"></a>

- **`backend/`**: API RESTful desenvolvida em Java (Spring Boot) com Spring Data JPA/Hibernate Spatial e Spring Security. Responsável pelas regras de negócio, ingestão de dados geoespaciais, controle de autenticação/autorização, endpoints WebSocket e chamadas a procedures/functions em PL/SQL no banco Oracle.
- **`frontend/`**: Interface web reativa em Vue.js 3 com gerenciamento de estado via Pinia, Axios para requisições assíncronas, Leaflet.js para renderização de mapas GIS e Chart.js para exibição dos indicadores ambientais.
- **`database/`**: Scripts DDL do Oracle Database, incluindo definições de `SDO_GEOMETRY`, triggers, procedures PL/SQL para validação de geometrias e rastreabilidade de dados.
- **`Documentacao/`**: Documentação técnica, especificações de arquitetura e relatórios das Sprints.

## 📂 Documentação <a id="docs"></a>

* 📑 [**Checklist DoR & DoD**](./Documentacao/Processo/Checklist/README.md) - Critérios de início e conclusão de tarefas.
* 🌳 [**Estratégia de Branch & Commits**](./Documentacao/Governanca/README.md) - Fluxo de trabalho no GitHub.

## Equipe

| Foto                                                                     |        Nome       |    Função     |                                                                         Github                                                                        |                                                                                             Linkedin                                                                                              |
| ----------------------------------------------------------------------- | :---------------: | :-----------: | :---------------------------------------------------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| <img src="https://github.com/GabrielRocha-27.png?size=50" width="50">   |   Gabriel Rocha   |   Scrum Master  |  <a href="https://github.com/GabrielRocha-27"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>  |          <a href="https://www.linkedin.com/in/gabriel-rocha-wk27/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>           |
| <img src="https://github.com/LeandroHCampos.png?size=50" width="50">    | Leandro Henrique |  Product Owner  |  <a href="https://github.com/LeandroHCampos"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>   |            <a href="https://www.linkedin.com/in/leandrohcampos/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>            |
| <img src="https://github.com/gabrielnunes926.png?size=50" width="50">   |   Gabriel Nunes   |   Dev. Team   |  <a href="https://github.com/gabrielnunes926"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>  | <a href="https://www.linkedin.com/in/gabriel-de-barcelos-nunes-a7a69832a/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a> |
| <img src="https://github.com/gabrielvalentesjc.png?size=50" width="50"> | Gabriel Valente   |   Dev. Team   | <a href="https://github.com/gabrielvalentesjc"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a> |      <a href="https://www.linkedin.com/in/gabriel-valente-b4897226b/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a>       |
| <img src="https://github.com/ManuelaBrito.png?size=50" width="50">   |   Manuela Brito   |   Dev. Team   |  <a href="https://github.com/ManuelaBrito"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>  | <a href="https://www.linkedin.com/in//"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a> |
| <img src="https://github.com/xRod-Rodriguesx.png?size=50" width="50">   |   Rodolfo Corbalan   |   Dev. Team   |  <a href="https://github.com/xRod-Rodriguesx"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white"></a>  | <a href="https://www.linkedin.com/in/rodolfo-corbalan-2a02b4207/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white"></a> |
