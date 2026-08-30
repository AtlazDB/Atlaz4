# 🌳 Estratégia de Branches (GitHub Flow) <a id="estrategia-branches"></a>

  

Este projeto adota o modelo **GitHub Flow**, priorizando a simplicidade, integração contínua e entregas frequentes. A branch `main` representa sempre a versão mais estável e atual do sistema.

  

---

  

### 🛠️ Fluxo de Trabalho

  

- [ ] **1. Branch Principal (`main`)**

  - A branch `main` deve estar sempre estável e pronta para uso.

  - Nenhuma alteração é feita diretamente na `main`.


- [ ] **2. Branch Intermediaria (`dev`)**

- A branch `dev` é utilizada como ambiente intermediário de integração das funcionalidades.
- Todas as novas funcionalidades e correções devem ser integradas primeiro na `dev`.
- A branch `dev` pode conter funcionalidades em validação e não possui a mesma estabilidade da `main`.
- Após validação e aprovação, as alterações da `dev` são promovidas para a `main` via Pull Request

- [ ] **3. Branches de Desenvolvimento**

  - Novas funcionalidades ou correções devem ser desenvolvidas em **branches curtas**, criadas a partir da `dev`.

  - Padrão de nomenclatura obrigatório:

    - `feat/tag-user-storie`

    - `fix/tag-user-storie`

    - `refactor/tag-user-storie`

  

- [ ] **3. Pull Requests (PRs)**

  - Toda alteração deve ser integrada à `dev` por meio de um **Pull Request**.

  - O PR deve passar por revisão de código e aprovação de pelo menos um membro da equipe antes do merge.

  - A branch deve estar atualizada com a `dev` antes da integração final.
  
  ---

  

### 📌 Padrão de Commits

  

Para manter o histórico organizado e rastreável, utilizamos o padrão **Conventional Commits**:

| Tipo       | Descrição                  | Bagde                                                          |
| ---------- | -------------------------- | -------------------------------------------------------------- |
| `feat`     | Nova funcionalidade        | ![Feature](https://img.shields.io/badge/Tipo-Feature-green)    |
| `fix`      | Correção de bug            | ![Fix](https://img.shields.io/badge/Tipo-Fix-red)              |
| `docs`     | Mudanças na documentação   | ![Docs](https://img.shields.io/badge/Tipo-Docs-blue)           |
| `refactor` | Refatoração de código      | ![Refactor](https://img.shields.io/badge/Tipo-Refactor-orange) |
| `test`     | Adição/alteração de testes | ![Test](https://img.shields.io/badge/Tipo-Test-yellow)         |
|  `chore`   | Manutenção geral           | ![Chore](https://img.shields.io/badge/Tipo-Chore-lightgrey)    |

Então um commit é composto por: "**Tipo**(Referencia): **Descrição" 

**Exemplo de uso:** 
> `feat(US01): implementa login do técnico com JWT `
> `docs(#01): Adiciona manual de usuário`
