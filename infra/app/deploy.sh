#!/usr/bin/env bash
# Atualiza o GeoRural DataHub na VM: baixa a versao mais nova do back e do front,
# gera as imagens e reinicia so o que mudou. Uso: ./deploy.sh
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "Falta o .env. Rode: cp .env.example .env  e preencha." >&2
    exit 1
fi

set -a
. ./.env
set +a

: "${BACK_BRANCH:=dev}"
: "${FRONT_BRANCH:=dev}"
: "${OCI_CONFIG_DIR:=$HOME/.oci}"
export OCI_CONFIG_DIR

for var in DB_ADMIN_PASSWORD DB_USERNAME DB_PASSWORD OCI_NAMESPACE OCI_BUCKET; do
    if [ -z "${!var:-}" ]; then
        echo "Variavel $var vazia no .env." >&2
        exit 1
    fi
done

if [ ! -f "$OCI_CONFIG_DIR/config" ]; then
    echo "Nao achei $OCI_CONFIG_DIR/config (o back precisa dele para o Object Storage)." >&2
    exit 1
fi

# src/ e so uma copia de trabalho do deploy: qualquer mudanca local la dentro e descartada.
atualizar() {
    local url=$1 pasta=$2 branch=$3
    if [ -d "$pasta/.git" ]; then
        git -C "$pasta" fetch --quiet origin "$branch"
        git -C "$pasta" checkout --quiet -B "$branch" "origin/$branch"
        git -C "$pasta" reset --quiet --hard "origin/$branch"
    else
        git clone --quiet --branch "$branch" "$url" "$pasta"
    fi
    echo "  $pasta @ $branch -> $(git -C "$pasta" log -1 --format='%h %s')"
}

echo "Baixando codigo..."
atualizar https://github.com/AtlazDB/Atlaz4-BackEnd.git src/backend "$BACK_BRANCH"
atualizar https://github.com/AtlazDB/Atlaz4-FrontEnd.git src/frontend "$FRONT_BRANCH"

echo "Gerando imagens (o site continua no ar)..."
docker compose build

echo "Subindo containers..."
docker compose up -d --remove-orphans

docker compose ps
echo
echo "Pronto. Logs do back: docker compose logs -f backend"
