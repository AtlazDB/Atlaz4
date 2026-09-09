# Atlaz - Projeto **GeoRural DataHub**

# Documentação - Sprint 1

> Status da Sprint: Em andamento 🚧

---

## 🏅 Desafio

Estabelecer o fluxo inicial de entrada e preparação dos dados do **GeoRural DataHub**. Isso inclui o cadastro das fontes de dados, a importação dos arquivos para a Zona Bruta, a validação das informações recebidas e a padronização dos dados válidos para utilização nas etapas posteriores de cruzamento geoespacial e cálculo dos indicadores ambientais.

---

| Capacidade estimada da Equipe por Sprint:               | pontos                                          |
| ------------------------------------------------------- | -------------------------------------------- |
| Meta da Sprint:                                         | User Stories de rank 1 e 2 (Total de 13 pontos)    |
| Previsão da Sprint (extras, sem compromisso de entrega) | User Story de rank 3 (Total de 8 pontos)           |

| Rank | Prioridade | User Story                                                                                                                                                                                                   | Estimativa | Sprint |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------ |
| 1    | Alta       | Como Operador de Dados, quero cadastrar fontes de dados e importar seus arquivos para que os dados recebidos sejam armazenados de forma íntegra e possam ser utilizados pela aplicação.                      | 5          | 1      |
| 2    | Alta       | Como Operador de Dados, quero validar os dados importados e identificar registros inválidos para que inconsistências sejam identificadas e os dados confiáveis sejam separados dos que precisam de correção. | 8          | 1      |
| 3    | Alta       | Como Operador de Dados, quero padronizar os dados válidos para que informações provenientes de diferentes fontes possam ser utilizadas de forma consistente nos cruzamentos e cálculos.                      | 8          | 1      |

---

## 📋 User Stories, DoD & DoR

Nesta seção, detalhamos as histórias de usuário e seus respectivos **DoD (Definition of Done)** e **DoR (Definition of Ready)**, que são os critérios específicos para considerar cada funcionalidade concluída.

### **US01 - Cadastro de Fontes e Importação de Dados**

> **Como Operador de Dados, quero cadastrar fontes de dados e importar seus arquivos para que os dados recebidos sejam armazenados de forma íntegra e possam ser utilizados pela aplicação.**

- **Prioridade:** Alta
    
- **Estimativa:** 5h
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
    - Interface funcional para cadastro das fontes de dados.
        
    - Registro dos metadados necessários para identificação da fonte e do conjunto de dados.
        
    - Permitir a importação dos arquivos suportados pela aplicação.
		
    - Permitir o cadastro e a importação inicial do conjunto de dados do **CAR**, utilizado como fonte base dos imóveis rurais.
	    
    - Armazenamento dos arquivos recebidos na Zona Bruta.
        
    - Geração de hash para garantir a integridade do arquivo original.
        
    - Registro das informações da importação para permitir sua identificação e rastreabilidade.
	    
    - Dados do CAR armazenados de forma que possam ser utilizados nas etapas posteriores de validação, tratamento e cálculo dos indicadores ambientais.
 
- **🏃‍ DoR (Definition of Ready):**
    
    - **Fontes:** Definição das fontes e conjuntos de dados utilizados.
    
	- **Dados de entrada:** Disponibilização de pelo menos um conjunto de dados para realização dos testes de ingestão, validação e padronização.

   	- **Modelagem:** Estrutura para fontes e importações definida.
 
 	- **Armazenamento:** Zona Bruta definida.
 
	- **Design:** Protótipo das telas definido, quando aplicável.
 
---

### **US02 - Validação dos Dados e Quarentena**

> **Como Operador de Dados, quero validar os dados importados e identificar registros inválidos para que inconsistências sejam identificadas e os dados confiáveis sejam separados dos que precisam de correção.**

- **Prioridade:** Alta
    
- **Estimativa:** 8h
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
    - Validação da estrutura dos dados importados.
        
    - Identificação de campos obrigatórios ausentes ou com formato inválido.
        
    - Validação das informações conforme as regras definidas para cada conjunto de dados.
        
    - Identificação de inconsistências nos dados geoespaciais, quando aplicável.
        
    - Separação dos registros considerados inválidos dos dados aprovados.
        
    - Armazenamento dos registros rejeitados na área de Quarentena.
        
    - Registro do motivo da rejeição para permitir análise posterior.
        
    - Disponibilização das informações de validação para acompanhamento pelo Operador de Dados.

- **🏃‍ DoR (Definition of Ready):**
    
    - **Dados de entrada:** Dados importados pela US01 disponíveis.
 
  	- **Modelagem:** Estrutura para dados validados e Quarentena definida.

  	- **Regras:** Critérios para identificar dados válidos e inválidos definidos.
 
  	- **Padronização:** Definição dos formatos esperados para os dados válidos.
 
  	- **Ambiente:** Ambiente de desenvolvimento configurado.

---

### **US03 - Padronização dos Dados**

> **Como Operador de Dados, quero padronizar os dados válidos para que informações provenientes de diferentes fontes possam ser utilizadas de forma consistente nos cruzamentos e cálculos.**

- **Prioridade:** Alta
    
- **Estimativa:** 8h
    
- **Status:** 🚧
    
- **DoD (Critérios de Sucesso):**
    
    - Padronização dos formatos dos dados aprovados.
        
    - Padronização dos nomes e estruturas dos campos utilizados pela aplicação.
        
    - Tratamento de formatos de datas, textos e demais atributos necessários.
        
    - Padronização das informações geoespaciais conforme o sistema de referência definido para a aplicação.
        
    - Persistência dos dados padronizados na Zona Tratada.
        
    - Registro da execução do processo de tratamento e das informações relevantes da operação.
        
    - Dados tratados disponíveis para utilização nas etapas posteriores de cruzamento e cálculo dos indicadores.

- **🏃‍ DoR (Definition of Ready):**
    
    - **Dados de entrada:** Dados aprovados pela US02 disponíveis.
 
  	- **Padronização:** Formatos e padrões dos dados definidos.
 
  	- **Modelagem:** Estrutura dos dados padronizados definida.
   
  	- **Dados geoespaciais:** Sistema de referência definido, quando aplicável.
     
	- **Zona Tratada:** Estrutura para armazenamento dos dados tratados definida.

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
