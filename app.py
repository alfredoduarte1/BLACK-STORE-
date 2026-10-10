import os
import secrets
from datetime import timedelta
from html import escape
from urllib.parse import quote

from flask import Flask, request, session, redirect, url_for

app = Flask(__name__)

# Antes de publicar, configure SECRET_KEY como variável de ambiente segura.
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")
app.permanent_session_lifetime = timedelta(days=30)

PRODUTOS = {
    "camisa": 1000,
    "tênis": 2500,
    "boné": 500,
    "perfume": 650,
}

# Códigos temporários apenas para demonstração. Não usar este sistema em produção.
codigos = {}


def pagina(conteudo):
    return f"""<!doctype html>
<html lang="pt">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BLACK STORE | O seu estilo, sua marca</title>
  <style>
    :root {{ color-scheme: dark; }}
    * {{ box-sizing: border-box; }}
    body {{ background:#050509; color:#f5f5ff; font-family:Arial,sans-serif; margin:0; padding:20px; }}
    main {{ max-width:760px; margin:0 auto; }}
    h1 {{ text-align:center; letter-spacing:3px; font-size:clamp(28px,6vw,42px); color:#b794ff; }}
    .slogan {{ text-align:center; color:#a8a8c7; margin-top:-12px; }}
    .card {{ background:linear-gradient(135deg,#101018,#17172a); border:1px solid #343052; border-radius:16px; padding:16px; margin:14px 0; }}
    .produto {{ display:flex; justify-content:space-between; gap:12px; padding:12px 0; border-bottom:1px solid #2a2940; }}
    .produto:last-child {{ border-bottom:0; }}
    .preco {{ color:#c4a7ff; font-weight:bold; white-space:nowrap; }}
    input, textarea, select {{ display:block; width:100%; background:#0b0b12; color:white; border:1px solid #484365; border-radius:9px; padding:12px; margin:8px 0 14px; font-size:16px; }}
    input[type=radio], input[type=checkbox] {{ display:inline-block; width:auto; margin:0 7px 0 0; }}
    label {{ display:inline-block; margin:8px 14px 8px 0; }}
    button, .btn {{ display:inline-block; border:0; border-radius:25px; padding:12px 18px; background:linear-gradient(90deg,#7027c9,#244c9b); color:white; font-weight:bold; text-decoration:none; cursor:pointer; }}
    button {{ width:100%; margin-top:8px; }}
    .aviso {{ background:#19152a; border:1px solid #6043a0; border-radius:10px; padding:14px; overflow-wrap:anywhere; }}
    .muted {{ color:#a8a8bd; font-size:13px; }}
    footer {{ text-align:center; color:#88889b; font-size:12px; line-height:1.8; margin:28px 0 8px; }}
    a {{ color:#c4a7ff; }}
  </style>
</head>
<body><main>
  <h1>BLACK STORE</h1>
  <p class="slogan">O seu estilo, sua marca</p>
  {conteudo}
  <footer>
    Criado por Alfredo Duarte<br>
    Email: alfredoduartee2@gmail.com<br>
    Pemba, Cabo Delgado, Moçambique<br>
    Ano de criação: 2026
  </footer>
</main></body></html>"""


@app.route("/", methods=["GET"])
def loja():
    itens = "".join(
        f"<div class='produto'><span>{escape(nome.title())}</span>"
        f"<span class='preco'>{preco} MT</span></div>"
        for nome, preco in PRODUTOS.items()
    )

    estado_login = (
        f"<p class='muted'>Sessão iniciada: {escape(session['telefone'])} "
        f"· <a href='{url_for('sair')}'>Terminar sessão</a></p>"
        if session.get("telefone")
        else f"<p class='muted'><a href='{url_for('entrar')}'>Entrar (opcional)</a>. "
             "Podes comprar sem criar conta.</p>"
    )

    pagamento = ""
    produto = request.args.get("produto", "")
    metodo = request.args.get("pagar", "")
    if produto in PRODUTOS and metodo in ("mpesa", "emola"):
        preco = PRODUTOS[produto]
        if metodo == "mpesa":
            dados = "M-Pesa: 85 690 8830"
        else:
            dados = "eMola: 87 924 4138"
        mensagem = quote(f"Olá, fiz uma compra na BLACK STORE: {produto.title()} por {preco} MT. Vou enviar o comprovativo.")
        pagamento = f"""
        <section class="card">
          <h3>Instruções de pagamento</h3>
          <p><strong>{escape(produto.title())} — {preco} MT</strong></p>
          <p>{dados}<br>Nome: Alfredo Duarte</p>
          <p class="muted">Depois de pagar, envia o comprovativo pelo WhatsApp. O pagamento precisa de ser confirmado antes da entrega.</p>
          <a class="btn" href="https://wa.me/258856908830?text={mensagem}">ENVIAR COMPROVATIVO</a>
        </section>"""

    conteudo = f"""
    {estado_login}
    <section class="card">
      <h2>Produtos</h2>
      {itens}
    </section>
    <section class="card">
      <h2>Comprar</h2>
      <form method="get" action="/">
        <label for="produto">Escolhe um produto</label>
        <select id="produto" name="produto" required>
          <option value="">Selecionar...</option>
          {''.join(f'<option value="{escape(nome, quote=True)}">{escape(nome.title())} — {preco} MT</option>' for nome, preco in PRODUTOS.items())}
        </select>
        <p>Forma de pagamento:</p>
        <label><input type="radio" name="pagar" value="mpesa" required> M-Pesa</label>
        <label><input type="radio" name="pagar" value="emola" required> eMola</label>
        <button type="submit">CONTINUAR COMPRA</button>
      </form>
    </section>
    {pagamento}
    <section class="card" id="feedback">
      <h2>Feedback</h2>
      <p>Conta-nos a tua opinião ou envia uma sugestão.</p>
      <form action="https://formsubmit.co/alfredoduartee2@gmail.com" method="POST">
        <input type="hidden" name="_subject" value="Novo feedback — BLACK STORE">
        <input type="hidden" name="_captcha" value="false">
        <label for="nome">Seu nome</label>
        <input id="nome" type="text" name="nome" placeholder="Seu nome" maxlength="100" required>
        <label for="mensagem">Mensagem</label>
        <textarea id="mensagem" name="mensagem" placeholder="Escreve aqui o teu feedback..." rows="4" maxlength="3000" required></textarea>
        <button type="submit">ENVIAR FEEDBACK</button>
      </form>
      <p class="muted">Na primeira utilização, o FormSubmit pode pedir confirmação do endereço de email.</p>
    </section>
    """
    return pagina(conteudo)


@app.route("/entrar", methods=["GET"])
def entrar():
    conteudo = """
    <section class="card">
      <h2>Entrar por telefone</h2>
      <p class="muted">O login é opcional. Podes comprar sem entrar.</p>
      <form method="post" action="/enviar-codigo">
        <label for="prefixo">Indicativo do país</label>
        <select id="prefixo" name="prefixo">
          <option value="+258">Moçambique (+258)</option>
          <option value="+27">África do Sul (+27)</option>
          <option value="+351">Portugal (+351)</option>
          <option value="+55">Brasil (+55)</option>
        </select>
        <label for="telefone">Número de telefone (apenas números)</label>
        <input id="telefone" name="telefone" inputmode="numeric" pattern="[0-9]{6,15}" minlength="6" maxlength="15" required>
        <label><input type="checkbox" name="manter" value="sim"> Manter sessão iniciada</label>
        <button type="submit">GERAR CÓDIGO DE TESTE</button>
      </form>
      <p class="muted">Demonstração: este protótipo não envia SMS nem está ligado ao Google. O código aparece na página apenas para testes.</p>
      <p><a href="/">Voltar à loja</a></p>
    </section>"""
    return pagina(conteudo)


@app.route("/enviar-codigo", methods=["POST"])
def enviar_codigo():
    prefixo = request.form.get("prefixo", "+258")
    telefone = "".join(ch for ch in request.form.get("telefone", "") if ch.isdigit())
    manter = request.form.get("manter") == "sim"

    if prefixo not in ("+258", "+27", "+351", "+55") or not 6 <= len(telefone) <= 15:
        return pagina("<section class='card'><h2>Dados inválidos</h2><p>Confirma o indicativo e o número de telefone.</p><a href='/entrar'>Tentar novamente</a></section>"), 400

    numero_completo = prefixo + telefone
    codigo = f"{secrets.randbelow(1000000):06d}"
    codigos[numero_completo] = codigo

    conteudo = f"""
    <section class="card">
      <h2>Código de demonstração</h2>
      <p>Telefone: {escape(numero_completo)}</p>
      <div class="aviso"><strong>O teu código de teste é: {codigo}</strong></div>
      <p class="muted">Este código aparece aqui apenas para testes. Não é enviado por SMS. Não uses esta versão para autenticação real.</p>
      <form method="post" action="/confirmar">
        <input type="hidden" name="telefone" value="{escape(numero_completo, quote=True)}">
        <input type="hidden" name="manter" value="{'sim' if manter else 'nao'}">
        <label for="codigo">Código de 6 dígitos</label>
        <input id="codigo" name="codigo" inputmode="numeric" pattern="[0-9]{{6}}" minlength="6" maxlength="6" required>
        <button type="submit">CONFIRMAR CÓDIGO</button>
      </form>
    </section>"""
    return pagina(conteudo)


@app.route("/confirmar", methods=["POST"])
def confirmar():
    telefone = request.form.get("telefone", "")
    codigo = request.form.get("codigo", "")
    codigo_guardado = codigos.get(telefone)

    if not codigo_guardado or not secrets.compare_digest(codigo, codigo_guardado):
        return pagina("<section class='card'><h2>Código inválido</h2><p>Gera um novo código e tenta novamente.</p><a href='/entrar'>Voltar</a></section>"), 400

    codigos.pop(telefone, None)
    session.clear()
    session["telefone"] = telefone
    session.permanent = request.form.get("manter") == "sim"
    return redirect(url_for("loja"))


@app.route("/sair", methods=["GET"])
def sair():
    session.clear()
    return redirect(url_for("loja"))


if __name__ == "__main__":
    # Para testar localmente. O alojamento define a porta em produção.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")), debug=False)
