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

class StoryFoundationRequest(BaseModel):
    title: Optional[str] = ""
    coreMessage: Optional[str] = ""
    age: Optional[str] = ""
    tone: Optional[str] = ""

class ImageGenerationRequest(BaseModel):
    prompt: str

class ChatRequest(BaseModel):
    message: str
    history: List[dict]

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

@app.post("/api/gpt/generate_story_foundation")
async def gpt_generate_story_foundation(req: StoryFoundationRequest):
    """Generate or complete a story foundation using AI"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        user_prompts = []
        if req.title:
            user_prompts.append(f"The story title is '{req.title}'.")
        if req.coreMessage:
            user_prompts.append(f"The core message is '{req.coreMessage}'.")
        if req.age:
            user_prompts.append(f"The target age is {req.age}.")
        if req.tone:
            user_prompts.append(f"The tone should be {req.tone}.")

        if not user_prompts:
            user_prompts.append("The user hasn't provided any details, so create a sweet, simple story idea for a young child.")

        prompt = f"""
        A user is creating a children's story. Based on the details they've provided, complete or create a story foundation.
        If a field is already provided, either keep it or refine it. If it's empty, generate a creative value for it.

        User's input:
        - {" ".join(user_prompts)}

        Your task is to return a JSON object with the following fields fully populated: "title", "coreMessage", "outline", "age", "tone".
        The outline should be a simple, 3-5 sentence paragraph describing the story's arc.

        JSON output format:
        {{
            "title": "A complete and engaging title",
            "coreMessage": "A clear and concise life lesson",
            "outline": "A paragraph outlining the story.",
            "age": "An appropriate age group (e.g., '4-6 years')",
            "tone": "A suitable tone (e.g., 'Gentle & Nurturing')"
        }}
        """

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant for writing children's books."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )

        foundation_json = response.choices[0].message.content
        foundation = json.loads(foundation_json)

        return {
            "success": True,
            "data": foundation
        }

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate story foundation: {e}")

@app.post("/api/gpt/generate_image")
async def gpt_generate_image(req: ImageGenerationRequest):
    """Generate an image using DALL-E"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"A cute, simple, and colorful children's book illustration of: {req.prompt}. The style should be gentle and heartwarming, suitable for young children, with soft colors and clean lines.",
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response.data[0].url
        return {
            "success": True,
            "data": {"url": image_url}
        }
    except Exception as e:
        print(f"Error calling DALL-E: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {e}")

@app.post("/api/ai/chat")
async def ai_chat(req: ChatRequest):
    """General purpose AI chat assistant"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    system_prompt = {
        "role": "system",
        "content": "You are the JonguBooks Assistant, a friendly and creative partner for parents building children's stories. Your goal is to help users flesh out their ideas. You can help with brainstorming titles, suggesting core messages, creating characters, writing page content, and describing illustrations. Keep your tone encouraging and helpful. The user is currently on a specific step of the story creation process, so tailor your advice accordingly."
    }

    messages = [system_prompt] + req.history

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
        reply = response.choices[0].message.content

        return {
            "success": True,
            "reply": reply
        }
    except Exception as e:
        print(f"Error in AI chat: {e}")
        raise HTTPException(status_code=500, detail="Failed to get response from AI assistant.")

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