# Atlaz - Projeto **GeoRural DataHub**

# Documentação - Sprint 2

> Status da Sprint: Planejada 📅

---

## 🏅 Desafio

Montar a arquitetura de dados do **GeoRural DataHub** para que ela funcione em escala real. As fontes passam a ser coletadas **automaticamente** pelo **Apache Airflow**, a partir de um link e de uma frequência, rodando numa máquina separada da aplicação. Os dados recebidos são **tratados por regras** definidas pelo usuário para cada coluna. O que não passa nas regras vai para a **quarentena**, onde é analisado, corrigido ou descartado. Por fim, calculamos os dois primeiros **indicadores ambientais** por imóvel: Reserva Legal (IRL) e Focos de Calor (IFC). Como entrega extra, o auditor passa a consultar e comparar as **versões** dos dados e rastrear cada resultado até a sua origem.

---

| Capacidade estimada da Equipe por Sprint:               | pontos (26)                                          |
| ------------------------------------------------------- | -------------------------------------------- |
| Meta da Sprint:                                         | User Stories de rank 1, 2, 3 e 4 (Total de 26 pontos)    |
| Previsão da Sprint (extras, sem compromisso de entrega) | User Story de rank 5 (Total de 8 pontos)           |

| Rank | Prioridade | User Story                                                                                                                                                                                                   | Estimativa | Sprint |
| ---- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ------ |
| 1    | Alta       | Como Operador de Dados, quero cadastrar fontes informando o link de acesso, o método de requisição e a frequência de coleta, e acompanhar cada execução, para que os dados sejam atualizados automaticamente e eu identifique falhas sem depender do envio manual de arquivos. | 8          | 2      |
| 2    | Alta       | Como Operador de Dados, quero definir como cada coluna da fonte é tratada (destino, tipo de dado e regras de validação) para que somente dados padronizados e válidos cheguem à zona tratada. | 8          | 2      |
| 3    | Alta       | Como Operador de Dados, quero consultar e tratar os registros rejeitados na validação para que eu possa corrigir, aprovar ou descartar cada inconsistência com justificativa registrada. | 5          | 2      |
| 4    | Alta       | Como Analista, quero consultar os indicadores de Reserva Legal e de focos de calor de cada imóvel rural para que eu possa avaliar sua conformidade ambiental. | 5          | 2      |
| 5    | Média      | Como Auditor, quero consultar o histórico das versões dos dados e indicadores e sua origem para que eu possa verificar como os resultados foram produzidos e comparar diferentes versões. | 8          | 2      |

---

## 📋 User Stories, DoD & DoR

Nesta seção, detalhamos as histórias de usuário e seus respectivos **DoD (Definition of Done)** e **DoR (Definition of Ready)**, que são os critérios específicos para considerar cada funcionalidade concluída.

* **DoR:** tudo o que precisa existir para **começar** a história.
* **DoD:** tudo o que precisa estar pronto para a história ser considerada **finalizada**.
* Nenhuma história depende de outra: cada uma pode ser iniciada e entregue sozinha.

### **US05 - Coleta automática de fontes e acompanhamento das execuções**

> **Como Operador de Dados, quero cadastrar fontes informando o link de acesso, o método de requisição e a frequência de coleta, e acompanhar cada execução, para que os dados sejam atualizados automaticamente e eu identifique falhas sem depender do envio manual de arquivos.**

- **Prioridade:** Alta
    
- **Estimativa:** 8
    
- **Status:** 📅
    
- **DoD (Critérios de Sucesso):**
    
	- Cadastro de fonte com link de acesso, método HTTP (GET ou POST), cabeçalhos, formato do arquivo e frequência de coleta
	- Coleta feita automaticamente pelo Airflow no horário definido
	- Botão "Executar agora" para coletar na hora
	- Arquivo coletado salvo na Zona Bruta com hash
	- Coleta igual à anterior registrada como "sem mudança"
	- Tela de execuções com etapa, status, duração, quantidade de registros e, em caso de falha, a mensagem de erro
	- Airflow rodando em uma máquina separada da aplicação
	- Endpoints documentados no Swagger
 
- **🏃‍ DoR (Definition of Ready):**
    
    - Protótipo do cadastro de fonte e da tela de execuções
    - Um link de fonte pública testado (ex.: malha municipal do IBGE)
    - Máquina do Airflow disponível
    - Campos do cadastro de fonte definidos
 
---

### **US06 - Mapeamento de colunas e regras de tratamento**

> **Como Operador de Dados, quero definir como cada coluna da fonte é tratada (destino, tipo de dado e regras de validação) para que somente dados padronizados e válidos cheguem à zona tratada.**

- **Prioridade:** Alta
    
- **Estimativa:** 8
    
- **Status:** 📅
    
- **DoD (Critérios de Sucesso):**
    
	- Tela de mapeamento de colunas por fonte (coluna de origem → campo de destino), com o tipo de dado
	- Regras por coluna: obrigatório, bloquear regressão, validar geometria, validar CPF/CNPJ, domínio (lista de valores permitidos) e integridade cruzada (valor precisa existir em outra tabela tratada)
	- Registros aprovados gravados na Zona Tratada
	- Registros reprovados enviados à quarentena com o tipo de erro e o motivo
	- Regras aplicadas no processamento do CAR que já existe
	- Nenhuma geometria corrigida sem registro da correção
	- Endpoints documentados no Swagger

- **🏃‍ DoR (Definition of Ready):**

	- Lista de regras e de tipos de erro definida
	- Tabelas de domínio definidas (ex.: situação do imóvel AT, PE, CA, SU)
	- Protótipo da tela de mapeamento
	- Arquivo de exemplo com erros conhecidos

---

### **US07 - Tratamento da quarentena**

> **Como Operador de Dados, quero consultar e tratar os registros rejeitados na validação para que eu possa corrigir, aprovar ou descartar cada inconsistência com justificativa registrada.**

- **Prioridade:** Alta
    
- **Estimativa:** 5
    
- **Status:** 📅
    
- **DoD (Critérios de Sucesso):**

	- Tela da quarentena com totais por status e filtros (tipo de erro, fonte e status)
	- Detalhe do registro com o valor recebido, o motivo da rejeição e o dado original
	- Geometria exibida no mapa, com o ponto do problema destacado
	- Ações: iniciar análise, corrigir manualmente, revalidar e aprovar, descartar com justificativa
	- Registro aprovado gravado na Zona Tratada
	- Toda ação registrada com data e justificativa
	- Endpoints documentados no Swagger

- **🏃‍ DoR (Definition of Ready):**
    
	- Protótipo da tela de quarentena
	- Registros de exemplo na quarentena (dados de demonstração)
	- Status da análise definidos (Pendente, Em análise, Corrigido, Descartado)
 
---

### **US08 - Indicadores de Reserva Legal (IRL) e Focos de Calor (IFC)**

> **Como Analista, quero consultar os indicadores de Reserva Legal e de focos de calor de cada imóvel rural para que eu possa avaliar sua conformidade ambiental.**

- **Prioridade:** Alta
    
- **Estimativa:** 5
    
- **Status:** 📅
    
- **DoD (Critérios de Sucesso):**

	- IRL calculado por imóvel: área de Reserva Legal ÷ área do imóvel, comparada ao mínimo de 20%
	- IFC calculado por imóvel: focos de calor dentro do imóvel a cada 1.000 hectares
	- Cálculo feito no banco Oracle (PL/SQL)
	- Cada indicador guarda a versão dos dados e a regra de cálculo usadas
	- Indicadores exibidos no detalhe do imóvel no mapa
	- Endpoint de consulta documentado no Swagger
	- Memória de cálculo documentada

- **🏃‍ DoR (Definition of Ready):**
    
	- Fórmulas dos dois indicadores definidas
	- Arquivo de Reserva Legal do CAR e arquivo de focos de calor do INPE (Paraná) disponíveis
	- Protótipo do card de indicadores

---

### **US11 - Histórico de versões e rastreabilidade** *(entrega extra)*

> **Como Auditor, quero consultar o histórico das versões dos dados e indicadores e sua origem para que eu possa verificar como os resultados foram produzidos e comparar diferentes versões.**

- **Prioridade:** Média

- **Estimativa:** 8

- **Status:** 📅

- **DoD (Critérios de Sucesso):**

	- Histórico do imóvel guardado a cada carga (a versão anterior não é apagada)
	- Lista de versões de cada conjunto de dados, com data, arquivo de origem, hash e quantidade de registros
	- Comparação entre duas versões de um imóvel, mostrando o que mudou
	- Rastreio de um resultado até a fonte, o arquivo (hash), a execução e a regra usada
	- Versões já geradas não podem ser alteradas
	- Endpoints documentados no Swagger

- **🏃‍ DoR (Definition of Ready):**

	- Protótipo da tela de versões e da comparação
	- Pelo menos duas cargas do mesmo conjunto disponíveis (podem ser dados de demonstração)
	- Campos exibidos na comparação definidos

---

## 🏃‍ DoR - Definition of Ready (Sprint 2)

Estes critérios garantem que o time tem todos os insumos necessários para iniciar o desenvolvimento desta Sprint:

- **Clareza:** User Stories definidas com objetivos de negócio e critérios de aceitação básicos estabelecidos.
    
- **Fontes de dados:** Links das fontes públicas e arquivos de exemplo (CAR, Reserva Legal e focos de calor) disponíveis.
    
- **Dados de demonstração:** Registros de exemplo de execuções e de quarentena carregados no banco de desenvolvimento.

- **Regras:** Regras de tratamento, tipos de erro, tabelas de domínio e fórmulas dos indicadores definidas.
    
- **Modelagem:** Estrutura do banco definida para fontes, mapeamento de colunas, quarentena e indicadores.
    
- **Ambiente:** Ambiente de desenvolvimento configurado e máquina do Airflow disponível.
    
- **Design:** Protótipo das telas de fontes, execuções, mapeamento, quarentena, indicadores e versões definido.


---

## 🏆 Critérios de Conclusão da Sprint

Para o fechamento da Sprint 2, a equipe deve atender aos seguintes requisitos gerais:
* Pull Requests revisados e aprovados seguindo o fluxo do **GitHub Flow**.
* Integração contínua: Código consolidado na branch `main` sem quebras de build.
* Documentação técnica: README da sprint atualizado com o status final das entregas.


---

# BurndownChart da Sprint
_Disponível ao final da Sprint._


---
 # 🎥 Demonstração da aplicação

 > Vídeo da demonstração da Sprint: _em produção_ 🎬

---
