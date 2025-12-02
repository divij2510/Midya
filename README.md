# Midya - Social Activity Feed

A Django REST Framework based social activity feed application with user authentication, posts, likes, follows, blocks, and activity tracking.

## Features

- **User Management**: Signup, login, and user profiles with roles (Owner, Admin, Regular)
- **Posts**: Create, view, update, and delete posts with optional images
- **Social Features**: Like posts, follow/unfollow users, block users
- **Activity Feed**: Real-time activity feed showing all network activities
- **Permissions**: Role-based access control (Owner > Admin > Regular)
- **REST API**: Complete RESTful API for all features
- **Frontend**: Dark-themed Django templates for testing

## Setup

### Prerequisites

- Python 3.11+
- Virtual environment

### Installation

1. Activate the virtual environment:
```bash
# Windows
.\inkle_proj_env\Scripts\activate

# Linux/Mac
source inkle_proj_env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
cd midya
python manage.py makemigrations
python manage.py migrate
```

4. Create an owner user:
```bash
python manage.py create_owner --username owner --email owner@midya.com --password owner123
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Collect static files:
```bash
python manage.py collectstatic --noinput
```

7. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get token
- `GET /api/auth/profile/` - Get current user profile

### Users
- `GET /api/auth/users/` - List all users
- `GET /api/auth/users/{id}/` - Get user details
- `DELETE /api/auth/users/{id}/` - Delete user (Admin/Owner only)

### Admin Management (Owner only)
- `POST /api/auth/admins/` - Create admin
- `GET /api/auth/admins/` - List admins
- `DELETE /api/auth/admins/{id}/` - Remove admin

### Posts
- `GET /api/posts/` - List all posts
- `POST /api/posts/` - Create a post
- `GET /api/posts/{id}/` - Get post details
- `PUT /api/posts/{id}/` - Update post
- `DELETE /api/posts/{id}/` - Delete post (Owner/Admin/Owner of post)
- `POST /api/posts/{id}/like/` - Like a post
- `DELETE /api/posts/{id}/like/` - Unlike a post

### Follows
- `GET /api/follows/` - List user's follows
- `POST /api/follows/` - Follow a user
- `DELETE /api/follows/{id}/` - Unfollow a user

### Blocks
- `GET /api/blocks/` - List blocked users
- `POST /api/blocks/` - Block a user
- `DELETE /api/blocks/{id}/` - Unblock a user

### Activities
- `GET /api/activities/` - Get activity feed
- `GET /api/activities/{id}/` - Get activity details

### Likes
- `GET /api/likes/` - List user's likes
- `DELETE /api/likes/{id}/` - Delete like (Admin only)

## Postman Collection

Import `Midya_API.postman_collection.json` into Postman to test all API endpoints.

**Setup in Postman:**
1. Import the collection
2. Set the `base_url` variable (default: `http://localhost:8000`)
3. Login to get the `auth_token` (automatically set by the Login request)
4. Use the token in subsequent requests

## Docker Deployment

### Build and Run with Docker

```bash
docker build -t midya .
docker run -p 8000:8000 midya
```

### Deploy to Render

1. Push your code to a Git repository
2. Connect the repository to Render
3. Render will automatically detect the `Dockerfile` or `render.yaml`
4. Set environment variables if needed
5. Deploy

## User Roles

- **Owner**: Full access, can create/delete admins, delete users/posts/likes
- **Admin**: Can delete users/posts/likes, cannot manage other admins
- **Regular**: Can create posts, like, follow, block users

## Activity Feed

The activity feed shows:
- Post creation: "ABC made a post"
- User follows: "DEF followed ABC"
- Post likes: "PQR liked ABC's post"
- User deletion: "User deleted by 'Owner'"
- Post deletion: "Post deleted by 'Admin'"

## Blocking Users

When a user blocks another user:
- All posts from the blocked user become invisible
- Any existing follows are removed
- Any likes on blocked user's posts are removed

## Development

### Project Structure

```
midya/
├── accounts/          # User management app
├── social/            # Social features app
├── templates/         # Django templates
├── static/           # Static files (CSS, JS)
├── media/            # User uploaded files
├── Dockerfile        # Docker configuration
├── requirements.txt  # Python dependencies
└── manage.py        # Django management script
```

## License

This project is for educational purposes.

