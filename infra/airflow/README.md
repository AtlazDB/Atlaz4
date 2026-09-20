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
