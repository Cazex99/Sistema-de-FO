from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

from io import BytesIO
import html
from collections import Counter
from sqlalchemy.orm import joinedload

app = Flask(__name__)

# =========================
#  SEGURANÇA
# =========================
app.config['SECRET_KEY'] = "chave-super-secreta-5cia"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",  
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # coloque True quando usar HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# =========================
# MODELOS
# =========================

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)


class Militar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    posto = db.Column(db.String(50), nullable=False)
    pelotao = db.Column(db.String(50), nullable=False)

    avaliacoes = db.relationship(
        'Avaliacao',
        backref='militar',
        cascade="all, delete-orphan"
    )


class Avaliacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    militar_id = db.Column(db.Integer, db.ForeignKey('militar.id'), nullable=False)
    avaliador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

    resultado = db.Column(db.String(10), nullable=False)
    descricao = db.Column(db.Text)
    data_ocorrido = db.Column(db.Date)

    avaliador = db.relationship('Usuario')


# =========================
# FUNÇÃO PONTUAÇÃO
# =========================

def converter_ponto(valor):
    if valor == "FO+":
        return 1
    elif valor == "FO-":
        return -1
    return 0


# =========================
# LOGIN
# =========================

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        senha = request.form.get("senha", "")

        user = Usuario.query.filter_by(username=username).first()

        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Usuário ou senha inválidos")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
@login_required
def dashboard():

    militares = Militar.query.all()

    if current_user.perfil == "admin":
        return render_template("dashboard_admin.html", militares=militares)

    return render_template("dashboard_avaliador.html", militares=militares)


# =========================
# GERENCIAR USUÁRIOS
# =========================

@app.route("/gerenciar_usuarios")
@login_required
def gerenciar_usuarios():

    if current_user.perfil != "admin":
        return "Acesso restrito"

    usuarios = Usuario.query.all()

    return render_template("gerenciar_usuarios.html", usuarios=usuarios)


# =========================
# EDITAR USUÁRIO
# =========================

@app.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
@login_required
def editar_usuario(id):

    if current_user.perfil != "admin":
        return "Acesso restrito"

    usuario = Usuario.query.get_or_404(id)

    if request.method == "POST":

        usuario.username = request.form.get("usuario")
        usuario.perfil = request.form.get("perfil")

        nova_senha = request.form.get("senha")

        if nova_senha:
            usuario.senha = generate_password_hash(nova_senha)

        db.session.commit()

        flash("Usuário atualizado com sucesso!")

        return redirect(url_for("gerenciar_usuarios"))

    return render_template("editar_usuario.html", usuario=usuario)


# =========================
# EXCLUIR USUÁRIO
# =========================

@app.route("/excluir_usuario/<int:id>")
@login_required
def excluir_usuario(id):

    if current_user.perfil != "admin":
        return "Acesso restrito"

    usuario = Usuario.query.get_or_404(id)

    if usuario.username == "admin":
        flash("Não é possível excluir o administrador principal.")
        return redirect(url_for("gerenciar_usuarios"))

    db.session.delete(usuario)
    db.session.commit()

    flash("Usuário excluído com sucesso!")

    return redirect(url_for("gerenciar_usuarios"))


# =========================
# CADASTRAR USUÁRIO
# =========================

@app.route("/cadastrar_usuario", methods=["GET", "POST"])
@login_required
def cadastrar_usuario():

    if current_user.perfil != "admin":
        return "Acesso restrito"

    if request.method == "POST":

        username = request.form.get("usuario", "").strip()
        senha = request.form.get("senha")
        perfil = request.form.get("perfil")

        if Usuario.query.filter_by(username=username).first():
            flash("Usuário já existe!")
            return redirect(url_for("cadastrar_usuario"))

        novo = Usuario(
            username=username,
            senha=generate_password_hash(senha),
            perfil=perfil
        )

        db.session.add(novo)
        db.session.commit()

        flash("Usuário cadastrado com sucesso!")

        return redirect(url_for("dashboard"))

    return render_template("cadastrar_usuario.html")


# =========================
# CADASTRAR MILITAR
# =========================

@app.route("/cadastrar_militar", methods=["GET", "POST"])
@login_required
def cadastrar_militar():

    if current_user.perfil != "admin":
        return "Acesso restrito"

    if request.method == "POST":

        nome = request.form.get("nome")
        posto = request.form.get("posto")
        pelotao = request.form.get("pelotao")

        novo = Militar(nome=nome, posto=posto, pelotao=pelotao)

        db.session.add(novo)
        db.session.commit()

        flash("Militar cadastrado com sucesso!")

        return redirect(url_for("dashboard"))

    return render_template("cadastrar_militar.html")


# =========================
# EDITAR MILITAR
# =========================

@app.route("/editar_militar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_militar(id):

    if current_user.perfil != "admin":
        return "Acesso restrito"

    militar = Militar.query.get_or_404(id)

    if request.method == "POST":

        militar.nome = request.form.get("nome")
        militar.posto = request.form.get("posto")
        militar.pelotao = request.form.get("pelotao")

        db.session.commit()

        flash("Militar atualizado com sucesso!")

        return redirect(url_for("dashboard"))

    return render_template("editar_militar.html", militar=militar)


# =========================
# EXCLUIR MILITAR
# =========================

@app.route("/excluir_militar/<int:id>")
@login_required
def excluir_militar(id):

    if current_user.perfil != "admin":
        return "Acesso restrito"

    militar = Militar.query.get_or_404(id)

    db.session.delete(militar)
    db.session.commit()

    flash("Militar excluído com sucesso!")

    return redirect(url_for("dashboard"))


# =========================
# AVALIAR
# =========================

@app.route("/avaliar/<int:id>", methods=["GET", "POST"])
@login_required
def avaliar(id):

    militar = Militar.query.get_or_404(id)

    if request.method == "POST":

        data_form = request.form.get("data_ocorrido")
        data_convertida = None

        if data_form:
            data_convertida = datetime.strptime(data_form, "%Y-%m-%d")

        nova = Avaliacao(
            militar_id=militar.id,
            avaliador_id=current_user.id,
            resultado=request.form.get("resultado"),
            descricao=request.form.get("descricao"),
            data_ocorrido=data_convertida
        )

        db.session.add(nova)
        db.session.commit()

        flash("Avaliação registrada com sucesso!")

        return redirect(url_for("dashboard"))

    return render_template("avaliar.html", militar=militar)


# =========================
# RELATÓRIO
# =========================

@app.route("/relatorio")
@login_required
def relatorio():

    if current_user.perfil != "admin":
        return "Relatório disponível apenas para administrador"

    militares = Militar.query.all()

    dados = []

    for m in militares:

        fo_positivo = sum(1 for a in m.avaliacoes if a.resultado == "FO+")
        fo_negativo = sum(1 for a in m.avaliacoes if a.resultado == "FO-")
        neutro = sum(1 for a in m.avaliacoes if a.resultado == "NEUTRO")

        total_avaliacoes = len(m.avaliacoes)
        total_pontos = sum(converter_ponto(a.resultado) for a in m.avaliacoes)

        if total_avaliacoes > 0:
            media_bruta = total_pontos / total_avaliacoes
            nota = ((media_bruta + 1) / 2) * 10
        else:
            nota = 0

        dados.append({
            "id": m.id,
            "nome": m.nome,
            "posto": m.posto,
            "pelotao": m.pelotao,
            "nota": round(nota, 1),
            "qtd_avaliacoes": total_avaliacoes,
            "fo_positivo": fo_positivo,
            "fo_negativo": fo_negativo,
            "neutro": neutro
        })

    return render_template("relatorio.html", dados=dados)


# =========================
# PDF 
# =========================

from flask import send_file
from io import BytesIO
import html
from datetime import datetime
from collections import Counter

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

from sqlalchemy.orm import joinedload


def borda(canvas, doc):
    width, height = A4
    margem = 20

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(1)
    canvas.rect(margem, margem, width - 2*margem, height - 2*margem)


@app.route("/relatorio_pdf/<int:militar_id>")
@login_required
def relatorio_pdf(militar_id):

    if current_user.perfil != "admin":
        return "Acesso restrito", 403

    militar = Militar.query.options(
        joinedload(Militar.avaliacoes).joinedload(Avaliacao.avaliador)
    ).get_or_404(militar_id)

    avaliacoes = militar.avaliacoes

    contagem = Counter(a.resultado for a in avaliacoes)
    fo_positivo = contagem.get("FO+", 0)
    fo_negativo = contagem.get("FO-", 0)
    neutro = contagem.get("NEUTRO", 0)

    avaliacoes = sorted(
        avaliacoes,
        key=lambda x: x.data_ocorrido or datetime.min,
        reverse=True
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elementos = []
    estilos = getSampleStyleSheet()

    # LOGO
    try:
        logo = Image("static/imagens/logo.png")
        logo.drawHeight = 80
        logo.drawWidth = 80
        logo.hAlign = 'CENTER'
        elementos.append(logo)
    except:
        pass

    elementos.append(Spacer(1, 10))

    # CABEÇALHO
    elementos.append(Paragraph(
        "<b> QUARTEL </b>",
        ParagraphStyle(
            'cabecalho',
            alignment=1,
            fontSize=16,
            textColor=colors.HexColor("#0a3d62"),
            spaceAfter=5
        )
    ))

    elementos.append(Paragraph(
        "",
        ParagraphStyle(
            'sub',
            alignment=1,
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=15
        )
    ))

    # RELATÓRIO
    elementos.append(Paragraph(
        "<b>RELATÓRIO INDIVIDUAL</b>",
        ParagraphStyle(
            'titulo',
            alignment=1,
            fontSize=14,
            textColor=colors.black,
            spaceAfter=25
        )
    ))

    # DADOS
    dados_militar = [
        ["Nome de guerra:", militar.nome],
        ["Graduação:", militar.posto],
        ["Seção/Pelotão:", militar.pelotao],
    ]

    tabela_info = Table(dados_militar, colWidths=[110, 290])

    tabela_info.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(tabela_info)
    elementos.append(Spacer(1, 15))

    # RESUMO
    resumo = [
        ["FO+", fo_positivo],
        ["FO-", fo_negativo],
        ["FO NEUTRO", neutro]
    ]

    tabela_resumo = Table(resumo, colWidths=[120, 80])

    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER')
    ]))

    elementos.append(tabela_resumo)
    elementos.append(Spacer(1, 25))

    # TABELA PRINCIPAL
    dados = [["Data", "Resultado", "Avaliador", "Descrição"]]

    for a in avaliacoes:

        resultado = "FO NEUTRO" if a.resultado == "NEUTRO" else a.resultado

        #  SEGURANÇA: limita tamanho + escape
        descricao_segura = "-"
        if a.descricao:
            descricao_limpa = a.descricao[:500]  # limite evita travamento
            descricao_segura = html.escape(descricao_limpa)

        dados.append([
            a.data_ocorrido.strftime("%d/%m/%Y") if a.data_ocorrido else "-",
            resultado,
            a.avaliador.username if a.avaliador else "Removido",
            Paragraph(descricao_segura, estilos["Normal"])
        ])

    tabela = Table(dados, repeatRows=1, colWidths=[70, 80, 120, 230])

    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0a3d62")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'LEFT'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f2f6fa")]),

        ('GRID', (0, 0), (-1, -1), 0.3, colors.grey)
    ]))

    elementos.append(tabela)

    # RODAPÉ
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(
        "Documento gerado pelo sistema<br/><br/>"
        "<b>Desenvolvido por 3º Sargento Cassemiro</b>",
        ParagraphStyle(
            'rodape',
            alignment=1,
            fontSize=8,
            textColor=colors.grey
        )
    ))

    #  SEGURANÇA: evita PDF corrompido
    try:
        doc.build(elementos, onFirstPage=borda, onLaterPages=borda)
    except Exception:
        return "Erro ao gerar PDF", 500

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"relatorio_{int(militar.id)}.pdf",
        mimetype='application/pdf'
    )



# =========================
# ALTERAR SENHA
# =========================

@app.route("/alterar_senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")

        if not check_password_hash(current_user.senha, senha_atual):
            flash("Senha atual incorreta!")
            return redirect(url_for("alterar_senha"))

        current_user.senha = generate_password_hash(nova_senha)
        db.session.commit()

        flash("Senha alterada com sucesso!")
        return redirect(url_for("dashboard"))

    return render_template("alterar_senha.html")


# =========================
# BANCO
# =========================

with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(username="admin").first():
        admin = Usuario(
            username="admin",
            senha=generate_password_hash("admin"),
            perfil="admin"
        )
        db.session.add(admin)
        db.session.commit()


# =========================
# EXECUTAR
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
