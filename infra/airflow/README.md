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
| `dags/` | As DAGs (`teste_conexoes`, `varredor_bruta`, `processar_arquivo`) |
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
5. Abra http://localhost:8080 (sem login em dev) e rode a DAG `teste_conexoes`:
   as duas tarefas verdes = Oracle e bucket funcionando
6. Ative a DAG `varredor_bruta` e, no `.env` do **back-end**, use `AIRFLOW_HABILITADO=true`.
   Daí em diante, todo upload do CAR (.zip) e todo clique em "Processar" fica com o Airflow:
   o varredor pega o arquivo em ate 2 minutos e dispara o `processar_arquivo`.

Testes do pipeline (dentro da imagem, que ja tem as bibliotecas):
```bash
docker compose -f docker-compose.local.yaml --env-file .env.local run --rm \
  -v ./tests:/opt/airflow/tests airflow bash -c "pip install -q pytest && pytest -q /opt/airflow/tests"
```

### Como o processamento funciona

```
upload ──> arquivo_bruto (RECEBIDO) ──> varredor_bruta (a cada 2 min)
                                           │ reserva: RECEBIDO → PROCESSANDO
                                           ▼
                                     processar_arquivo
                                       preparar:  abre a execucao
                                       processar: baixa o .zip, le em lotes,
                                                  valida, grava imovel_rural e
                                                  registro_quarentena, conclui
                                           │
                                           ▼
                             arquivo_bruto PROCESSADO | REJEITADO
```

* Faz o mesmo que o processamento Java (`ProcessamentoCarServiceImpl`), com duas diferencas:
  geometria invalida vai para a **quarentena** (o Java corrigia em silencio) e a geometria
  e **reprojetada** para 4326 de verdade (o Java so marcava como 4326).
* Le o shapefile em lotes de `GEORURAL_TAMANHO_LOTE` registros: a memoria depende do lote,
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
