#!/bin/bash

case $1 in
  "build")
    echo "Building Docker image for web service..."
    docker-compose build web
    ;;
  "start")
    echo "Starting local development environment with Daphne ASGI server (WebSocket support)..."
    docker-compose up web redis
    ;;
  "runserver")
    echo "Starting local development environment with Django runserver (no WebSocket support)..."
    # Stop current service and restart with runserver
    docker-compose down
    docker-compose run --rm --service-ports web sh -c "
      python manage.py collectstatic --noinput &&
      python manage.py migrate &&
      python manage.py runserver 0.0.0.0:8000
    "
    ;;
  "rebuild")
    echo "Rebuilding Docker image without cache..."
    docker-compose build --no-cache web
    echo "Rebuild complete! Now run: ./dev.sh start"
    ;;
  "stop")
    echo "Stopping local development environment..."
    docker-compose down
    ;;
  "restart")
    echo "Restarting local development environment with Daphne..."
    docker-compose down
    docker-compose up web redis --build
    ;;
  "migrate")
    echo "Running migrations..."
    docker-compose run --rm web python manage.py migrate
    ;;
  "makemigrations")
    echo "Creating migrations..."
    docker-compose run --rm web python manage.py makemigrations
    ;;
  "shell")
    echo "Opening Django shell..."
    docker-compose run --rm web python manage.py shell
    ;;
  "logs")
    echo "Showing logs..."
    docker-compose logs -f
    ;;
  "clean")
    echo "Cleaning up Docker..."
    docker-compose down -v
    docker system prune -f
    ;;
  *)
    echo "Usage: ./dev.sh {start|runserver|rebuild|stop|restart|migrate|makemigrations|shell|logs|clean}"
    echo ""
    echo "Commands:"
    echo "  start           - Start with Daphne ASGI server (port 8000, WebSocket support)"
    echo "  runserver       - Start with Django runserver (port 8000, no WebSocket support)"
    echo "  rebuild         - Rebuild Docker image without cache (faster than clean)"
    echo "  stop            - Stop development environment"
    echo "  restart         - Restart with Daphne"
    echo "  migrate         - Run database migrations"
    echo "  makemigrations  - Create new migrations"
    echo "  shell           - Open Django shell"
    echo "  logs            - Show container logs"
    echo "  clean           - Clean up Docker containers and volumes (slow)"
    echo ""
    echo "Note: Use 'start' for normal development (WebSocket support)"
    echo "      Use 'runserver' only if you don't need WebSockets"
    echo "      Use 'rebuild' to force rebuild without full clean"
    ;;
esac
