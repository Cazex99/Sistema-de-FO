# Sistema de Fato Observado

Sistema web desenvolvido com Flask para gestão de avaliações organizacionais. A aplicação permite autenticação de usuários, registro de avaliações e geração de relatórios.

O banco de dados é criado automaticamente na inicialização utilizando SQLite, com possibilidade de migração para PostgreSQL em ambiente de produção. A aplicação foi preparada para deploy utilizando Gunicorn como servidor WSGI e Nginx como proxy reverso.

---

##  Funcionalidades

* Autenticação de usuários
* Cadastro de registros
* Registro de avaliações
* Geração de relatórios

---

##  Tecnologias

* Flask
* PostgreSQL / SQLite
* Gunicorn
* Nginx

---

##  Arquitetura

Usuário → Nginx → Gunicorn → Flask (app.py) → PostgreSQL

A aplicação segue uma arquitetura em camadas:

* Nginx: atua como proxy reverso, recebendo requisições externas
* Gunicorn: servidor WSGI responsável por executar a aplicação Flask
* Flask: backend da aplicação
* PostgreSQL: banco de dados utilizado em produção

O projeto foi inicialmente desenvolvido com SQLite e posteriormente migrado para PostgreSQL.

---

##  Como executar

```bash
python -m venv venv
venv\Scripts\activate  # Windows

pip install -r requirements.txt
python app.py
```

Acesse em:
http://127.0.0.1:5000

---

##  Deploy

Exemplos de configuração para ambiente de produção estão disponíveis na pasta `deploy/`, incluindo:

* Gunicorn (WSGI server)
* Nginx (reverse proxy)

Os arquivos são genéricos e devem ser ajustados conforme o ambiente.

---

##  Imagens

As imagens não estão incluídas neste repositório.

Para o funcionamento correto da interface, adicione os seguintes arquivos na pasta:

```
static/imagens/
```

Arquivos necessários:

* `logo.png`
* `fundo.jpg`

Você pode utilizar quaisquer imagens, desde que mantenha esses nomes.
Caso altere os nomes dos arquivos, será necessário atualizar as referências no código.

---

##  Banco de Dados

O sistema utiliza SQLite no ambiente de desenvolvimento.

Ao iniciar a aplicação, o banco de dados é criado automaticamente na pasta:

```
instance/
```

Essa pasta é utilizada pelo Flask para armazenar arquivos locais da aplicação.

Para ambiente de produção, é recomendado utilizar PostgreSQL.

---

##  English Version

Web-based performance evaluation system built with Flask, designed for organizational assessment management. The application includes user authentication, evaluation records, and reporting features.

The database is automatically created on startup (SQLite), with support for migration to PostgreSQL in production environments. The system is prepared for deployment using Gunicorn as a WSGI server and Nginx as a reverse proxy.
