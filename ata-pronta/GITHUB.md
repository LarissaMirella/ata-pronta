# Como publicar o projeto no seu GitHub (passo a passo)

O GitHub é o "Google Drive dos programadores": guarda seu projeto e permite que recrutadores vejam. Há dois caminhos. **Se é a sua primeira vez, use o Caminho A (GitHub Desktop).**

## Antes de tudo: proteja sua chave

- A chave de API fica no arquivo `.env`. O `.gitignore` do projeto já impede que ele seja enviado.
- Mesmo assim, **confira** antes de publicar (os passos abaixo mostram onde). Se uma chave for enviada por engano, **apagar o arquivo não adianta**: vá ao site do provedor, **revogue a chave** e crie outra.

## Passo 0: crie sua conta
Acesse **github.com** → *Sign up*. Escolha um nome de usuário profissional (ele aparece no seu link, ex.: github.com/seunome).

---

## Caminho A: GitHub Desktop (mais fácil, sem comandos)

1. Baixe e instale o **GitHub Desktop** em **desktop.github.com** e entre com sua conta.
2. Menu **File → Add local repository...** e escolha a pasta `ata-pronta`.
3. Vai aparecer um aviso de que não é um repositório. Clique em **"create a repository"**, confirme o nome (`ata-pronta`), escreva uma descrição curta (ex.: *"Transforma anotações de reunião em ata, tarefas e e-mail usando IA"*) e clique em **Create repository**.
4. Na lista **Changes** (à esquerda), confira: **não deve aparecer `.env`**, apenas `.env.example`. Se aparecer, pare e peça ajuda.
5. Em *Summary* (embaixo à esquerda), escreva `Primeira versão do Ata Pronta` e clique em **Commit to main**.
6. Clique em **Publish repository** (no alto). Desmarque *"Keep this code private"* para o repositório ficar público (recrutadores precisam conseguir ver) e clique em **Publish repository**.
7. Pronto! Clique em **View on GitHub** para ver sua página.

**Para atualizar depois:** mudou algo no projeto? Abra o GitHub Desktop, escreva um resumo da mudança, clique em **Commit to main** e depois em **Push origin**.

---

## Caminho B: pelo terminal

1. Instale o **Git** em **git-scm.com** (pode aceitar as opções padrão).
2. No site do GitHub, clique em **+ → New repository**. Nome: `ata-pronta`. Deixe **Public**. **Não marque** "Add a README", ".gitignore" nem "license" (o projeto já tem). Clique em **Create repository**.
3. Abra o terminal **dentro da pasta `ata-pronta`** e digite, um por vez (troque pelos seus dados):

```
git config --global user.name "Seu Nome"
git config --global user.email "seu-email-do-github@exemplo.com"
git init
git add .
git status
```
4. No resultado do `git status`, **confira que `.env` não aparece** (só `.env.example`).
5. Continue:
```
git commit -m "Primeira versão do Ata Pronta"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/ata-pronta.git
git push -u origin main
```
6. Uma janela do navegador pode abrir pedindo para você entrar no GitHub: autorize. Se pedir "senha" no terminal, o GitHub não aceita a senha da conta: use um *Personal Access Token* (GitHub → Settings → Developer settings → Personal access tokens) ou, mais simples, use o Caminho A.

**Para atualizar depois:**
```
git add .
git commit -m "Descreva o que mudou"
git push
```

---

## Deixe o repositório com cara profissional

1. **Descrição e tópicos:** na página do repositório, clique na engrenagem ao lado de *About* e preencha a descrição e os tópicos (ex.: `python`, `ai`, `llm`, `prompt-engineering`, `automation`, `productivity`).
2. **Print:** rode `python web.py`, gere uma ata, tire um print e salve como `docs/print.png` (crie a pasta `docs`). No `README.md`, troque o comentário do print por `![Print](docs/print.png)`.
3. **Commits claros e em português:** "Adiciona botão de copiar e-mail" é melhor que "mudanças".
4. **Fixe no perfil:** em *github.com/seunome*, clique em *Customize your pins* e escolha este repositório.
5. **README sincero:** a última linha do README diz como o projeto foi feito. Escreva a verdade (por exemplo, quais partes a IA ajudou e o que você mudou).
6. **Coloque o link** do repositório no currículo e no LinkedIn.

## Checklist final
- [ ] O repositório está **público** e abre sem login.
- [ ] Não há nenhuma chave ou senha no código (nem no `.env` enviado).
- [ ] O README abre bonito e o passo a passo funciona numa pasta nova.
- [ ] Rodei o projeto **com uma chave de IA de verdade** pelo menos uma vez.
- [ ] Consigo explicar com minhas palavras o que cada arquivo faz.
