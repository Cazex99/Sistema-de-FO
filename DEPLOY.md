# Deployment Documentation

This document outlines the processes and configurations necessary for deploying the Sistema-de-FO application.

## Deployment Process

1. **Clone the Repository**:  
   First, clone the repository to your server:
   ```bash
   git clone https://github.com/Cazex99/Sistema-de-FO.git
   cd Sistema-de-FO
   ```

2. **Install Dependencies**:  
   It is essential to have Python 3.8+ and pip installed. You can install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:  
   Create a `.env` file in the root directory and populate it with the necessary environment variables. Example:
   ```env
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_database_url
   DEBUG=False
   ```

4. **Database Migrations**:  
   Run the following command to apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. **Collect Static Files**:  
   To serve static files with Nginx, run:
   ```bash
   python manage.py collectstatic
   ```
   Ensure you configure Nginx to serve the collected static files.

## Architecture

The application architecture is designed to modularly handle web requests:
- **Frontend**: User interface built with HTML, CSS, and JavaScript.
- **Backend**: Developed using Django REST framework, serving RESTful APIs.
- **Database**: PostgreSQL for data persistence.

## Server Configuration

### Gunicorn

Gunicorn is a Python WSGI HTTP server for UNIX. It is used to run the Django application. Here is a sample command to start the Gunicorn process:
```bash
gunicorn --bind 0.0.0.0:8000 SistemaDEFO.wsgi:application
```

### Nginx

Nginx serves as a reverse proxy to communicate with Gunicorn. Sample Nginx configuration:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/your/static/files;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/gunicorn.sock;
    }
}
```

### systemd Service

Creating a systemd service file to manage the Gunicorn process. Create a file named `gunicorn.service` in `/etc/systemd/system/`:
```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=user
Group=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/usr/local/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/your/gunicorn.sock SistemaDEFO.wsgi:application

[Install]
WantedBy=multi-user.target
```

### Environment Setup

- **Operating System**: Ubuntu 20.04 LTS (recommended)
- **Python Version**: 3.8+
- **Database**: PostgreSQL 13+

## Database Configuration

1. **Create a PostgreSQL Database**:
   ```sql
   CREATE DATABASE sistema_de_fo;
   ```

2. **Create a PostgreSQL User**:
   ```sql
   CREATE USER sistema_user WITH PASSWORD 'password';
   ```

3. **Grant Privileges**:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE sistema_de_fo TO sistema_user;
   ```

## Production Best Practices

1. **Use HTTPS**: Secure your server with an SSL certificate.
2. **Regular Backups**: Set up automated backups for your database.
3. **Monitoring**: Implement monitoring tools to track server performance and errors.
4. **Load Testing**: Perform load testing to ensure your application can handle high traffic.

By following this guide, you will have a solid foundation for deploying the Sistema-de-FO application efficiently and securely.
