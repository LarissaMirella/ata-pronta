"""Versão com página web do Ata Pronta (roda só no seu computador).

Uso:
    python web.py
e abra http://127.0.0.1:8000 no navegador.
"""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

import ata

LIMITE_ENVIO = 100_000  # bytes aceitos por envio

PAGINA = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ata Pronta</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;background:#f6f7fb;color:#1f2430;margin:0}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}
h1{margin:0 0 4px}.sub{color:#5b6475;margin:0 0 16px}
textarea{width:100%;box-sizing:border-box;padding:12px;border:1px solid #c9cfdb;border-radius:8px;font:inherit}
.linha{display:flex;gap:12px;align-items:center;margin:10px 0}
button{background:#3b5bdb;color:#fff;border:0;border-radius:8px;padding:10px 18px;font:inherit;cursor:pointer}
.card{background:#fff;border:1px solid #e1e5ee;border-radius:10px;padding:16px;margin-top:16px}
.card h2{font-size:17px;margin:0 0 8px}table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:6px;border-bottom:1px solid #e1e5ee;vertical-align:top}
.erro{background:#fdecec;border:1px solid #f3b4b4;padding:12px;border-radius:8px;margin-top:16px}
.nota{color:#5b6475;font-size:13px;margin-top:20px}.selo{font-size:13px;color:#5b6475}
pre{white-space:pre-wrap;font:inherit;margin:0}
</style></head><body><main>
<h1>📝 Ata Pronta</h1><p class="sub">Cole suas anotações e receba resumo, decisões, tarefas e um e-mail pronto.</p>
<form method="post"><textarea name="texto" rows="10" required placeholder="Cole aqui as anotações da reunião, aula ou assembleia...">%%TEXTO%%</textarea>
<div class="linha"><label>Tom do e-mail:
<select name="tom"><option value="informal" %%INF%%>informal</option><option value="formal" %%FOR%%>formal</option></select></label>
<button type="submit">Gerar ata</button></div></form>%%RESULTADO%%
<p class="nota">⚠️ Com uma chave de API configurada, o texto é enviado ao provedor de IA. Não cole dados sensíveis (senhas, documentos, informações de terceiros).</p>
</main></body></html>"""


def _lista(itens):
    return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in itens) + "</ul>" if itens else "<p>(nada identificado)</p>"


def renderizar_resultado(dados, modo):
    """Monta o HTML do resultado. Todo texto passa por html.escape (segurança contra HTML malicioso)."""
    if dados["tarefas"]:
        linhas = "".join(
            f"<tr><td>{html.escape(t['o_que'])}</td><td>{html.escape(t['responsavel'])}</td><td>{html.escape(t['prazo'])}</td></tr>"
            for t in dados["tarefas"])
        tarefas = f"<table><tr><th>O quê</th><th>Quem</th><th>Prazo</th></tr>{linhas}</table>"
    else:
        tarefas = "<p>(nenhuma tarefa identificada)</p>"
    return (
        f'<div class="card"><h2>{html.escape(dados["titulo"])}</h2><span class="selo">{html.escape(ata.ROTULO_MODO[modo])}</span></div>'
        f'<div class="card"><h2>Resumo</h2>{_lista(dados["resumo"])}</div>'
        f'<div class="card"><h2>Decisões</h2>{_lista(dados["decisoes"])}</div>'
        f'<div class="card"><h2>Tarefas</h2>{tarefas}</div>'
        f'<div class="card"><h2>Pontos em aberto</h2>{_lista(dados["pontos_em_aberto"])}</div>'
        f'<div class="card"><h2>E-mail de follow-up</h2><pre>{html.escape(dados["email_followup"])}</pre></div>'
    )


def pagina(texto="", tom="informal", resultado=""):
    return (PAGINA.replace("%%TEXTO%%", html.escape(texto)).replace("%%RESULTADO%%", resultado)
            .replace("%%INF%%", "selected" if tom != "formal" else "")
            .replace("%%FOR%%", "selected" if tom == "formal" else ""))


class Manipulador(BaseHTTPRequestHandler):
    def _enviar(self, conteudo, status=200):
        corpo = conteudo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path.split("?")[0] != "/":
            return self._enviar("Página não encontrada", 404)
        self._enviar(pagina())

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._enviar("Requisição inválida.", 400)
        if tamanho < 0:
            return self._enviar("Requisição inválida.", 400)
        if tamanho > LIMITE_ENVIO:
            return self._enviar("Texto grande demais.", 413)
        campos = parse_qs(self.rfile.read(tamanho).decode("utf-8", "replace"))
        texto = campos.get("texto", [""])[0]
        tom = campos.get("tom", ["informal"])[0]
        try:
            dados, modo = ata.analisar(texto, tom)
            resultado = renderizar_resultado(dados, modo)
        except (ValueError, RuntimeError) as erro:
            resultado = f'<div class="erro">{html.escape(str(erro))}</div>'
        self._enviar(pagina(texto, tom, resultado))

    def log_message(self, formato, *args):  # silencia o log do servidor
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--porta", type=int, default=8000)
    args = parser.parse_args()
    servidor = ThreadingHTTPServer(("127.0.0.1", args.porta), Manipulador)
    print(f"Ata Pronta rodando em http://127.0.0.1:{args.porta}  (Ctrl+C para parar)")
    print(f"Modo atual: {ata.ROTULO_MODO[ata.qual_ia()]}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
