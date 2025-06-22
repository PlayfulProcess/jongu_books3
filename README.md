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