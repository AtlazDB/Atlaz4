# Ambiente do Airflow

Pipeline de ingestao do data lake. Roda numa VM Ampere A1 (**aarch64**) da OCI,
com Airflow 3.3.1 em `docker compose`, dentro de `~/airflow`.

## Arquivos

| Arquivo | O que e |
|---|---|
| `Dockerfile` | Imagem propria: Airflow 3.3.1 + bibliotecas do pipeline |
| `.env.example` | Modelo do `.env`. O `.env` real fica so na VM |
| `docker-compose.yaml` | **Ainda nao versionado** — ver "Pendencias" |
| `Caddyfile` | **Ainda nao versionado** — proxy reverso que publica a UI em HTTPS |
| `docker-compose.local.yaml` | Airflow de **desenvolvimento** no seu PC (um container, `airflow standalone`) |
| `.env.local.example` | Modelo do `.env.local` do desenvolvimento |
| `dags/` | As DAGs (`teste_conexoes`, `coleta_fontes`, `coletar_fonte`, `varredor_bruta`, `processar_arquivo`) |
| `dags/georural/` | Codigo do pipeline usado pelas DAGs (testavel sem Airflow) |
| `tests/` | Testes do pipeline (pytest) |

## Rodar no seu computador (desenvolvimento)

Precisa do Docker Desktop. O Airflow roda num container e usa o **Oracle local** do
back-end e o **bucket real** da OCI (com a sua chave da API, a mesma do back-end).

1. Suba o Oracle local: `cd Atlaz4-BackEnd && docker compose up -d`
2. Rode o back-end uma vez (`mvnw spring-boot:run`) para o Flyway criar as tabelas
3. Aqui em `infra/airflow`: `cp .env.local.example .env.local` e preencha
4. Suba o Airflow:
   ```bash
   docker compose -f docker-compose.local.yaml --env-file .env.local up --build
   ```
5. Abra http://localhost:8088 (sem login em dev; a 8080 fica para o back-end) e rode a DAG `teste_conexoes`:
   as duas tarefas verdes = Oracle e bucket funcionando
6. Ative as DAGs `varredor_bruta`, `processar_arquivo`, `coleta_fontes` e `coletar_fonte` e, no
   `.env` do **back-end**, use `AIRFLOW_HABILITADO=true`. Daí em diante, todo upload, todo clique em
   "Processar" e todo "Executar" de fonte por link fica com o Airflow.
7. Para a demonstração com as fontes do DataGIS (municípios, focos, Reserva Legal e CAR pelo WFS),
   rode uma vez o `Atlaz4-BackEnd/db/seed-demo/fontes_datagis.sql`: ele cadastra as 4 fontes por
   link com o mapeamento.

Testes do pipeline (dentro da imagem, que ja tem as bibliotecas):
```bash
docker compose -f docker-compose.local.yaml --env-file .env.local run --rm \
  -v ./tests:/opt/airflow/tests airflow bash -c "pip install -q pytest && pytest -q /opt/airflow/tests"
```

### Como a coleta por link funciona

```
"Executar" na tela ──> fonte.coleta_solicitada_em ──> coleta_fontes (a cada 2 min)
                                                         │ reserva o pedido
                                                         ▼
                                                   coletar_fonte (uma por vez)
                                                     pergunta o total, pagina o servico
                                                     (ArcGIS ou WFS) em ordem fixa, confere
                                                     coletado = total, zip de paginas GeoJSON
                                                         │ mesmo hash da ultima? "sem mudanca"
                                                         ▼
                                     bucket bruta/<SIGLA>/... + arquivo_bruto RECEBIDO (COLETA)
```

* `georural/coleta.py`. Pagina ArcGIS por `resultOffset`/`resultRecordCount` ordenado pelo
  objectid, e WFS por `startIndex`/`count` ordenado pela coluna-chave do mapeamento.
* Faltou registro ou veio repetido entre paginas: a coleta **falha** ("vieram X de Y") em vez de
  gravar dado pela metade. HTTP 500 ou demora na pagina: ela e dividida pela metade (ate 50).
* O andamento e o resultado aparecem na tela da fonte (`fonte.ultima_coleta_mensagem`).

### Como o processamento funciona

```
upload/coleta ──> arquivo_bruto (RECEBIDO) ──> varredor_bruta (a cada 2 min)
                                                  │ reserva: RECEBIDO → PROCESSANDO
                                                  ▼
                                            processar_arquivo
                                              preparar:  abre a execucao
                                              processar: CAR (.zip da fonte CAR) ou generico
                                                  │
                                                  ▼
                       arquivo_bruto PROCESSADO | REJEITADO | AGUARDANDO_MAPEAMENTO
```

* **Caminho do CAR** (`car.py`): o shapefile de imoveis da fonte CAR, com as regras em Python.
  Faz o mesmo que o processamento Java (`ProcessamentoCarServiceImpl`), com duas diferencas:
  geometria invalida vai para a **quarentena** (o Java corrigia em silencio) e a geometria
  e **reprojetada** para 4326 de verdade (o Java so marcava como 4326).
* **Caminho generico** (`generico.py`): todo o resto, guiado pelo mapeamento da fonte. Registra
  as colunas que vieram (`fonte_coluna`; sem mapeamento o arquivo fica AGUARDANDO_MAPEAMENTO),
  aplica o desempate de codigo repetido quando o mapeamento tem `situacao`, grava a staging,
  roda `pkg_quality.validate` e grava Tratada e quarentena com `pkg_tratada.gravar_aprovados` /
  `gravar_reprovados`. No fim recalcula IRL/IFC quando o conjunto e deles.
* Le em lotes de `GEORURAL_TAMANHO_LOTE` registros: a memoria depende do lote,
  nao do tamanho do arquivo.
* Na VM troque `GEORURAL_OCI_AUTH=instance_principal` e aponte `GEORURAL_DB_*` para o Oracle
  da VM; o codigo e o mesmo.

## Como aplicar uma mudanca

Sempre de dentro de `~/airflow` na VM. Fora dela o compose responde
`no configuration file provided: not found`, e o erro vem enterrado embaixo de
varios avisos de `FERNET_KEY` — da pra achar que o comando funcionou.

```bash
cd ~/airflow
docker compose build      # nao reinicia nada
docker compose up -d      # aqui sim, ~1 min de indisponibilidade
```

Conferir que as bibliotecas subiram:

```bash
cd ~/airflow && docker compose exec airflow-scheduler \
  python -c "import geopandas,shapely,pyproj,pyogrio,requests,oci;print('ok',geopandas.__version__)"
```

## Armadilhas conhecidas

- **`fiona` nao instala nesta VM.** Sem wheel para Linux ARM em nenhuma versao.
  Use `pyogrio`, que ja vem junto do geopandas 1.x. Detalhes no `Dockerfile`.
- **O build regrava a tag local `apache/airflow:3.3.1`**, porque o compose declara
  `image:` e `build:` ao mesmo tempo. Um `docker pull` nessa tag apaga as
  bibliotecas e o ambiente quebra sem aviso.
- **A autenticacao com a OCI e por Instance Principal**, nao por chave em disco:
  dynamic group + policy na tenancy. Isso nao se recria copiando arquivo, e
  configuracao na OCI.

## Pendencias

- [ ] Versionar `docker-compose.yaml` e `Caddyfile`. Hoje eles existem so na VM:
      se ela morrer, o ambiente se perde. Antes de commitar o compose, trocar as
      senhas literais por variaveis lidas do `.env` — o repositorio e publico.
- [ ] `FERNET_KEY` esta vazia na VM. Enquanto estiver, nao guarde senha do Oracle
      numa Connection do Airflow.
- [ ] A UI esta publicada na internet com o login padrao do Airflow. Trocar a senha.
