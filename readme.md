# E-Learning Platform

A full-stack learning management system featuring real-time course-based chat, role-based access control, and seamless content management. Built with Django REST Framework and Next.js for a scalable, modern web experience.

**[Live Demo](https://advanced-web-development-pearl.vercel.app/auth/login)** • **[API Docs](https://asadullah.alwaysdata.net/api/docs/)**

![Platform Screenshot](./frontend/public/screenshot.png)

## What It Does

- **Course Management**: Teachers create courses, students enroll and access materials
- **Real-Time Chat**: WebSocket-powered chat rooms for each course
- **Role-Based Access**: Separate permissions for teachers and students
- **File Uploads**: Secure course material storage (PDFs, images) with 10MB limit
- **Notifications**: Real-time updates for course activities

## Tech Stack

**Backend**: Django 5.2.4, Django REST Framework, Django Channels, Redis, PostgreSQL  
**Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS  
**DevOps**: Docker, GitHub Actions, Vercel (frontend), AlwaysData (backend)

## Key Technical Highlights

- **100+ concurrent WebSocket connections** using Django Channels + Redis channel layers
- **25+ RESTful API endpoints** with OpenAPI/Swagger documentation
- **Service layer architecture** separating business logic from views
- **Full test coverage** for critical features
- **Type-safe frontend** with TypeScript + Zod validation
- **CI/CD pipeline** with GitHub Actions for automated deployment

## Quick Start

### Prerequisites

- Python 3.10+, Node.js 20+, Redis

### Run Locally

**Backend:**

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
redis-server  # In separate terminal
daphne -p 8000 elearning_project.asgi:application
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

### Or Use Docker

```bash
cd backend
docker-compose up
```

## Project Structure

```
backend/
  ├── elearning/          # Main app
  │   ├── models.py       # Database models
  │   ├── views/          # API viewsets
  │   ├── serializers/    # Data serialization
  │   ├── services/       # Business logic layer
  │   ├── consumers/      # WebSocket consumers
  │   └── tests/          # Test suite
  └── elearning_project/  # Django settings

frontend/
  ├── src/
  │   ├── app/            # Next.js App Router
  │   ├── components/      # React components
  │   ├── services/        # API layer
  │   └── store/           # Zustand state management
```

## Security & Architecture

- **RBAC**: Role-based permissions with custom policy classes
- **Private file storage** for course materials
- **CSRF + CORS** protection configured
- **Input validation** at serializer level
- **WebSocket authentication** with session management
- **Database optimization** with select_related/prefetch_related

---

<details>
<summary><b>Detailed Feature List (Click to Expand)</b></summary>

### Course Management

- Course creation with lessons and materials
- Enrollment system with tracking
- File uploads with preview support (PDF, images, text)
- Rating and feedback system
- Student access restrictions by teacher

### Real-Time Communication

- Course-based chat rooms
- WebSocket real-time messaging
- Role-based participant management
- Persistent message history

### User Management

- Student/Teacher role separation
- Profile picture uploads
- User status system (online/offline)
- Secure authentication with sessions

### Notifications

- Real-time WebSocket notifications
- Multiple notification types
- Mark as read/unread functionality

</details>

<details>
<summary><b>Testing & Documentation (Click to Expand)</b></summary>

### Run Tests

```bash
cd backend
python manage.py test
```

Test coverage includes:

- Model tests
- View/API tests
- Permission tests
- Service layer tests
- WebSocket integration tests

### API Documentation

Once backend is running:

- **Swagger UI**: `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://localhost:8000/api/schema/redoc/`

</details>

<details>
<summary><b>Environment Variables (Click to Expand)</b></summary>

**Backend** (`.env`):

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://127.0.0.1:6379
DATABASE_URL=postgresql://user:pass@localhost/dbname  # Optional
```

**Frontend** (`.env`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

</details>

---

## Why This Project?

This portfolio project demonstrates production-ready full-stack development skills:

- **Real-time systems**: WebSocket architecture supporting 100+ concurrent connections
- **Scalable architecture**: Service layer pattern with separation of concerns
- **Type safety**: TypeScript + Zod validation throughout the frontend
- **Testing**: Comprehensive test suite covering models, APIs, permissions, and WebSocket integration
- **DevOps**: CI/CD pipelines, containerization, and multi-platform deployment

## Author

**Asadullah Jan**  
[LinkedIn](https://linkedin.com/in/asadullah-jan-b1949922b/) • [Portfolio](https://quiet-phoenix-a6fa02.netlify.app/) • [Email](mailto:asadullah.jan@outlook.com) • [WhatsApp](https://wa.me/923160123456)

---

**License**: Portfolio project available for review purposes
