from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime
import os

data_hora = datetime.now()


app = Flask(__name__)
app.secret_key = 'minha-chave-secreta-123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor = conn.cursor()

class Admin(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT id, email FROM administrador WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        return Admin(result[0], result[1])
    return None

@app.route('/')
def index():
    sucesso = request.args.get('sucesso')
    return render_template('index.html', sucesso=sucesso)



@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        cursor.execute("SELECT * FROM administrador WHERE email = %s AND senha = %s", (email, senha))
        admin = cursor.fetchone()
        
        if admin and senha == admin[2]:
            login_user(Admin(admin[0], admin[1]))  # salva na sessão
            return redirect(url_for('painel'))
        else:
            erro = 'Email ou senha inválidos.'

    return render_template('login.html', erro=erro)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/painel')
@login_required
def painel():
    return render_template('painel.html')

@app.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro():
    erro = None

    if request.method == 'POST':
        matricula = request.form['matricula']
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        turma_id = request.form['turma_id']

        administrador_id = current_user.id  # aqui está a mudança!

        try:
            cursor.execute(
                "INSERT INTO alunos (matricula, nome, data_nascimento, administrador_id, turma_id) VALUES (%s, %s, %s, %s, %s)",
                (matricula, nome, data_nascimento, administrador_id, turma_id)
            )
            conn.commit()
            return redirect(url_for('index', sucesso='cadastro'))
        
        except IntegrityError:
            conn.rollback()
            erro = "Erro: matrícula já cadastrada."
        conn.commit()
        return redirect('/')
    
    cursor.execute("""
        SELECT turmas.id, escolas.nome, turmas.ano_escolar, turnos.nome
        FROM turmas
        JOIN escolas ON turmas.escola_id = escolas.id
        JOIN turnos ON turmas.turno_id = turnos.id
        ORDER BY escolas.nome, turmas.ano_escolar
    """)
    turmas = cursor.fetchall()

    return render_template('cadastro.html', turmas=turmas, erro=erro)


@app.route('/editar', methods=['GET', 'POST'])
@login_required
def editar():
    erro = None
    if request.method == 'POST':
        matricula = request.form['matricula']
        campo = request.form['campo']

        if campo == 'turma_id':
            novo_valor = request.form.get('novo_valor_turma', '')
        else:
            novo_valor = request.form.get('novo_valor_texto', '')

        try:
            if campo == 'nome':
                cursor.execute("UPDATE alunos SET nome = %s WHERE matricula = %s", (novo_valor, matricula))
            elif campo == 'data_nascimento':
                cursor.execute("UPDATE alunos SET data_nascimento = %s WHERE matricula = %s", (novo_valor, matricula))
            elif campo == 'turma_id':
                if not novo_valor or not novo_valor.isdigit():
                    raise ValueError("ID da turma inválido.")
                turma_id = int(novo_valor)
                cursor.execute("UPDATE alunos SET turma_id = %s WHERE matricula = %s", (turma_id, matricula))
            elif campo == 'matricula':
                cursor.execute("UPDATE alunos SET matricula = %s WHERE matricula = %s", (novo_valor, matricula))
            else:
                raise ValueError("Campo inválido.")

            conn.commit()
            return redirect(url_for('index', sucesso='editado'))

        except Exception as e:
            conn.rollback()
            erro = f"Erro ao editar: {e}"

    cursor.execute("SELECT matricula, nome FROM alunos ORDER BY nome")
    alunos = cursor.fetchall()

    cursor.execute("""
        SELECT turmas.id, escolas.nome, turmas.ano_escolar, turnos.nome
        FROM turmas
        JOIN escolas ON turmas.escola_id = escolas.id
        JOIN turnos ON turmas.turno_id = turnos.id
        ORDER BY escolas.nome, turmas.ano_escolar
    """)
    turmas = cursor.fetchall()

    return render_template('editar.html', alunos=alunos, erro=erro, turmas=turmas)

@app.route('/excluir', methods=['GET', 'POST'])
@login_required
def excluir():
    erro = None
    if request.method == 'POST':
        matricula = request.form['matricula']
        cursor.execute("DELETE FROM alunos WHERE matricula = %s", (matricula,))
        conn.commit()
        return redirect(url_for('index', sucesso = 'excluido'))
    
    cursor.execute("SELECT matricula, nome FROM alunos ORDER BY nome")
    alunos = cursor.fetchall()
    return render_template('excluir.html', alunos = alunos, erro = erro)


@app.route('/alunos', methods=['GET', 'POST'])
def consultar_por_escola_turma():
    cursor.execute("SELECT id, nome FROM escolas ORDER BY nome")
    escolas = cursor.fetchall()

    turmas = []
    alunos = []

    escola_id = request.form.get('escola_id')
    turma_id = request.form.get('turma_id')

    if escola_id:
        cursor.execute("""
            SELECT turmas.id, turmas.ano_escolar, turnos.nome
            FROM turmas
            JOIN turnos ON turmas.turno_id = turnos.id
            WHERE turmas.escola_id = %s
            ORDER BY turmas.ano_escolar
        """, (escola_id,))
        turmas = cursor.fetchall()

    if turma_id:
        cursor.execute("""
            SELECT a.matricula, a.nome, a.data_nascimento
            FROM alunos a
            WHERE a.turma_id = %s
            ORDER BY a.data_hora ASC
        """, (turma_id,))
        alunos = cursor.fetchall()

    return render_template(
        'listarAlunos.html',
        escolas=escolas,
        turmas=turmas,
        alunos=alunos,
        escola_selecionada=escola_id,
        turma_selecionada=turma_id
    )

if __name__ == '__main__':
    app.run(debug=True)
