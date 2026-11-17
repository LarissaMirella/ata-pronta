# Guia para iniciantes: rodando o Ata Pronta do zero

Você não precisa entender programação para seguir. Vá devagar, um passo de cada vez.
Os comandos abaixo são digitados no **terminal** (uma janela preta onde você escreve comandos).

## Parte 1: preparar o computador

### 1. Instale o Python
- Acesse **python.org** → *Downloads* e baixe a versão mais recente.
- **Windows:** na primeira tela do instalador, marque **"Add python.exe to PATH"** antes de clicar em *Install Now*. (Esse é o erro mais comum.)
- Para conferir, abra o terminal e digite: `python --version`. Se aparecer um número (ex.: `Python 3.12.1`), está certo.
  - Se der "não é reconhecido" no Windows, tente `py --version`. Se funcionar, use `py` no lugar de `python` em todos os comandos.
  - No Mac/Linux, pode ser `python3`.

### 2. Abra o terminal dentro da pasta do projeto
- Extraia o arquivo `.zip` do projeto. Você terá uma pasta `ata-pronta`.
- **Windows:** abra a pasta no Explorador, clique na barra de endereço (onde aparece o caminho), digite `cmd` e aperte Enter.
- **Mac:** clique com o botão direito na pasta → *Novo Terminal na Pasta* (ou abra o Terminal e digite `cd ` e arraste a pasta para a janela).

## Parte 2: rodar em modo demonstração (sem IA, sem chave)

No terminal, digite:

```
python ata.py exemplos/reuniao_projeto.txt
```

Você verá a ata organizada na tela, e um arquivo novo aparece na pasta `resultados/`. Pronto, já está funcionando!

Agora a versão com página web:

```
python web.py
```

Abra o navegador em **http://127.0.0.1:8000**, cole um texto e clique em *Gerar ata*. Para parar, volte ao terminal e aperte `Ctrl + C`.

Teste com o seu próprio texto: crie um arquivo `teste.txt` (Bloco de Notas), cole anotações de uma reunião sua e rode `python ata.py teste.txt`.

## Parte 3: ligar uma IA de verdade

A "chave de API" é uma senha que permite ao seu programa conversar com a IA. **Ela é secreta: não mostre a ninguém e nunca envie ao GitHub.**
Escolha UM provedor:

**Opção A: Google Gemini**
1. Acesse **aistudio.google.com** e entre com sua conta Google.
2. Procure *Get API key* e crie uma chave.
3. O Google costuma oferecer um nível gratuito com limites, mas as condições mudam: leia o que aparece na tela.

**Opção B: Anthropic (Claude)**
1. Acesse **console.anthropic.com**, crie uma conta e vá em *API Keys*.
2. A API é paga por uso (precisa adicionar crédito) e **é separada** da assinatura do chat Claude.ai. Confira os preços antes.

Depois de copiar a chave:
1. Na pasta do projeto, copie o arquivo de exemplo:
   - Windows: `copy .env.example .env`
   - Mac/Linux: `cp .env.example .env`
2. Abra o arquivo `.env` com o Bloco de Notas ou o VS Code e cole a chave logo depois do `=`, **sem espaços e sem aspas**:
   ```
   GEMINI_API_KEY=cole_sua_chave_aqui
   ```
3. Salve e rode de novo: `python ata.py exemplos/grupo_de_estudos.txt`.
   No fim da ata aparece o modo usado. Se disser **"IA: Gemini"** (ou Claude), funcionou!

Compare o resultado com o do modo demonstração e anote as diferenças: isso é material excelente para contar na entrevista.

## Parte 4: problemas comuns

| Mensagem | O que fazer |
|---|---|
| `python não é reconhecido` | Reinstale o Python marcando "Add to PATH", ou use `py`. |
| `Não encontrei o arquivo` | Você não está na pasta certa, ou escreveu o nome errado. |
| `A chave de API foi recusada` | Copie a chave de novo, sem espaços, sem aspas, na linha certa do `.env`. |
| `O limite de uso da IA foi atingido` | Espere alguns minutos ou confira seu plano/crédito. |
| Continua em "Modo demonstração" | O arquivo precisa se chamar exatamente `.env` (não `.env.txt`) e estar na mesma pasta do `ata.py`. |

**Truque de ouro:** quando aparecer um erro que você não entende, copie a mensagem inteira, cole no ChatGPT, Claude ou Gemini e escreva: *"Sou iniciante. Estou rodando um projeto em Python no Windows e apareceu este erro. Explique em palavras simples o que significa e como resolver, passo a passo."*

## Parte 5: entenda o que você tem (e evolua com ajuda de IA)

Para aprender o código, abra o `ata.py` e peça a uma IA:
> "Sou iniciante. Explique este arquivo por blocos, em português simples, dizendo o que cada função faz e por que existe."

Depois faça pequenas mudanças, uma de cada vez:
1. **Mude o prompt.** Edite o `prompt.txt` (por exemplo, peça resumo em até 2 frases) e rode de novo. Veja o que muda. Isso é *prompt engineering* na prática.
2. **Peça uma melhoria à IA.** Exemplo de pedido: *"Neste projeto, adicione na página web um botão 'Copiar e-mail'. Mostre só o trecho que muda e em qual arquivo colar."*
3. **Rode os testes** depois de cada mudança (`pip install pytest` e depois `python -m pytest`). Se algum falhar, cole o erro na IA.
