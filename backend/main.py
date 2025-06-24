from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv
import openai
import json
import re

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
    title: Optional[str] = ""
    coreMessage: Optional[str] = ""
    age: Optional[str] = ""
    tone: Optional[str] = ""
    story_context: Optional[dict] = None

class StoryFoundationRequest(BaseModel):
    title: Optional[str] = ""
    coreMessage: Optional[str] = ""
    age: Optional[str] = ""
    tone: Optional[str] = ""
    story_context: Optional[dict] = None

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

class PageTextGenerationRequest(BaseModel):
    story_title: str
    core_message: str
    page_number: int
    total_pages: Optional[int]
    previous_text: Optional[str] = None
    story_context: Optional[dict] = None

class AllPagesGenerationRequest(BaseModel):
    story_title: str
    core_message: str
    total_pages: Optional[int] = 12
    age: Optional[str] = "4-6 years"
    tone: Optional[str] = "Gentle & Nurturing"
    story_context: Optional[dict] = None

class PageImageGenerationRequest(BaseModel):
    story_context: dict
    page_number: int

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
        # Use story_context if provided
        if req.story_context:
            ctx = req.story_context
            prompt_parts = []
            if ctx.get('title'):
                prompt_parts.append(f"Story Title: '{ctx['title']}'")
            if ctx.get('coreMessage'):
                prompt_parts.append(f"Core Message: '{ctx['coreMessage']}'")
            if ctx.get('age'):
                prompt_parts.append(f"Target Age: {ctx['age']}")
            if ctx.get('storyTone'):
                prompt_parts.append(f"Tone: {ctx['storyTone']}")
            if ctx.get('outline'):
                prompt_parts.append(f"Outline: {ctx['outline']}")
            if ctx.get('pages'):
                prompt_parts.append(f"The story has {len(ctx['pages'])} pages.")
            if not prompt_parts:
                prompt_parts.append("No details provided. Invent a sweet, simple story idea for a young child.")
            prompt = f"""
            Based on the following children's story idea, generate 3 distinct and creative characters.
            For each character, provide a name, type, and personality.
            The output should be a clean JSON array.

            {' '.join(prompt_parts)}

            JSON output format:
            [
                {{
                    "name": "Character Name",
                    "type": "Character Type (e.g., Brave knight, Curious fox)",
                    "personality": "Personality traits (e.g., Adventurous and kind)"
                }}
            ]
            """
        else:
            # If no context at all, instruct AI to invent everything
            prompt = """
            Invent a sweet, simple story idea for a young child and generate 3 distinct and creative characters.
            For each character, provide a name, type, and personality.
            The output should be a clean JSON array.

            JSON output format:
            [
                {
                    "name": "Character Name",
                    "type": "Character Type (e.g., Brave knight, Curious fox)",
                    "personality": "Personality traits (e.g., Adventurous and kind)"
                }
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
        print(f"OpenAI response: {characters_json}")  # Debug log
        
        # Clean the response and try to parse JSON
        characters_json = characters_json.strip()
        if not characters_json:
            raise Exception("OpenAI returned an empty response")
            
        # Try to extract JSON if it's wrapped in markdown
        if characters_json.startswith("```json"):
            characters_json = characters_json.split("```json")[1]
        if characters_json.endswith("```"):
            characters_json = characters_json.rsplit("```", 1)[0]
        characters_json = characters_json.strip()
        
        characters = json.loads(characters_json)

        return {
            "success": True,
            "data": characters
        }

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate characters: {e}")

@app.post("/api/gpt/generate_page_text")
async def gpt_generate_page_text(req: PageTextGenerationRequest):
    """Generate text for a specific story page using AI"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        # Use story_context if provided
        if req.story_context:
            ctx = req.story_context
            prompt_parts = []
            if ctx.get('title'):
                prompt_parts.append(f"Story Title: '{ctx['title']}'")
            if ctx.get('coreMessage'):
                prompt_parts.append(f"Core Message: '{ctx['coreMessage']}'")
            if ctx.get('storyTone'):
                prompt_parts.append(f"Tone: {ctx['storyTone']}")
            if ctx.get('targetAge'):
                prompt_parts.append(f"Target Age: {ctx['targetAge']}")
            if ctx.get('outline'):
                prompt_parts.append(f"Outline: {ctx['outline']}")
            if ctx.get('characters'):
                char_descriptions = []
                for char in ctx['characters']:
                    desc = f"Name: {char.get('name', '')}, Personality: {char.get('personality', '')}, Visual: {char.get('visualDescription', '')}"
                    char_descriptions.append(desc)
                if char_descriptions:
                    prompt_parts.append("Characters: " + "; ".join(char_descriptions))
            if ctx.get('pages'):
                prompt_parts.append(f"The story has {len(ctx['pages'])} pages.")
            if req.page_number:
                prompt_parts.append(f"This is for page {req.page_number} of roughly {ctx.get('totalPages', ctx.get('pages') and len(ctx['pages']) or 12)} pages.")
            if req.previous_text:
                prompt_parts.append(f"The text of the previous page was: '{req.previous_text}'")
            prompt = f"""
            You are a gentle and creative author of children's books.\nBased on the following story details, write the text for the current page.\nKeep the language simple, engaging, and appropriate for a young child ({ctx.get('targetAge', '4-6 years')}).\nThe text should be a short paragraph, around 2-4 sentences.\n\nContext:\n- {' '.join(prompt_parts)}\n\nGenerate only the text for the current page.\n"""
        else:
            prompt_context = [
                f"Story Title: \"{req.story_title}\"",
                f"Core Message: \"{req.core_message}\"",
                f"This is for page {req.page_number} of roughly {req.total_pages or '12'} pages."
            ]
            if req.previous_text:
                prompt_context.append(f"The text of the previous page was: \"{req.previous_text}\"")
            prompt = f"""
            You are a gentle and creative author of children's books.\nBased on the following story details, write the text for the current page.\nKeep the language simple, engaging, and appropriate for a young child (4-6 years old).\nThe text should be a short paragraph, around 2-4 sentences.\n\nContext:\n- {' '.join(prompt_context)}\n\nGenerate only the text for the current page.\n"""

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative assistant for writing children's books."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        
        page_text = response.choices[0].message.content.strip()

        return {
            "success": True,
            "data": {"text": page_text}
        }

    except Exception as e:
        print(f"Error calling OpenAI for page text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate page text: {e}")

@app.post("/api/gpt/generate_all_pages")
async def gpt_generate_all_pages(req: AllPagesGenerationRequest):
    """Generate all pages for a story using AI"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        # Use story_context if provided
        if req.story_context:
            ctx = req.story_context
            prompt_parts = []
            if ctx.get('title'):
                prompt_parts.append(f"Story Title: '{ctx['title']}'")
            if ctx.get('coreMessage'):
                prompt_parts.append(f"Core Message: '{ctx['coreMessage']}'")
            if ctx.get('age'):
                prompt_parts.append(f"Target Age: {ctx['age']}")
            if ctx.get('storyTone'):
                prompt_parts.append(f"Tone: {ctx['storyTone']}")
            if ctx.get('outline'):
                prompt_parts.append(f"Outline: {ctx['outline']}")
            if ctx.get('characters'):
                char_descriptions = []
                for char in ctx['characters']:
                    desc = f"Name: {char.get('name', '')}, Personality: {char.get('personality', '')}, Visual: {char.get('visualDescription', '')}"
                    char_descriptions.append(desc)
                if char_descriptions:
                    prompt_parts.append("Characters: " + "; ".join(char_descriptions))
            if ctx.get('pages'):
                prompt_parts.append(f"The story has {len(ctx['pages'])} pages.")
            prompt = f"""
            You are a gentle and creative author of children's books.
            Based on the following story details, create a complete story with {ctx.get('totalPages', 12)} pages.
            Each page should have engaging text appropriate for {ctx.get('targetAge', '4-6 years')} children with a {ctx.get('storyTone', 'Gentle & Nurturing')} tone.

            {' '.join(prompt_parts)}

            Generate a JSON array with {ctx.get('totalPages', 12)} pages. Each page should have:
            - page_number: the page number (1, 2, 3, etc.)
            - text: 2-4 sentences of engaging story text
            - illustration_prompt: a brief description for creating an illustration

            JSON output format:
            [
                {{
                    "page_number": 1,
                    "text": "Once upon a time...",
                    "illustration_prompt": "A cozy scene showing..."
                }},
                {{
                    "page_number": 2,
                    "text": "The next day...",
                    "illustration_prompt": "A bright morning scene..."
                }}
            ]
            """
        else:
            prompt = f"""
            You are a gentle and creative author of children's books.
            Based on the following story details, create a complete story with {req.total_pages} pages.
            Each page should have engaging text appropriate for {req.age} children with a {req.tone} tone.

            Story Title: "{req.story_title}"
            Core Message: "{req.core_message}"
            Target Age: {req.age}
            Tone: {req.tone}
            Number of Pages: {req.total_pages}

            Generate a JSON array with {req.total_pages} pages. Each page should have:
            - page_number: the page number (1, 2, 3, etc.)
            - text: 2-4 sentences of engaging story text
            - illustration_prompt: a brief description for creating an illustration

            JSON output format:
            [
                {{
                    "page_number": 1,
                    "text": "Once upon a time...",
                    "illustration_prompt": "A cozy scene showing..."
                }},
                {{
                    "page_number": 2,
                    "text": "The next day...",
                    "illustration_prompt": "A bright morning scene..."
                }}
            ]
            """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative assistant for writing children's books."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )
        
        pages_json = response.choices[0].message.content
        print(f"OpenAI response for pages: {pages_json}")  # Debug log
        
        # Clean the response and try to parse JSON
        pages_json = pages_json.strip()
        if not pages_json:
            raise Exception("OpenAI returned an empty response")
            
        # Try to extract JSON if it's wrapped in markdown
        if pages_json.startswith("```json"):
            pages_json = pages_json.split("```json")[1]
        if pages_json.endswith("```"):
            pages_json = pages_json.rsplit("```", 1)[0]
        pages_json = pages_json.strip()
        
        pages = json.loads(pages_json)

        return {
            "success": True,
            "data": pages
        }

    except Exception as e:
        print(f"Error calling OpenAI for all pages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate all pages: {e}")

@app.post("/api/gpt/generate_story_foundation")
async def gpt_generate_story_foundation(req: StoryFoundationRequest):
    """Generate or complete a story foundation using AI"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        user_prompts = []
        # Use story_context if provided
        if req.story_context:
            ctx = req.story_context
            if ctx.get('title'):
                user_prompts.append(f"The story title is '{ctx['title']}'.")
            if ctx.get('coreMessage'):
                user_prompts.append(f"The core message is '{ctx['coreMessage']}'.")
            if ctx.get('age'):
                user_prompts.append(f"The target age is {ctx['age']}.")
            if ctx.get('storyTone'):
                user_prompts.append(f"The tone should be {ctx['storyTone']}.")
            if ctx.get('characters'):
                char_descriptions = []
                for char in ctx['characters']:
                    desc = f"Name: {char.get('name', '')}, Personality: {char.get('personality', '')}, Visual: {char.get('visualDescription', '')}"
                    char_descriptions.append(desc)
                if char_descriptions:
                    user_prompts.append("Characters: " + "; ".join(char_descriptions))
            if ctx.get('pages'):
                user_prompts.append(f"The story has {len(ctx['pages'])} pages.")
        else:
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
        - {' '.join(user_prompts)}

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
        print(f"OpenAI response for foundation: {foundation_json}")  # Debug log
        
        # Clean the response and try to parse JSON
        foundation_json = foundation_json.strip()
        if not foundation_json:
            raise Exception("OpenAI returned an empty response")
            
        # Try to extract JSON if it's wrapped in markdown
        if foundation_json.startswith("```json"):
            foundation_json = foundation_json.split("```json")[1]
        if foundation_json.endswith("```"):
            foundation_json = foundation_json.rsplit("```", 1)[0]
        foundation_json = foundation_json.strip()
        
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
    """Generate a character image using DALL-E with maximum anti-text measures"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    try:
        # Build the most effective prompt
        prompt = build_ultimate_character_prompt(req.prompt, getattr(req, "story_context", None))
        
        # Try up to 2 times if needed
        for attempt in range(2):
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                response_format="url",
                quality="standard",  # Less detail = less chance of text
                style="natural"      # Your insight: natural style is better
            )
            
            image_url = response.data[0].url
            
            # Optional: Quick validation (you could implement actual text detection)
            if not contains_obvious_text_keywords(prompt):
                return {
                    "success": True,
                    "data": {"url": image_url}
                }
        return {
            "success": True,
            "data": {"url": image_url}
        }
    except Exception as e:
        print(f"Error calling DALL-E: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {e}")

def build_ultimate_character_prompt(character_description: str, story_context: dict = None) -> str:
    """Build the most effective prompt combining all insights"""
    critical_rules = [
        "CRITICAL: This image must contain absolutely NO text, letters, words, writing, signs, labels, captions, or any written language whatsoever.",
        "Create a character portrait. Do NOT show any book, page, or illustration context.",
        "Only the character, centered, with a plain white background.",
        "Pure illustration only with NO textual elements of any kind."
    ]
    character_parts = [
        f"Character description: {character_description}",
        "Show ONLY this character as a portrait",
        "No background objects, especially no items that could have text"
    ]
    style_parts = [
        "Art style: Soft watercolor or gentle digital painting",
        "Colors: Warm, muted, child-friendly palette", 
        "Character centered with lots of white space",
        "Full body view, facing forward",
        "Kind, approachable expression",
        "Simple solid color or white background",
        "No props, accessories, or background elements that could contain text"
    ]
    context_parts = []
    if story_context:
        if story_context.get('targetAge'):
            context_parts.append(f"Age-appropriate for: {story_context['targetAge']}")
    all_parts = (
        critical_rules + 
        [""] +  # Empty line for clarity
        character_parts + 
        [""] +
        style_parts +
        ([""] + context_parts if context_parts else []) +
        [""] +
        ["Remember: This is a standalone character portrait with NO text or book context."]
    )
    return "\n".join(all_parts)

@app.post("/api/gpt/generate_page_image")
async def gpt_generate_page_image(req: PageImageGenerationRequest):
    """Generate page illustration with maximum context and zero text"""
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    try:
        prompt = build_ultimate_page_prompt(req.story_context, req.page_number)
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
            quality="standard",
            style="natural"
        )
        image_url = response.data[0].url
        return {
            "success": True,
            "data": {"url": image_url}
        }
    except Exception as e:
        print(f"Error generating page image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate page image: {e}")

def build_ultimate_page_prompt(story_context: dict, page_number: int) -> str:
    critical_rules = [
        "ABSOLUTELY NO TEXT OR WRITING OF ANY KIND in this image.",
        "Do NOT show any text, writing, or book pages. Only the scene and characters.",
        "NO letters, words, signs, books with visible text, newspapers, labels, or any written language.",
        "Pure visual storytelling only - this is a scene illustration, not a book page."
    ]
    current_page, previous_page, next_page = get_page_context(story_context, page_number)
    scene_parts = []
    if current_page:
        if current_page.get('illustrationPrompt'):
            cleaned_prompt = clean_illustration_prompt(current_page['illustrationPrompt'])
            scene_parts.append(f"Scene to illustrate: {cleaned_prompt}")
        elif current_page.get('text'):
            scene_parts.append(f"Create a visual representation of: {current_page['text']}")
    character_parts = []
    relevant_characters = get_relevant_characters_for_page(story_context, current_page)
    if relevant_characters:
        character_parts.append("Maintain these character appearances:")
        for char in relevant_characters:
            if char.get('visualDescription'):
                character_parts.append(f"- {char['name']}: {char['visualDescription']}")
    context_parts = []
    if previous_page and previous_page.get('text'):
        context_parts.append(f"Previous moment: {previous_page['text'][:50]}...")
    if story_context.get('storyTone'):
        context_parts.append(f"Emotional tone: {story_context['storyTone']}")
    style_parts = [
        "Visual style requirements:",
        "- Soft, child-friendly illustration style",
        "- Consistent with character designs",
        "- Focus on emotions and actions",
        "- Clear, uncluttered composition",
        "- Warm, gentle color palette",
        "- Avoid ANY objects that typically have text (signs, books, posters, etc.)"
    ]
    final_reminder = [
        "This is a standalone scene illustration with no text elements.",
        "Focus on visual storytelling through character expressions and actions."
    ]
    all_sections = [
        critical_rules,
        [""],
        scene_parts,
        [""],
        character_parts if character_parts else [],
        [""],
        context_parts if context_parts else [],
        [""],
        style_parts,
        [""],
        final_reminder
    ]
    all_parts = []
    for section in all_sections:
        all_parts.extend(section)
    return "\n".join(filter(None, all_parts))

def clean_illustration_prompt(prompt: str) -> str:
    text_related_words = {
        'book': 'story',
        'books': 'stories',
        'page': 'scene',
        'pages': 'scenes',
        'reading': 'looking at',
        'written': 'shown',
        'writing': 'drawing',
        'text': 'image',
        'words': 'pictures',
        'letters': 'shapes',
        'sign': 'symbol',
        'poster': 'picture',
        'newspaper': 'paper'
    }
    cleaned = prompt.lower()
    for old, new in text_related_words.items():
        cleaned = cleaned.replace(old, new)
    return cleaned

def get_page_context(story_context: dict, page_number: int) -> tuple:
    current_page = None
    previous_page = None
    next_page = None
    if story_context.get('pages'):
        for i, page in enumerate(story_context['pages']):
            page_num = page.get('pageNumber') or page.get('page_number')
            if page_num == page_number:
                current_page = page
                if i > 0:
                    previous_page = story_context['pages'][i-1]
                if i < len(story_context['pages']) - 1:
                    next_page = story_context['pages'][i+1]
                break
    return current_page, previous_page, next_page

def get_relevant_characters_for_page(story_context: dict, current_page: dict) -> List[dict]:
    if not current_page or not story_context.get('characters'):
        return []
    page_text = (current_page.get('text', '') + ' ' + current_page.get('illustrationPrompt', '')).lower()
    relevant_chars = []
    for char in story_context['characters']:
        char_name = char.get('name', '').lower()
        if char_name and char_name in page_text:
            relevant_chars.append(char)
    if not relevant_chars and story_context['characters']:
        relevant_chars.append(story_context['characters'][0])
    return relevant_chars

def contains_obvious_text_keywords(text: str) -> bool:
    text_keywords = ['text', 'word', 'letter', 'writing', 'sign', 'book', 'page']
    return any(keyword in text.lower() for keyword in text_keywords)

@app.post("/api/gpt/generate_minimal_image")
async def generate_minimal_image(req: ImageGenerationRequest):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    try:
        minimal_prompt = f"""
NO TEXT IN IMAGE.

{req.prompt}

Watercolor style.
No text anywhere.
        """
        response = openai.images.generate(
            model="dall-e-3",
            prompt=minimal_prompt.strip(),
            n=1,
            size="1024x1024",
            response_format="url",
            quality="standard",
            style="natural"
        )
        return {
            "success": True,
            "data": {"url": response.data[0].url}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate minimal image: {e}")

@app.post("/api/validate_prompt")
async def validate_prompt(prompt: str):
    issues = []
    problematic_words = ['book', 'page', 'text', 'word', 'letter', 'sign', 'writing']
    found_words = [w for w in problematic_words if w in prompt.lower()]
    if found_words:
        issues.append(f"Found text-related words: {', '.join(found_words)}")
    cleaned_prompt = clean_illustration_prompt(prompt)
    return {
        "original": prompt,
        "cleaned": cleaned_prompt,
        "issues": issues,
        "is_safe": len(issues) == 0
    }

character_reference_cache = {}

@app.post("/api/store_character_reference")
async def store_character_reference(story_id: str, character_name: str, image_url: str):
    if story_id not in character_reference_cache:
        character_reference_cache[story_id] = {}
    character_reference_cache[story_id][character_name] = {
        "image_url": image_url,
        "timestamp": datetime.now()
    }
    return {"success": True, "message": "Character reference stored"}

def get_character_reference(story_id: str, character_name: str) -> Optional[str]:
    if story_id in character_reference_cache:
        if character_name in character_reference_cache[story_id]:
            return character_reference_cache[story_id][character_name]["image_url"]
    return None

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