"""Ata Pronta: transforma anotações bagunçadas em resumo, decisões, tarefas e e-mail de follow-up.

Como funciona (em 4 passos):
  1. Você dá um texto (anotação de reunião, aula, assembleia...).
  2. O programa monta um "prompt": instruções claras + o seu texto (veja o arquivo prompt.txt).
  3. Envia para uma IA (Claude ou Gemini). Sem chave de API, usa o MODO DEMONSTRAÇÃO (sem IA).
  4. Confere se a resposta veio no formato certo e mostra o resultado organizado.

Uso no terminal:
    python ata.py exemplos/reuniao_projeto.txt
    python ata.py minha_anotacao.txt --tom formal
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
LIMITE_CARACTERES = 20000
NAO_INFORMADO = "não informado"
ROTULO_MODO = {
    "claude": "IA: Claude",
    "gemini": "IA: Gemini",
    "demo": "Modo demonstração (sem IA, regras simples)",
}


# ---------------------------------------------------------------- configuração
def carregar_env():
    """Lê o arquivo .env (onde ficam suas chaves secretas) e coloca nas variáveis de ambiente."""
    arquivo = PASTA / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            chave, _, valor = linha.partition("=")
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def qual_ia():
    """Decide qual IA usar: 'claude', 'gemini' ou 'demo' (sem chave)."""
    carregar_env()
    if os.getenv("ATA_MODO", "").lower() == "demo":
        return "demo"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return "demo"


# ---------------------------------------------------------------- prompt
def montar_prompt(texto, tom):
    """Junta as instruções (prompt.txt) com o texto do usuário."""
    modelo = (PASTA / "prompt.txt").read_text(encoding="utf-8")
    # Remove tags do texto do usuário para ele não conseguir "fugir" da área de dados.
    texto_seguro = re.sub(r"</?\s*texto\s*>", "", texto, flags=re.I)
    return modelo.replace("{{TOM}}", tom).replace("{{TEXTO}}", texto_seguro)


# ---------------------------------------------------------------- chamadas de IA
def _post_json(url, corpo, cabecalhos):
    pedido = urllib.request.Request(
        url, data=json.dumps(corpo).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json", **cabecalhos},
    )
    try:
        with urllib.request.urlopen(pedido, timeout=60) as resposta:
            return json.loads(resposta.read().decode("utf-8"))
    except urllib.error.HTTPError as erro:
        if erro.code in (401, 403):
            mensagem = "A chave de API foi recusada. Confira se copiou a chave inteira no arquivo .env."
        elif erro.code == 429:
            mensagem = "O limite de uso da IA foi atingido. Espere um pouco ou verifique seu plano."
        else:
            mensagem = f"A IA respondeu com o erro {erro.code}: {erro.read().decode('utf-8', 'ignore')[:300]}"
        raise RuntimeError(mensagem) from erro
    except (urllib.error.URLError, TimeoutError) as erro:
        raise RuntimeError("Não consegui falar com a IA. Verifique sua conexão com a internet.") from erro


def chamar_claude(prompt):
    dados = _post_json(
        "https://api.anthropic.com/v1/messages",
        {"model": os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"), "max_tokens": 1500,
         "messages": [{"role": "user", "content": prompt}]},
        {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"},
    )
    return "".join(b.get("text", "") for b in dados.get("content", []) if b.get("type") == "text")


def chamar_gemini(prompt):
    modelo = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    dados = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
        {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
         "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}},
        {"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
    )
    try:
        return "".join(p.get("text", "") for p in dados["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError) as erro:
        raise RuntimeError("A IA não devolveu uma resposta utilizável. Tente de novo.") from erro


# ---------------------------------------------------------------- conferindo a resposta
def extrair_json(texto):
    """Pega o JSON da resposta, mesmo que a IA coloque ```json ou texto extra ao redor."""
    limpo = re.sub(r"^```(?:json)?\s*|\s*```$", "", texto.strip(), flags=re.I)
    try:
        return json.loads(limpo)
    except json.JSONDecodeError:
        inicio, fim = limpo.find("{"), limpo.rfind("}")
        if inicio != -1 and fim > inicio:
            return json.loads(limpo[inicio:fim + 1])
        raise ValueError("A resposta não contém um JSON.")


def _lista_de_textos(valor):
    if not isinstance(valor, list):
        return []
    return [str(item).strip() for item in valor if str(item).strip()]


def validar(dados):
    """Garante que o resultado tem todos os campos e no formato certo (a IA às vezes erra)."""
    if not isinstance(dados, dict):
        raise ValueError("O resultado precisa ser um objeto JSON.")
    tarefas = []
    for t in dados.get("tarefas") or []:
        if isinstance(t, dict) and str(t.get("o_que", "")).strip():
            tarefas.append({
                "o_que": str(t["o_que"]).strip(),
                "responsavel": str(t.get("responsavel") or NAO_INFORMADO).strip(),
                "prazo": str(t.get("prazo") or NAO_INFORMADO).strip(),
            })
    return {
        "titulo": str(dados.get("titulo") or "Resumo").strip(),
        "resumo": _lista_de_textos(dados.get("resumo")),
        "decisoes": _lista_de_textos(dados.get("decisoes")),
        "tarefas": tarefas,
        "pontos_em_aberto": _lista_de_textos(dados.get("pontos_em_aberto")),
        "email_followup": str(dados.get("email_followup") or "").strip(),
    }


# ---------------------------------------------------------------- modo demonstração (sem IA)
PRONOMES = {"Ele", "Ela", "Isso", "Tudo", "Também", "Então", "Quem", "Alguém", "Ninguém"}


def analisar_demo(texto, tom):
    """Versão simples por regras, só para você testar sem chave. A IA real entende muito mais."""
    frases = [f.strip() for f in re.split(r"(?<=[.!?])\s+|\n+", texto) if len(f.strip()) > 15]
    decisoes = [f for f in frases if re.search(r"decidi|aprovad|combinamos|vamos adotar", f, re.I)]
    abertos = [f for f in frases if re.search(r"\?|pendente|em aberto|ainda não|falta definir|a definir", f, re.I)]
    tarefas = []
    for frase in frases:
        achou = re.search(
            r"\b([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)\s+(?:vai|ficou de|precisa|fica responsável por|deve)\s+(.+)", frase)
        if achou and achou.group(1) not in PRONOMES:
            prazo = re.search(
                r"(até\s+[^,.;]+|amanhã|hoje|na\s+(?:segunda|terça|quarta|quinta|sexta)[^,.;]*|dia\s+\d{1,2}[^,.;]*)",
                frase, re.I)
            tarefas.append({"o_que": achou.group(2).strip(" ."), "responsavel": achou.group(1),
                            "prazo": prazo.group(1).strip() if prazo else NAO_INFORMADO})
    abertura, fecho = ("Prezados,", "Atenciosamente,") if tom == "formal" else ("Olá, pessoal!", "Abraço!")
    linhas = [abertura, "", "Segue o resumo do nosso encontro."]
    if decisoes:
        linhas += ["", "Decisões:"] + [f"- {d}" for d in decisoes]
    if tarefas:
        linhas += ["", "Próximos passos:"] + [f"- {t['responsavel']}: {t['o_que']}" for t in tarefas]
    linhas += ["", fecho]
    return {"titulo": "Resumo (modo demonstração)", "resumo": frases[:3], "decisoes": decisoes,
            "tarefas": tarefas, "pontos_em_aberto": abertos, "email_followup": "\n".join(linhas)}


# ---------------------------------------------------------------- função principal
def analisar(texto, tom="informal"):
    """Recebe o texto e devolve (resultado, modo). Levanta ValueError/RuntimeError com mensagem amigável."""
    texto = (texto or "").strip()
    if len(texto) < 20:
        raise ValueError("Cole um texto um pouco maior (mínimo de 20 caracteres).")
    if len(texto) > LIMITE_CARACTERES:
        raise ValueError(f"Texto grande demais (máximo de {LIMITE_CARACTERES} caracteres). Divida em partes.")
    tom = tom if tom in ("formal", "informal") else "informal"
    modo = qual_ia()
    if modo == "demo":
        return validar(analisar_demo(texto, tom)), modo

    prompt = montar_prompt(texto, tom)
    for _ in range(2):  # se a IA errar o formato, pedimos mais uma vez
        resposta = chamar_claude(prompt) if modo == "claude" else chamar_gemini(prompt)
        try:
            return validar(extrair_json(resposta)), modo
        except ValueError:
            prompt += "\n\nSua resposta anterior não era um JSON válido. Responda de novo SOMENTE com o JSON."
    raise RuntimeError("A IA não devolveu o formato esperado. Tente de novo.")


def para_markdown(dados, modo):
    """Transforma o resultado em um texto Markdown (bom para salvar e para o GitHub)."""
    def lista(itens):
        return [f"- {i}" for i in itens] or ["- (nada identificado)"]

    celula = lambda t: t.replace("|", "/").replace("\n", " ")
    linhas = [f"# {dados['titulo']}", "", f"_Gerado em {datetime.now():%d/%m/%Y %H:%M} · {ROTULO_MODO[modo]}_",
              "", "## Resumo", *lista(dados["resumo"]), "", "## Decisões", *lista(dados["decisoes"]), "",
              "## Tarefas", ""]
    if dados["tarefas"]:
        linhas += ["| O quê | Quem | Prazo |", "|---|---|---|"]
        linhas += [f"| {celula(t['o_que'])} | {celula(t['responsavel'])} | {celula(t['prazo'])} |" for t in dados["tarefas"]]
    else:
        linhas.append("- (nenhuma tarefa identificada)")
    linhas += ["", "## Pontos em aberto", *lista(dados["pontos_em_aberto"]), "", "## E-mail de follow-up", "",
              *[f"> {l}" if l else ">" for l in dados["email_followup"].splitlines()]]
    return "\n".join(linhas) + "\n"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # evita erro de acentos no terminal do Windows
    parser = argparse.ArgumentParser(description="Ata Pronta: anotações bagunçadas -> ata organizada")
    parser.add_argument("arquivo", help="arquivo .txt com as anotações")
    parser.add_argument("--tom", choices=["informal", "formal"], default="informal", help="tom do e-mail")
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    if not caminho.exists():
        sys.exit(f"Não encontrei o arquivo: {caminho}")
    try:
        dados, modo = analisar(caminho.read_text(encoding="utf-8"), args.tom)
    except (ValueError, RuntimeError) as erro:
        sys.exit(f"Erro: {erro}")

    markdown = para_markdown(dados, modo)
    saida = PASTA / "resultados" / f"{caminho.stem}_{datetime.now():%Y%m%d_%H%M%S}.md"
    saida.parent.mkdir(exist_ok=True)
    saida.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"Salvo em: {saida}")
    if modo == "demo":
        print("Dica: você está no modo demonstração. Coloque uma chave de API no .env para usar IA de verdade.")


if __name__ == "__main__":
    main()
