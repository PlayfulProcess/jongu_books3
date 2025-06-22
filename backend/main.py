from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import json

# Load environment variables
load_dotenv()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="JonguBooks API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data models
class Character(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    personality: str
    visual_description: Optional[str] = ""
    role: Optional[str] = "supporting character"

class Page(BaseModel):
    id: Optional[str] = None
    page_number: int
    text: str
    illustration_prompt: Optional[str] = ""
    illustration_url: Optional[str] = None

class StoryGenerationRequest(BaseModel):
    title: str
    coreMessage: str
    age: str
    tone: str

class Story(BaseModel):
    id: Optional[str] = None
    title: str
    coreMessage: str = ""
    outline: str = ""
    totalWords: Optional[str] = ""
    totalPages: Optional[str] = ""
    age: str = "4-6 years"
    tone: str = "Gentle & Nurturing"
    characters: List[Character] = []
    pages: List[Page] = []
    created_at: Optional[datetime] = None
    status: str = "draft"
    author: Optional[str] = "Anonymous"

# In-memory storage (replace with PostgreSQL later)
stories = {}
# Create a dummy story for development
if not stories:
    dummy_id = str(uuid.uuid4())
    stories[dummy_id] = Story(
        id=dummy_id,
        title="The Little Bear's Big Dream",
        coreMessage="It's okay to be different and to follow your own path.",
        outline="A young bear wants to be a gardener instead of a hunter, and learns to show his family the value of his unique skills.",
        age="4-6 years",
        tone="Gentle & Nurturing",
        characters=[
            Character(id=str(uuid.uuid4()), name="Barnaby", type="Young bear", personality="Curious and gentle"),
            Character(id=str(uuid.uuid4()), name="Papa Bear", type="Wise guide", personality="Initially skeptical but loving")
        ],
        pages=[
            Page(id=str(uuid.uuid4()), page_number=1, text="Once upon a time, in a cozy den, lived a little bear named Barnaby."),
            Page(id=str(uuid.uuid4()), page_number=2, text="Unlike the other bears, Barnaby didn't dream of catching fish; he dreamt of growing flowers.")
        ],
        created_at=datetime.now()
    )

# Serve frontend at root
@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

# GPT+ Action Endpoints
@app.post("/api/gpt/create_story")
async def gpt_create_story(story: Story):
    """GPT+ calls this to create a new story"""
    story.id = str(uuid.uuid4())
    story.created_at = datetime.now()
    stories[story.id] = story
    
    return {
        "success": True,
        "data": story,
        "message": f"Story '{story.title}' created successfully!"
    }

@app.post("/api/gpt/add_character")
async def gpt_add_character(story_id: str, character: Character):
    """GPT+ calls this to add a character"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    character.id = str(uuid.uuid4())
    stories[story_id].characters.append(character)
    
    return {
        "success": True,
        "data": character,
        "message": f"Character '{character.name}' added!"
    }

@app.post("/api/gpt/add_page")
async def gpt_add_page(story_id: str, page: Page):
    """GPT+ calls this to add a page"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    page.id = str(uuid.uuid4())
    page.page_number = len(stories[story_id].pages) + 1
    stories[story_id].pages.append(page)
    
    return {
        "success": True,
        "data": page,
        "message": f"Page {page.page_number} added!"
    }

@app.post("/api/gpt/generate_characters")
async def gpt_generate_characters(req: StoryGenerationRequest):
    """Generate character ideas using AI"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        prompt = f"""
        Based on the following children's story idea, generate 3 distinct and creative characters.
        For each character, provide a name, type, and personality.
        The output should be a clean JSON array.

        Story Title: "{req.title}"
        Core Message: "{req.coreMessage}"
        Target Age: {req.age}
        Tone: {req.tone}

        JSON output format:
        [
            {{
                "name": "Character Name",
                "type": "Character Type (e.g., Brave knight, Curious fox)",
                "personality": "Personality traits (e.g., Adventurous and kind)"
            }}
        ]
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant for writing children's books."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        
        characters_json = response.choices[0].message.content
        characters = json.loads(characters_json)

        return {
            "success": True,
            "data": characters
        }

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate characters: {e}")

# Regular API Endpoints
@app.get("/api/stories")
async def get_stories():
    """Get all stories"""
    return {
        "success": True,
        "data": list(stories.values()),
        "count": len(stories)
    }

@app.post("/api/stories")
async def create_story(story: Story):
    """Create a new story from web interface"""
    story.id = str(uuid.uuid4())
    story.created_at = datetime.now()
    stories[story.id] = story
    return {
        "success": True,
        "data": story,
        "message": "Story created successfully!"
    }

@app.get("/api/stories/{story_id}")
async def get_story(story_id: str):
    """Get a specific story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    return {
        "success": True,
        "data": stories[story_id]
    }

@app.put("/api/stories/{story_id}")
async def update_story(story_id: str, story: Story):
    """Update a story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story.id = story_id
    story.created_at = stories[story_id].created_at
    stories[story_id] = story
    
    return {
        "success": True,
        "data": story,
        "message": "Story updated successfully!"
    }

@app.delete("/api/stories/{story_id}")
async def delete_story(story_id: str):
    """Delete a story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    deleted_story = stories.pop(story_id)
    return {
        "success": True,
        "message": f"Story '{deleted_story.title}' deleted successfully!"
    }

@app.post("/api/stories/{story_id}/characters")
async def add_character_to_story(story_id: str, character: Character):
    """Add a character to a story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    character.id = str(uuid.uuid4())
    stories[story_id].characters.append(character)
    
    return {
        "success": True,
        "data": character,
        "message": f"Character '{character.name}' added to story!"
    }

@app.post("/api/stories/{story_id}/pages")
async def add_page_to_story(story_id: str, page: Page):
    """Add a page to a story"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    page.id = str(uuid.uuid4())
    page.page_number = len(stories[story_id].pages) + 1
    stories[story_id].pages.append(page)
    
    return {
        "success": True,
        "data": page,
        "message": f"Page {page.page_number} added to story!"
    }

@app.get("/api/export/{story_id}/pdf")
async def export_pdf(story_id: str):
    """Export story as PDF"""
    if story_id not in stories:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # Implementation with reportlab
    # For now, return a placeholder
    return {
        "success": True,
        "message": "PDF export coming soon!",
        "story_id": story_id
    }

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "stories_count": len(stories)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 