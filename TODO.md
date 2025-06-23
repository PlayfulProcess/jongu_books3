# To Do List for JonguBooks

## 🧹 Clean Up
- [x] Clean up the export buttons (PDF, eBook, Share Online) that are not working or are placeholders.
- [ ] Enable and use version control (git) locally for better tracking of changes and collaboration.

## 🤖 AI Improvements
- [x] When generating characters with AI, prompt the user to create an initial story description if they haven't provided one yet.
- [x] Pass the full story context object to all AI calls in the backend (for richer, context-aware generation).
- [ ] Try to create image consistency across the pages (e.g., by passing a style or character description to each image prompt, or using a seed if supported).
- [ ] Implement multi-turn image editing using OpenAI's new multi-turn editing API (for refining images across multiple turns).
- [ ] Make all AI context fields optional and allow AI calls to proceed even with missing context (start with 'Use AI to Create Characters').

## 🧠 AI Context Awareness & Smart Fallbacks
- [ ] When user prompts AI without sufficient context (e.g., empty story title/message), AI should intelligently create context or ask clarifying questions
- [ ] AI should be able to invent story elements when context is missing, rather than just showing error messages
- [ ] Add smart prompts that guide users to provide better context when needed
- [ ] Implement progressive context building - start with basic elements and expand as user provides more details

## 🎨 Image Generation
- [ ] Implement individual page image generation (`generatePageImage()` function) - currently shows "coming soon"
- [ ] Update page image generation to use full story context for better prompts
- [ ] Add DALL-E integration for page illustrations

## 💬 AI Chat Assistant
- [ ] Update AI chat assistant (`sendChatMessage()`) to include story context in requests
- [ ] Make chat assistant aware of current story details for more relevant advice

## ✅ Completed (Full Story Context Implementation)
- [x] Story Foundation generation - uses full story context
- [x] Character generation - uses full story context  
- [x] All pages generation - uses full story context
- [x] Individual page text generation - uses full story context
- [x] Backend endpoints updated to accept and use `story_context` parameter
- [x] Frontend `getStoryContext()` function gathers all user input
- [x] All major AI functions now have richer, context-aware generation

## 🎨 Sidebar UI Improvements
- [ ] Implement DALL-E Gen ID workflow for character consistency (request Gen ID after character creation, use it in subsequent prompts)
- [ ] Research and possibly implement other DALL-E character consistency techniques (reference images, grid prompts, seed/variation, etc)
- [ ] Sidebar UI: Use the same font as the main website, and replace sidebar icons with purple step circles (matching the main content step style)
- [ ] Continue polishing sidebar spacing, alignment, and hover/active states for a modern, unified look

---
Add more tasks as needed! 