# Manual de usuário - GeoRural 

**Equipe Atlaz** · Projeto Fatec para a Visiona — Tecnologia Espacial
São José dos Campos - SP · 2º semestre de 2026

Integrantes: Gabriel Rocha · Leandro Campos · Manuela Brito Migri · Gabriel Valente ·
Gabriel Nunes · Rodolfo Corbalan


## Sumário

1. [Agradecimentos](#agradecimentos)
2. [Apresentação](#apresentação)
3. [Requisitos de sistema](#requisitos-de-sistema)
   - [Funcionais](#funcionais)
   - [Não funcionais](#não-funcionais)
4. [Como instalar e rodar](#como-instalar-e-rodar)
5. [Como usar](#como-usar)
   - [Ingestão de dados](#ingestão-de-dados)
   - [Consulta territorial](#consulta-territorial)


## Agradecimentos

"Agradecemos à Visiona — Tecnologia Espacial por proporcionar a oportunidade de desenvolver este
sistema web. Como grupo, nos comprometemos a simplificar o seu dia a dia e otimizar a sua rotina de
trabalho."

**Gabriel Rocha** — Agradeço à Visiona pela oportunidade de desenvolver este projeto e
principalmente à minha equipe pela parceria e pelo trabalho conjunto durante todo o processo.

**Leandro Campos** — _a escrever_

**Manuela Brito Migri** — Agradeço aos meus colegas de API pelo apoio e companheirismo ao decorrer desse trabalho. Grandes conquistas não são feitas por mentes isoladas, mas sim por equipes que
compartilham a mesma visão com respeito e cumplicidade.

**Gabriel Valente** — _a escrever_

**Gabriel Nunes** — Grato pelos companheiros da Visiona por colaborar com nosso progresso de
estudos, e também aos meus colegas de equipe por somar com a produtividade e atender ao problema de
nossa empresa parceira.

**Rodolfo Corbalan** — _a escrever_


## Apresentação

A Visiona atua em projetos que usam informações territoriais, ambientais e geoespaciais para apoiar
análise, planejamento e tomada de decisão. Nesses projetos, os dados sobre imóveis rurais costumam vir de várias fontes, públicas e privadas, e incluem registros cadastrais e informações geográficas produzidas ao longo do tempo. Como essas fontes têm formatos variados, níveis de qualidade diferentes e são atualizadas com frequência, fica difícil rastrear e auditar os dados. Muitas vezes não se consegue saber de qual fonte, versão e processamento uma informação exibida veio, e isso prejudica a transparência e a confiabilidade das informações.

Para resolver esse problema, este projeto propõe o **GeoRural**, uma plataforma web com back-end em **Spring Boot (Java)** e front-end em **Vue.js**. A solução reúne em um banco de dados relacional
**Oracle** — com suporte a dados espaciais via Hibernate Spatial e JTS — o catálogo, a validação e a
rastreabilidade dos dados territoriais. Entre seus recursos estão: gestão de fontes de dados e de
lotes de importação com prova de integridade (hash SHA-256), processamento e validação dos dados do Cadastro Ambiental Rural (CAR) antes de disponibilizá-los, rastreabilidade entre cada imóvel gravado e a versão/execução que o produziu, e visualização espacial interativa dos imóveis rurais do Paraná em mapa.


## Requisitos de sistema

### Funcionais

#### Cadastro de fontes e importação de dados

> Como Operador de Dados, quero cadastrar fontes de dados e importar seus arquivos para que os
> dados recebidos sejam armazenados de forma íntegra e possam ser utilizados pela aplicação.

- O sistema permite cadastrar uma fonte de dados, informando nome, sigla (até 12 caracteres), órgão responsável, formato do arquivo (CSV, GeoJSON, SHP, XLSX ou JSON) e periodicidade de atualização (diária, semanal, mensal, anual ou eventual).
- O sistema impede o cadastro de duas fontes com a mesma sigla.
- O sistema permite consultar as fontes já cadastradas, com busca por nome, sigla ou órgão.
- O sistema permite importar um arquivo para uma fonte cadastrada, nos formatos `.csv`, `.zip`,`.geojson`, `.json`, `.shp`, `.xlsx` ou `.txt`, com até 500 MB.
- O arquivo original é armazenado sem alterações (zona bruta), junto com um hash SHA-256 de
  integridade e a data/hora do recebimento — essa cópia nunca é sobrescrita.
- O sistema informa o status de cada arquivo importado: **Recebido**, **Processando**,**Processado** ou **Rejeitado**.

#### Disponibilização dos dados territoriais do CAR

> Como Operador de Dados, quero disponibilizar os dados territoriais do CAR após seu processamento inicial para que as informações dos imóveis rurais possam ser consultadas pela aplicação.

- O sistema processa o shapefile do CAR (enviado como `.zip`) automaticamente, assim que o upload termina, sem precisar de outra ação do Operador.
- O sistema valida cada imóvel do arquivo — código vazio ou duplicado, geometria ausente ou
  inválida. Imóveis reprovados vão para uma quarentena, com o motivo registrado; os demais são
  gravados.
- O sistema converte a geometria de cada imóvel para o formato espacial do banco de dados,
  corrigindo o sentido do contorno do polígono quando necessário.
- O sistema mantém o vínculo entre cada imóvel gravado e a versão/execução do processamento que o
  produziu.
- O sistema atualiza o status do arquivo ao final do processamento: **Processado** (com a
  quantidade de imóveis lidos, válidos e inválidos) ou **Rejeitado** (com a mensagem de erro).
- O sistema permite reprocessar manualmente um arquivo que ficou **Recebido** ou foi **Rejeitado**.
- Somente os imóveis validados com sucesso ficam disponíveis para consulta.

#### Consulta de imóveis rurais via API

> Como Analista, quero consultar os imóveis rurais por meio de uma API para que suas informações
> territoriais possam ser consumidas pela aplicação.

- O sistema disponibiliza uma API para listar os imóveis rurais de forma paginada (até 500 itens
  por página).
- O sistema permite consultar um imóvel específico pelo código do CAR, retornando sua geometria em
  formato GeoJSON.
- O sistema permite filtrar os imóveis por município (nome) ou por código do imóvel.
- Para cada imóvel na listagem, o sistema retorna código, município, área (em hectares) e situação
  cadastral no CAR (Ativo, Cancelado, Pendente ou Suspenso) — sem a geometria, para não sobrecarregar
  a listagem.

#### Visualização em mapa e tabela

> Como Analista, quero visualizar os imóveis rurais e suas divisões territoriais em um mapa para
> que eu possa localizar e analisar espacialmente os imóveis do Paraná.

- O sistema exibe os imóveis rurais do Paraná em um mapa interativo, com zoom e navegação.
- Abaixo de um certo nível de zoom, o mapa não carrega imóveis — evita sobrecarregar o navegador com
  o estado inteiro de uma vez — e avisa o usuário para aproximar o zoom.
- O sistema exibe o contorno do município selecionado no filtro, e mantém a navegação do mapa
  restrita à área do Paraná.
- O sistema exibe as informações de um imóvel (código, município, área, situação) ao selecioná-lo
  no mapa ou na tabela — a seleção é sincronizada entre os dois.

### Não funcionais

**Tecnologia e arquitetura**
- Back-end em Java 17 com Spring Boot; front-end em Vue 3.
- Banco de dados relacional Oracle; dados geoespaciais em colunas espaciais, acessadas via
  Hibernate Spatial e JTS.
- API no padrão REST, trocando dados em JSON; geometrias no formato GeoJSON.
- Arquivos originais armazenados em Object Storage (OCI), organizados por zona (bruta, tratada,
  publicada, quarentena).

**Integridade e rastreabilidade dos dados**
- A importação e o processamento de um lote são transacionais: se ocorrer erro, nenhum dado
  parcial daquele lote é persistido.
- Cada imóvel gravado mantém o vínculo com a versão do conjunto de dados e a execução que o
  produziu.
- O histórico de arquivos importados e das execuções de processamento não é apagado.
- As geometrias são armazenadas no sistema de referência **EPSG:4326 (WGS84)**. As fontes originais
  (CAR, IBGE) usam SIRGAS 2000; a diferença entre os dois é menor que 1 metro, então é ignorada de
  propósito — decisão registrada na documentação técnica do projeto.

**Desempenho**
- As listagens de imóveis são sempre paginadas e nunca retornam a geometria de todos os registros
  de uma vez.
- A consulta de imóveis no mapa é limitada à área visível na tela e a uma quantidade máxima de
  imóveis por vez, com aviso ao usuário quando há mais imóveis do que o exibido.
- O limite de tamanho de arquivo para importação é de 500 MB.

**Usabilidade e confiabilidade**
- As mensagens de erro retornadas pela API seguem um formato padronizado, com o código HTTP
  apropriado e uma descrição do problema em português.
- O andamento do processamento de um arquivo é atualizado automaticamente na tela, sem precisar
  recarregar a página.

**Manutenibilidade**
- O código é versionado no GitHub, com o fluxo de branches `feature → dev → main` e revisão por
  Pull Request.
- O back-end segue arquitetura em camadas (`controller` → `service` → `repository`).

## Como instalar e rodar

O GeoRural é formado por dois projetos: o **back-end** (a API) e o **front-end** (a tela). Os dois
precisam estar rodando para usar a aplicação por completo.

### Back-end

**Pré-requisitos:** Java 17, Docker (para o banco Oracle local) e uma credencial válida da Oracle
Cloud (OCI) para o Object Storage.

1. Clone o repositório `Atlaz4-BackEnd`.
2. Crie o arquivo `.env` na raiz do projeto (a partir do `.env.example`), com `OCI_NAMESPACE`,
   `OCI_BUCKET`, `DB_USERNAME` e `DB_PASSWORD`.
3. Suba o banco de dados local: `docker compose up -d` (a primeira subida demora alguns minutos).
4. Configure a credencial da OCI em `~/.oci/config`, no perfil `DEFAULT`. Sem esse arquivo a
   aplicação não inicia.
5. Rode a aplicação: `mvnw.cmd spring-boot:run` (Windows) ou `./mvnw spring-boot:run`. As tabelas do
   banco são criadas automaticamente na primeira subida.
6. A API fica disponível em `http://localhost:8080/api/v1`.

### Front-end

**Pré-requisitos:** Node.js 18 ou mais recente, npm.

1. Clone o repositório `Atlaz4-FrontEnd`.
2. Instale as dependências: `npm install`.
3. Copie o arquivo `.env.example` para `.env.development`.
4. **Para testar só a tela de Ingestão de dados**, sem precisar do back-end real: `npm run start`
   (sobe um servidor de exemplo e a aplicação juntos).
5. **Para usar a aplicação completa** — incluindo a tela de Consulta territorial, que só funciona
   com o back-end real — edite o `.env.development` e defina
   `VITE_API_URL=http://localhost:8080/api/v1`, com o back-end já rodando; depois rode `npm run dev`.
6. Acesse `http://localhost:5173`.


## Como usar

A aplicação tem duas telas, acessíveis pelo menu superior.

### Ingestão de dados

A tela usada pelo Operador de Dados para cadastrar fontes e importar arquivos. É dividida em uma
trilha de etapas no topo, a lista de fontes à esquerda e a importação de arquivo à direita.

A trilha de etapas mostra o caminho que o dado percorre: **Cadastro & Importação** (a etapa desta
tela, sempre acessível), **Validação** e **Padronização** (essas duas aparecem esmaecidas, sem
link — são as próximas etapas do pipeline, ainda não implementadas como tela própria; a validação
já acontece durante o processamento, só não tem uma tela dedicada a ela).

<img width="1600" height="813" alt="tela de cadastro" src="https://github.com/user-attachments/assets/c35b35e3-b252-414f-9c6f-e43404e82ed2" />
<img width="1600" height="818" alt="WhatsApp Image 2026-09-27 at 19 31 01" src="https://github.com/user-attachments/assets/df3a4f5b-7c40-439b-b177-ec69612788d7" />


**Passo a passo:**

1. **Cadastrar uma fonte** (se ainda não existir): clique em "Nova fonte" e informe nome, sigla,
   órgão, formato e periodicidade.
2. **Selecionar a fonte** na lista à esquerda.
3. **Enviar o arquivo**: arraste o arquivo para a área de importação, ou clique para selecioná-lo,
   e inicie a importação. Uma barra mostra o progresso do envio.
4. **Processamento automático**: se o arquivo for um `.zip` da fonte do CAR, o processamento começa
   sozinho assim que o envio termina — não é preciso clicar em nada.
5. **Acompanhar o status**: a lista de arquivos recebidos mostra o status de cada um — Recebido,
   Processando, Processado ou Rejeitado — e se atualiza automaticamente enquanto algum arquivo
   estiver sendo processado.
6. **Reprocessar**, se necessário: arquivos com status Recebido ou Rejeitado (do CAR, em `.zip`)
   mostram um botão "Processar" para tentar de novo. Ao concluir, aparece um resumo (quantidade de
   imóveis lidos, válidos e inválidos) ou a mensagem de erro, se tiver sido rejeitado.

### Consulta territorial

Tela usada pelo Analista para consultar e visualizar os imóveis rurais já processados. Mostra um
filtro no topo, o mapa à esquerda e a tabela de imóveis à direita.

**Passo a passo:**

1. **Filtrar** (opcional): escolha um município na lista, e/ou digite parte do código de um
   imóvel. Os dois filtros podem ser usados juntos.
2. **Consultar na tabela**: os imóveis que atendem ao filtro aparecem paginados, com código,
   município, situação cadastral e área. Use os botões de página para navegar.
3. **Consultar no mapa**: o mapa começa centrado no Paraná. A partir de um certo nível de zoom, os
   imóveis da área visível aparecem como polígonos; abaixo desse zoom, uma mensagem pede para
   aproximar. O mapa não sai dos limites do Paraná.
4. **Selecionar um imóvel**: clique numa linha da tabela ou num imóvel no mapa — a seleção é
   sincronizada entre os dois, e um balão mostra código, município, área e situação. Ao selecionar
   um município no filtro, o mapa desenha o contorno dele.
