CREATE TABLE turnos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE escolas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL,
    localizacao VARCHAR(10) NOT NULL CHECK (localizacao IN ('urbano', 'rural'))
);

CREATE TABLE turmas (
    id SERIAL PRIMARY KEY,
    escola_id INTEGER NOT NULL,
    ano_escolar VARCHAR(20) NOT NULL,
    turno_id INTEGER NOT NULL,
    FOREIGN KEY (escola_id) REFERENCES escolas(id),
    FOREIGN KEY (turno_id) REFERENCES turnos(id),
    UNIQUE (escola_id, ano_escolar, turno_id)
);

CREATE TABLE administrador (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(20) NOT NULL
);

CREATE TABLE acessos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    cpf VARCHAR(20),
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alunos (
    matricula VARCHAR(20) PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    administrador_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (administrador_id) REFERENCES administrador(id),
    FOREIGN KEY (turma_id) REFERENCES turmas(id)

);

CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    visitante_id INTEGER NOT NULL,
    aluno_matricula VARCHAR(20) NOT NULL,
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visitante_id) REFERENCES visitantes(id),
    FOREIGN KEY (aluno_matricula) REFERENCES alunos(matricula)
);
