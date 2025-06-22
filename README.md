# JonguBooks - Create Personalized Children's Stories

A beautiful web application for parents to create personalized children's books with custom characters and meaningful lessons.

## 🎯 Vision

**Short Term**: Launch a beautiful, simple tool where parents can craft personalized children's books - with or without AI assistance.

**Long Term Goals**:
- Build a library of parent-created stories that can inspire others
- Create a community where parents share wisdom through storytelling
- Develop story templates for specific childhood challenges
- Make every story easily shareable on social media with beautiful preview cards
- Expand to other mindful parenting tools that align with the Jongu philosophy

## 🏗️ Technical Architecture

- **Frontend**: Single HTML file with Tailwind CSS and vanilla JavaScript
- **Backend**: FastAPI for modern, fast API development
- **Storage**: In-memory storage (PostgreSQL planned for Phase 2)
- **Deployment**: Docker for easy deployment anywhere

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/jongubooks.git
   cd jongubooks
   ```

2. **Set up environment variables**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your API keys
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Visit the application**
   Open http://localhost:8000 in your browser

### Option 2: Local Development

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Run the backend**
   ```bash
   python main.py
   ```

4. **Serve the frontend**
   ```bash
   # You can use any static file server
   cd ../frontend
   python -m http.server 8080
   ```

## 📁 Project Structure

```
jongubooks/
├── frontend/
│   └── index.html          # Complete UI with all functionality
├── backend/
│   ├── main.py            # FastAPI backend
│   ├── requirements.txt   # Python dependencies
│   └── env.example        # Environment variables template
├── docker-compose.yml     # Docker orchestration
├── Dockerfile            # Container setup
├── README.md            # This file
└── static/              # Static assets (images, etc.)
    └── og-images/       # Social media previews
```

## 🎨 Features

### Phase 1: Core MVP ✅
- [x] Beautiful, responsive frontend
- [x] Character creation (name, personality, type)
- [x] Story foundation (title, theme, lesson, outline)
- [x] Page creation with text
- [x] Basic story viewing
- [x] In-memory storage
- [x] Docker setup for easy deployment

### Phase 2: Storage & Export (Planned)
- [ ] PostgreSQL for data persistence
- [ ] PDF export with ReportLab
- [ ] Image upload handling
- [ ] Social media preview generation

### Phase 3: AI Integration (Planned)
- [ ] GPT+ custom actions
- [ ] Direct OpenAI integration for paid users
- [ ] DALL-E integration for illustrations
- [ ] AI story suggestions

### Phase 4: Ghost CMS Integration (Planned)
- [ ] User authentication via Ghost
- [ ] Subscription tiers
- [ ] User story library
- [ ] Community features

### Phase 5: Social Features (Planned)
- [ ] Share stories with custom URLs
- [ ] Social media previews
- [ ] Story templates marketplace
- [ ] Parent community

## 🔐 Next Steps & Multi-User Authentication

### Current Limitations (June 2024)
**⚠️ CRITICAL: The current application is NOT ready for multiple simultaneous users**

#### Data Flow Issues:
- **Shared Memory Storage**: All users share the same in-memory `stories` dictionary
- **No User Isolation**: User A's stories are visible to User B
- **Race Conditions**: Multiple users editing simultaneously can corrupt data
- **Session Confusion**: All users see the same dummy story on startup
- **No Persistence**: Server restart = complete data loss

#### Current Data Flow:
```
User A Session          User B Session
     ↓                       ↓
Browser (Frontend)    Browser (Frontend)
     ↓                       ↓
HTTP Requests         HTTP Requests
     ↓                       ↓
FastAPI Backend       FastAPI Backend
     ↓                       ↓
Shared Memory Dict    Shared Memory Dict
  stories = {}          stories = {}
     ↓                       ↓
SAME DATA STORAGE     SAME DATA STORAGE
```

### Required Changes for Multi-User Support:

#### 1. Database Architecture
```sql
-- SQLite tables for user isolation
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP
);

CREATE TABLE stories (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    title TEXT,
    core_message TEXT,
    outline TEXT,
    age TEXT,
    tone TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE characters (
    id TEXT PRIMARY KEY,
    story_id TEXT,
    name TEXT,
    type TEXT,
    personality TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(id)
);

CREATE TABLE pages (
    id TEXT PRIMARY KEY,
    story_id TEXT,
    page_number INTEGER,
    text TEXT,
    FOREIGN KEY (story_id) REFERENCES stories(id)
);
```

#### 2. Authentication System
- **JWT Token Authentication** for stateless sessions
- **User Registration/Login** endpoints
- **Password Hashing** with bcrypt
- **Protected API Routes** requiring authentication

#### 3. API Changes
```python
# Current (problematic)
@app.get("/api/stories")
async def get_stories():
    return list(stories.values())  # All users see all stories

# Required (user-isolated)
@app.get("/api/stories")
async def get_stories(user_id: str):
    return get_user_stories(user_id)  # Only user's stories
```

#### 4. Frontend Changes
- **Login/Register Forms**
- **User Session Management**
- **User-Specific Story Loading**
- **Authentication Headers** on all API calls

### Implementation Priority:
1. **SQLite Database** with user and story tables
2. **Basic Authentication** (email/password)
3. **User-Specific API Endpoints**
4. **Frontend Login System**
5. **Session Management**

### Deployment Considerations:
- **SQLite** works perfectly on Render/Railway/Vercel
- **No external database** needed initially
- **Simple authentication** without OAuth complexity
- **Environment variables** for JWT secrets

### Temporary Solution:
- **Removed Save Button** from frontend to prevent data confusion
- **Focus on UI/UX** development while planning authentication
- **Single-user testing** only until multi-user ready

## 🔧 API Endpoints

### Story Management
- `GET /api/stories` - List all stories
- `POST /api/stories` - Create a new story
- `GET /api/stories/{id}` - Get a specific story
- `PUT /api/stories/{id}` - Update a story
- `DELETE /api/stories/{id}` - Delete a story

### Characters
- `POST /api/stories/{id}/characters` - Add character to story

### Pages
- `POST /api/stories/{id}/pages` - Add page to story

### Export
- `GET /api/export/{id}/pdf` - Export story as PDF (coming soon)

### Health Check
- `GET /health` - API health status

## 🎯 Development Guidelines

1. **Start Simple**: Get Phase 1 working first
2. **Test with Real Parents**: Friends are the QA team
3. **Mobile First**: Parents use phones
4. **Keep It Fast**: FastAPI lives up to its name
5. **Document Everything**: Future me needs help

## 🤝 Contributing

This is a personal project focused on helping parents create magical moments with their children. Every line of code serves that purpose.

## 📝 License

This project is for personal use and helping parents create meaningful stories for their children.

## 🚀 Deployment

### Simple Start (Phase 1)
```bash
docker-compose up
```

### Production (Later)
- **Frontend**: Vercel/Netlify (static hosting)
- **Backend**: Railway/Fly.io (FastAPI)
- **Database**: Supabase/Neon (PostgreSQL)
- **Images**: Cloudinary
- **Domain**: jongubooks.com

---

**Remember**: This is about helping parents create magical moments with their children. Every line of code serves that purpose. Let's build something beautiful together! 🚀 