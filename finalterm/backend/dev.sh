#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    # First, try to find python3
    if command -v python3; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        if [[ $? -eq 0 && $PYTHON_VERSION == *"Python"* ]]; then
            print_success "Using Python: $PYTHON_VERSION"
            return 0
        fi
    fi
    
    # If python3 doesn't work, try python
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
        if [[ $? -eq 0 && $PYTHON_VERSION == *"Python"* ]]; then
            print_success "Using Python: $PYTHON_VERSION"
            return 0
        fi
    fi
    
    print_error "Python is not installed or not working properly."
    print_error "Please install Python 3.8+ and ensure it's in your PATH."
    exit 1
}

# Create virtual environment
create_venv() {
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        print_status "Creating virtual environment in $SCRIPT_DIR/venv..."
        $PYTHON_CMD -m venv "$SCRIPT_DIR/venv"
        print_success "Virtual environment created successfully!"
    else
        print_warning "Virtual environment already exists in $SCRIPT_DIR/venv."
    fi
}

# Activate virtual environment
activate_venv() {
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows Git Bash
        source "$SCRIPT_DIR/venv/Scripts/activate"
    else
        # Unix/Linux/macOS
        source "$SCRIPT_DIR/venv/bin/activate"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment activated!"
        print_status "Python path: $(which python)"
    else
        print_error "Failed to activate virtual environment!"
        exit 1
    fi
}

# Install requirements
install_requirements() {
    print_status "Installing requirements..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Requirements installed successfully!"
    else
        print_error "Failed to install requirements!"
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    python manage.py migrate
    
    if [ $? -eq 0 ]; then
        print_success "Migrations completed successfully!"
    else
        print_error "Failed to run migrations!"
        exit 1
    fi
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    
    if [ $? -eq 0 ]; then
        print_success "Static files collected successfully!"
    else
        print_error "Failed to collect static files!"
        exit 1
    fi
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    activate_venv
    python manage.py createsuperuser
}

# Main setup function
setup() {
    print_status "Setting up local development environment..."
    check_python
    create_venv
    activate_venv
    install_requirements
    run_migrations
    collect_static
    print_success "Setup completed! You can now run: ./dev.sh runserver or ./dev.sh daphne"
}

# Run Django development server
run_server() {
    print_status "Starting Django development server..."
    activate_venv
    python manage.py runserver 0.0.0.0:8000
}

# Run with Daphne (ASGI server with WebSocket support)
run_daphne() {
    print_status "Starting Daphne ASGI server (WebSocket support)..."
    activate_venv
    daphne -b 0.0.0.0 -p 8000 elearning_project.asgi:application
}

# Run tests
run_tests() {
    print_status "Running tests..."
    activate_venv
    if [ -n "$1" ]; then
        echo "Running tests for: $1"
        python manage.py test "$1"
    else
        echo "Running all tests..."
        python manage.py test
    fi
}

# Make migrations
make_migrations() {
    print_status "Creating migrations..."
    activate_venv
    python manage.py makemigrations
}

# Shell
shell() {
    print_status "Opening Django shell..."
    activate_venv
    python manage.py shell
}

# Clean up
clean() {
    print_status "Cleaning up..."
    if [ -d "venv" ]; then
        rm -rf venv
        print_success "Virtual environment removed!"
    fi
    if [ -d "__pycache__" ]; then
        find . -type d -name "__pycache__" -exec rm -rf {} +
        print_success "Python cache cleaned!"
    fi
    if [ -d "staticfiles" ]; then
        rm -rf staticfiles
        print_success "Static files cleaned!"
    fi
}

# Show help
show_help() {
    echo "Usage: ./dev.sh {setup|runserver|daphne|test [test_path]|migrate|makemigrations|shell|clean|help}"
    echo ""
    echo "Commands:"
    echo "  create_superuser - Create superuser"
    echo "  check_python   - Check Python version"
    echo "  setup          - Create venv, install requirements, run migrations"
    echo "  runserver      - Start Django development server (port 8000)"
    echo "  daphne         - Start with Daphne ASGI server (WebSocket support)"
    echo "  test [path]    - Run Django tests (optional: specific test path)"
    echo "  migrate        - Run database migrations"
    echo "  makemigrations - Create new migrations"
    echo "  shell          - Open Django shell"
    echo "  clean          - Remove venv, cache, and static files"
    echo "  help           - Show this help message"
    echo ""
    echo "Note: Use 'setup' first time to initialize environment"
    echo "      Virtual environment creation automatically installs requirements"
    echo "      Use 'runserver' for normal development"
    echo "      Use 'daphne' for WebSocket support"
    echo "      Test path format: app_name.test_file.TestClass.test_method"
}

# Main script logic
case $1 in
    "create_superuser")
        create_superuser
        ;;
    "check_python")
        check_python
        ;;
    "setup")
        setup
        ;;
    "runserver")
        run_server
        ;;
    "daphne")
        run_daphne
        ;;
    "test")
        run_tests "$2"
        ;;
    "migrate")
        activate_venv
        run_migrations
        ;;
    "makemigrations")
        make_migrations
        ;;
    "shell")
        shell
        ;;
    "clean")
        clean
        ;;
    "help"|*)
        show_help
        ;;
esac
