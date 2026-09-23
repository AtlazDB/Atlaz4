# Deploy da aplicacao

GeoRural DataHub (back + front + banco) em `docker compose`, na mesma VM Ampere A1
(**aarch64**) da OCI que roda o Airflow, dentro de `~/atlaz4-app`. O deploy e manual:
alguem do grupo entra na VM e roda `./deploy.sh`.

```
navegador ──> :8081 nginx (front) ──/api──> backend :8080 ──> oracle :1521
                                                 └──> Object Storage (zona bruta)
```

So a porta do front fica aberta para fora. Back e banco escutam apenas em `127.0.0.1`.

## Arquivos

| Arquivo | O que e |
|---|---|
| `docker-compose.yaml` | Os tres containers e o volume do banco |
| `backend.Dockerfile` | Build do Spring Boot com Java 17 |
| `frontend.Dockerfile` | Build do Vue + nginx |
| `nginx.conf` | Serve o front e repassa `/api` para o back |
| `deploy.sh` | Baixa o codigo, gera as imagens e sobe tudo |
| `.env.example` | Modelo do `.env`. O `.env` real fica so na VM |

O codigo do back e do front **nao** vem daqui: o `deploy.sh` clona os repositorios
em `src/` (fora do git) na branch definida no `.env`.

## Dar acesso a alguem do grupo

Cada pessoa gera uma chave SSH no proprio PC (`ssh-keygen -t ed25519`) e manda so a
parte **publica** (`~/.ssh/id_ed25519.pub`). Quem ja tem acesso adiciona na VM:

```bash
echo "ssh-ed25519 AAAA... nome-da-pessoa" >> ~/.ssh/authorized_keys
```

## Primeira vez (uma pessoa so)

**1. Liberar a porta do site.** Duas camadas, as duas sao necessarias:

- **OCI:** na subnet da VM, Security List → Add Ingress Rule → origem `0.0.0.0/0`,
  TCP, porta `8081`.
- **Firewall da VM:**
  ```bash
  # Oracle Linux
  sudo firewall-cmd --permanent --add-port=8081/tcp && sudo firewall-cmd --reload
  # Ubuntu (imagem da OCI vem com iptables fechado)
  sudo iptables -I INPUT 6 -p tcp --dport 8081 -j ACCEPT && sudo netfilter-persistent save
  ```

**2. Conferir memoria.** O Oracle Free usa ~2 GB. Com o Airflow junto, veja `free -h`
antes. Se sobrar pouco, aumente a VM (a A1 gratis vai ate 24 GB).

**3. Credencial da OCI.** O back usa `~/.oci/config` + chave API (perfil `DEFAULT`,
regiao `sa-saopaulo-1`). Precisa existir na VM, no usuario que roda o deploy:

```bash
ls ~/.oci          # config e o .pem
chmod 600 ~/.oci/*
```

Se o `config` veio de um PC Windows, corrija o `key_file`: `C:\Users\...\oci_api_key.pem`
nao existe na VM e o back nao sobe (`Could not find private key`). Use
`key_file=~/.oci/oci_api_key.pem`.

**4. Baixar e configurar:**

```bash
git clone https://github.com/AtlazDB/Atlaz4.git ~/atlaz4-repo
ln -s ~/atlaz4-repo/infra/app ~/atlaz4-app
cd ~/atlaz4-app
cp .env.example .env
nano .env          # senhas, OCI_NAMESPACE, OCI_BUCKET, IP publico
chmod 600 .env
chmod +x deploy.sh
```

**5. Subir:**

```bash
./deploy.sh
```

A primeira vez demora (baixa imagens, dependencias do Maven e do npm, e o Oracle cria
o banco). O back so inicia quando o banco fica saudavel. Acompanhe:

```bash
docker compose logs -f backend   # espere "Started GeoRuralApplication"
```

Pronto: `http://IP_PUBLICO_DA_VM:8081`.

## Atualizar (qualquer pessoa do grupo)

```bash
ssh usuario@IP_PUBLICO_DA_VM
cd ~/atlaz4-repo && git pull     # so se mudou algo em infra/app
cd ~/atlaz4-app && ./deploy.sh
```

O `build` roda com o site no ar. A indisponibilidade e so o reinicio do back
(~30 s). O banco nao reinicia se a imagem dele nao mudou.

## Comandos uteis

Sempre de dentro de `~/atlaz4-app`:

```bash
docker compose ps                  # o que esta rodando
docker compose logs -f backend     # logs do back
docker compose restart backend     # reinicia so o back
```

Acessar o banco pelo DBeaver/IntelliJ do seu PC (tunel SSH):

```bash
ssh -L 1521:localhost:1521 usuario@IP_PUBLICO_DA_VM
# conecte em localhost:1521/FREEPDB1 com DB_USERNAME / DB_PASSWORD
```

## Armadilhas conhecidas

- **Senhas do banco so valem na primeira subida.** Depois o Oracle ja criou os
  usuarios dentro do volume `oracle-data`; mudar o `.env` nao troca a senha.
- **`docker compose down -v` apaga o banco inteiro.** Use `down` sem `-v`.
- **Nao ha login na aplicacao.** Quem tiver o endereco pode cadastrar e apagar
  fontes. Nao divulgue o IP fora do grupo.
- **A VM usa Instance Principal, mas o back nao.** O Airflow autentica na OCI sem
  chave em disco; o back so sabe ler `~/.oci/config`. Por isso o passo 3.

## Pendencias

- [ ] Fazer o back aceitar Instance Principal (fallback quando nao houver
      `~/.oci/config`), para nao depender de chave de uma pessoa na VM.
- [ ] Publicar em HTTPS pelo Caddy que ja existe na VM (`reverse_proxy localhost:8081`).
- [ ] Backup do volume `oracle-data`.
