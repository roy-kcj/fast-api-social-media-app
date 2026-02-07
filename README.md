# Social Media App

A full-stack Twitter-style social media application with personalized feeds, follow system, and real-time view tracking.

## Live Demo

- **Frontend:** https://fast-api-social-media-app.vercel.app
- **API Docs:** https://roy-social-api.duckdns.org/docs

## Features

- **Authentication:** JWT with access/refresh tokens
- **Posts:** Create, like, and view posts with hashtag support
- **Social:** Follow/unfollow users, personalized feed
- **Feed Algorithm:** Posts from followed users, sorted by recency, with viewed posts deprioritized
- **View Tracking:** Redis write-behind cache, batch-syncing to PostgreSQL every 5 minutes
- **Explore:** Search posts by tags, discover users

## 🛠 Tech Stack

**Backend:**

- Python, FastAPI
- PostgreSQL, Redis
- TortoiseORM, Pydantic

**Frontend:**

- TypeScript, Next.js 16, React 19
- Tailwind CSS

**DevOps:**

- Docker, Docker Compose
- AWS EC2, Nginx, Let's Encrypt SSL
- Vercel (Frontend hosting)

## Project Structure

```
fast-api-social-media-app/
├── backend/
│   ├── src/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Database models
│   │   └── schemas/      # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   ├── lib/              # API client
│   └── Dockerfile
├── scripts/
│   ├── start.sh          # Start production containers
│   ├── stop.sh           # Stop containers
│   └── logs.sh           # View logs
├── docker-compose.yml        # Development
└── docker-compose.prod.yml   # Production
```

## Quick Start (Local Development)

```bash
# Clone the repo
git clone https://github.com/roy-kcj/fast-api-social-media-app.git
cd fast-api-social-media-app

# Start everything with Docker
docker compose up

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

## API Highlights

| Endpoint                        | Description       |
| ------------------------------- | ----------------- |
| `POST /auth/register`           | Create account    |
| `POST /auth/login`              | Get JWT tokens    |
| `GET /posts/feed`               | Personalized feed |
| `POST /posts/`                  | Create post       |
| `POST /posts/{id}/like/toggle`  | Like/unlike       |
| `POST /users/{username}/follow` | Follow user       |
| `GET /users/search?q=`          | Search users      |

Full API documentation at [/docs](https://roy-social-api.duckdns.org/docs)

## Production Deployment

### Prerequisites

- Docker Hub account
- AWS EC2 instance (Ubuntu)
- Domain or DuckDNS subdomain

### 1. Build and Push Docker Images (Local Machine)

```bash
docker login

# Build and push backend
docker build -t YOUR_DOCKERHUB_USERNAME/social-api:latest ./backend
docker push YOUR_DOCKERHUB_USERNAME/social-api:latest

# Build and push frontend
docker build -t YOUR_DOCKERHUB_USERNAME/social-web:latest ./frontend
docker push YOUR_DOCKERHUB_USERNAME/social-web:latest
```

### 2. Setup EC2

```bash
# SSH into EC2
ssh -i path/to/key.pem ubuntu@YOUR_EC2_IP

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker ubuntu
sudo apt install docker-compose-plugin -y

# Logout and back in for group changes
exit
```

### 3. Deploy Application

```bash
# SSH back in
ssh -i path/to/key.pem ubuntu@YOUR_EC2_IP

# Clone repo
git clone https://github.com/roy-kcj/fast-api-social-media-app.git
cd fast-api-social-media-app

# Create environment file
cp .env.example .env.prod
nano .env.prod  # Edit with your values

# Make scripts executable and start
chmod +x scripts/*.sh
./scripts/start.sh
```

### 4. Setup SSL with Nginx (Optional but Recommended)

```bash
# Install Nginx and Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx (see docs for full config)
sudo nano /etc/nginx/sites-available/social-api

# Get SSL certificate
sudo certbot --nginx -d your-domain.duckdns.org
```

## Architecture Decisions

- **Redis Write-Behind Cache:** View tracking writes to Redis first, batch syncs to PostgreSQL every 5 minutes to reduce database load
- **JWT with Refresh Tokens:** Secure authentication with short-lived access tokens (60 min) and long-lived refresh tokens (7 days)
- **Feed Algorithm:** Posts from followed users, sorted by recency, with viewed posts deprioritized (not hidden)
- **Standalone Next.js Build:** Optimized Docker image using Next.js standalone output

## Documentation

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
