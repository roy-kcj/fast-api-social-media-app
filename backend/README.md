# Social Media API - Backend

A RESTful API for a Twitter-style social media platform built with FastAPI.

## Features

- **Authentication:** JWT with access/refresh tokens, bcrypt password hashing
- **Users:** Registration, profiles, follow/unfollow, user search
- **Posts:** CRUD operations, hashtag extraction, likes
- **Feed:** Personalized feed with view tracking and Redis caching
- **Tags:** Auto-extraction from post body, trending tags

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (production), SQLite (development)
- **Cache:** Redis (view tracking, write-behind cache)
- **ORM:** TortoiseORM
- **Auth:** python-jose (JWT), bcrypt

## API Endpoints

### Authentication

| Method | Endpoint         | Description                 |
| ------ | ---------------- | --------------------------- |
| POST   | `/auth/register` | Create new account          |
| POST   | `/auth/login`    | Get access & refresh tokens |
| POST   | `/auth/refresh`  | Refresh access token        |
| GET    | `/auth/me`       | Get current user profile    |

### Users

| Method | Endpoint                      | Description      |
| ------ | ----------------------------- | ---------------- |
| GET    | `/users/{username}`           | Get user profile |
| GET    | `/users/search?q=`            | Search users     |
| POST   | `/users/{username}/follow`    | Follow user      |
| DELETE | `/users/{username}/follow`    | Unfollow user    |
| GET    | `/users/{username}/followers` | Get followers    |
| GET    | `/users/{username}/following` | Get following    |

### Posts

| Method | Endpoint                  | Description                  |
| ------ | ------------------------- | ---------------------------- |
| GET    | `/posts/`                 | List posts (with tag filter) |
| GET    | `/posts/feed`             | Personalized feed            |
| POST   | `/posts/`                 | Create post                  |
| GET    | `/posts/{id}`             | Get single post              |
| PATCH  | `/posts/{id}`             | Update post                  |
| DELETE | `/posts/{id}`             | Delete post                  |
| POST   | `/posts/{id}/like/toggle` | Toggle like                  |
| POST   | `/posts/views`            | Track viewed posts           |

### Tags

| Method | Endpoint         | Description       |
| ------ | ---------------- | ----------------- |
| GET    | `/tags/`         | List all tags     |
| GET    | `/tags/trending` | Get trending tags |

## Local Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload

# Access API docs
# http://localhost:8000/docs
```

## Environment Variables

```env
DATABASE_URL=sqlite://db.sqlite3
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=true
FRONTEND_URL=http://localhost:3000
```

## Testing

```bash
# Run all tests
pytest src/tests/ -v

# Run with coverage
pytest src/tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest src/tests/test_auth.py -v

# Run specific test
pytest src/tests/test_auth.py::TestLogin::test_login_success -v

# Stop on first failure
pytest src/tests/ -v -x
```

## Project Structure

```
backend/
├── src/
│   ├── core/           # Config, security, database
│   ├── models/         # TortoiseORM models
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── tasks/          # Background tasks
│   └── tests/          # Pytest tests
├── Dockerfile
├── requirements.txt
└── README.md
```

## Architecture Highlights

- **View Tracking:** Redis write-behind cache batches view data, syncs to PostgreSQL every 5 minutes
- **Feed Algorithm:** Posts from followed users, sorted by recency, viewed posts deprioritized
- **Hashtag Extraction:** Automatically parses `#hashtags` from post body and links to Tag model
