Sistema web de avaliação de desempenho desenvolvido com Flask, voltado para gestão de avaliações organizacionais. A aplicação conta com autenticação de usuários, registro de avaliações e geração de relatórios. O banco de dados é criado automaticamente na inicialização (SQLite), com possibilidade de migração para PostgreSQL em ambiente de produção. A aplicação foi preparada para deploy utilizando Gunicorn como servidor WSGI e Nginx como proxy reverso.

Web-based performance evaluation system built with Flask, designed for organizational assessment management. The application includes user authentication, evaluation records, and reporting features. The database is automatically created on startup (SQLite), with support for migration to PostgreSQL in production environments. The system is deployed using Gunicorn as a WSGI server and Nginx as a reverse proxy.

# Sistema de Fato Observado.

##  Funcionalidades
- Autenticação
- Cadastro
- Avaliações
- Relatórios

##  Tecnologias
- Flask
- PostgreSQL / SQLite
- Gunicorn
- Nginx

##  Arquitetura

Usuário → Nginx → Gunicorn → Flask (app.py) → PostgreSQL

A aplicação segue uma arquitetura em camadas:

- Nginx: atua como proxy reverso, recebendo requisições externas
- Gunicorn: servidor WSGI responsável por executar a aplicação Flask
- Flask: backend da aplicação
- PostgreSQL: banco de dados utilizado em produção

O projeto foi inicialmente desenvolvido com SQLite e posteriormente migrado para PostgreSQL.


