# SecurityGuard

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.11+-blue) ![Django](https://img.shields.io/badge/Django-5.2.7-green)

A focused, production-ready Security Guard Management system to manage guards, shifts, incidents, and site assignments. Designed for scalability with Django + Channels for real-time updates and Celery for background tasks.

## Key features
- Guard roster and shift scheduling
- Site and checkpoint management
- Incident reporting with media attachments
- Real-time notifications (WebSockets)
- Authentication and JWT-based API
- Exportable reports (CSV/PDF)
- Background jobs with Celery + Redis
- Docker-friendly for simple deploys

## Technologies
- Django 5.2.x, Django REST Framework
- Channels (WebSockets) and Daphne
- Celery + Redis for asynchronous tasks
- PostgreSQL recommended for production
- Optional Docker / docker-compose

## Quickstart (local)
1. Clone the repo:
    git clone <repo-url> && cd SecurityGuard
2. Create and activate a virtualenv:
    python -m venv .venv
    source .venv/bin/activate
3. Install dependencies:
    pip install -r requirements.txt
4. Create environment variables (example .env):
    SECRET_KEY=replace-me
    DEBUG=True
    DATABASE_URL=sqlite:///db.sqlite3
    REDIS_URL=redis://localhost:6379/0
5. Run migrations and start:
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Start channels (if enabled):
    daphne -b 0.0.0.0 -p 8001 SecurityGuard.asgi:application

Start Celery worker:
    celery -A SecurityGuard worker -l info

## Docker (optional)
- Provide a docker-compose.yml linking web, redis, and db.
- Build and run:
    docker-compose up --build

## Configuration
- Use python-decouple or environment variables for secrets and DB settings.
- JWT configuration for API auth via djangorestframework-simplejwt.
- Configure Channels and Daphne for WebSocket endpoints.

## Testing
- Run unit tests:
    python manage.py test

## Contributing
- Open issues for features or bugs.
- Follow the code style, run tests locally, and submit PRs with descriptive titles.

## License
MIT — see LICENSE file.

## Notes
- See requirements.txt for exact package versions. For production, use PostgreSQL, configure HTTPS, and rotate SECRET_KEY and credentials.

# Security-Workforce-Management
