// JonguBooks JavaScript Application

// --- Lifecycle ---
document.addEventListener('DOMContentLoaded', () => {
    // Initialize with empty state
    updateProgress('story');
    
    // Add initial character and page
    addCharacter();
    addPage();
  });
  
  // --- Navigation and UI functions ---
  function setActiveSection(event, section) {
    event.preventDefault(); // Stop the default anchor link behavior
    
    // Update navigation active class
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
  
    // Scroll to the corresponding section
    const sectionElement = document.getElementById(section + '-section');
    if (sectionElement) {
        sectionElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  
    // Update progress bar
    updateProgress(section);
  
    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
      document.getElementById('sidebar').classList.remove('open');
    }
  }
  
  function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
  }
  
  function startOver(event) {
    event.preventDefault();
    if (confirm('Are you sure you want to start over? This will erase all your progress.')) {
      characterCount = 0;
      pageCount = 0;
  
      // Reset Story Foundation fields
      document.getElementById('storyTitle').value = '';
      document.getElementById('coreMessage').value = '';
      document.getElementById('storyOutline').value = '';
      document.getElementById('totalWords').value = '';
      document.getElementById('totalPages').value = '';
      document.getElementById('storyTone').selectedIndex = 0;
      document.getElementById('targetAge').selectedIndex = 0;
  
      // Reset Characters section to its initial state
      const charactersContainer = document.getElementById('charactersContainer');
      charactersContainer.innerHTML = '';
      addCharacter(); // Add a single blank card
  
      // Reset Pages section to its initial state
      const pagesContainer = document.getElementById('pagesContainer');
      pagesContainer.innerHTML = '';
      addPage(); // Add a single blank card
  
      // Reset navigation to the first step
      document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
      const firstNavItem = document.querySelector('.nav-item[href="#story-section"]');
      if (firstNavItem) {
        firstNavItem.classList.add('active');
        firstNavItem.click()
      }
      updateProgress('story');
  
      showToast('Project cleared. Ready for a new story!');
    }
  }
  
  function updateProgress(section) {
    const steps = ['story', 'characters', 'pages', 'export'];
    const currentIndex = steps.indexOf(section);
    
    if (currentIndex === -1) return;
    
    const progressPercent = ((currentIndex) / (steps.length - 1)) * 100;
    document.getElementById('progressFill').style.width = progressPercent + '%';
    
    document.querySelectorAll('.progress-step').forEach((step, index) => {
      step.classList.remove('active', 'completed');
      if (index < currentIndex) {
        step.classList.add('completed');
      } else if (index === currentIndex) {
        step.classList.add('active');
      }
    });
  }
  
  // --- Toast Notification ---
  function showToast(message) {
    const toast = document.getElementById('toast');
    document.getElementById('toastMessage').textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3000);
  }
  
  // --- Card management ---
  let characterCount = 0;
  function addCharacter(character = null) {
    characterCount++;
    const container = document.getElementById('charactersContainer');
    const newCard = document.createElement('div');
    newCard.className = 'character-card';
    newCard.innerHTML = `
      <div class="field-group">
          <label class="field-label">Character Name</label>
          <input type="text" class="field-input" placeholder="e.g., Leo the Brave Lion" id="characterName${characterCount}" value="${character ? character.name : ''}">
      </div>
      <div class="field-group">
          <label class="field-label">Character Purpose & Personality</label>
          <textarea class="field-input field-textarea" placeholder="What makes this character special?" id="characterPersonality${characterCount}">${character ? character.personality : ''}</textarea>
      </div>
      <div class="field-group">
          <label class="field-label">Visual Description for AI</label>
          <textarea class="field-input field-textarea" placeholder="e.g., A small, fluffy bunny with long, floppy ears and a tiny pink nose, wearing a blue waistcoat." id="characterVisualDescription${characterCount}"></textarea>
      </div>
      <div class="field-group">
          <label class="field-label">Visual Reference (Optional)</label>
          <input type="file" class="field-input" accept="image/*" id="characterImage${characterCount}" onchange="previewManualImage(this)">
          <div class="image-preview" id="imagePreview${characterCount}"></div>
      </div>
      <div class="button-group" style="margin-top: 1rem;">
          <button class="button" onclick="generateCharacterImage(this)">🎨 Use AI to Create Image</button>
      </div>
      <div class="button-group" style="margin-top: 1rem;">
        <button class="button button-secondary" onclick="removeCharacter(this)">🗑️ Remove</button>
      </div>
    `;
    container.appendChild(newCard);
    if (!character) {
      showToast('New character card added!');
    }
  }
  
  function removeCharacter(button) {
    if (confirm('Are you sure you want to remove this character?')) {
      button.closest('.character-card').remove();
      showToast('Character removed');
    }
  }
  
  function previewManualImage(input) {
    const card = input.closest('.character-card');
    const previewContainer = card.querySelector('.image-preview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            previewContainer.innerHTML = `<img src="${e.target.result}" alt="Manually uploaded character image">`;
        }
        reader.readAsDataURL(input.files[0]);
    }
  }
  
  async function generateCharacterImage(button) {
    const card = button.closest('.character-card');
    const visualDescriptionInput = card.querySelector('textarea[id^="characterVisualDescription"]');
    let prompt = visualDescriptionInput.value.trim();
  
    if (!prompt) {
      // Try to auto-generate a prompt from story foundation and character info
      const storyTitle = document.getElementById('storyTitle').value.trim();
      const coreMessage = document.getElementById('coreMessage').value.trim();
      const characterName = card.querySelector('input[id^="characterName"]').value.trim();
      const characterPersonality = card.querySelector('textarea[id^="characterPersonality"]').value.trim();
      prompt = `A children's book character illustration. Name: ${characterName || 'Unnamed Character'}. Personality: ${characterPersonality || 'unique and friendly'}. Story: ${storyTitle ? storyTitle + '. ' : ''}${coreMessage}`;
      visualDescriptionInput.value = prompt;
      showToast('No visual description provided. Using an AI-generated prompt based on your story and character.');
    }
  
    button.disabled = true;
    button.textContent = '🎨 Creating...';
  
    try {
      const storyContext = getStoryContext();
      if (!storyContext.title || !storyContext.coreMessage) {
        showToast('Please provide a title and core message in Step 1 first.');
        return;
      }
      const response = await fetch('/api/gpt/generate_all_pages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          story_title: storyContext.title,
          core_message: storyContext.coreMessage,
          story_context: storyContext 
        })
      });
  
      const result = await response.json();
  
      if (result.success && result.data) {
        const pagesContainer = document.getElementById('pagesContainer');
        pagesContainer.innerHTML = ''; // Clear existing pages
        pageCount = 0; // Reset page count
        
        result.data.forEach(page => {
          addPage({
            page_number: page.page_number,
            text: page.text,
            illustration_prompt: page.illustration_prompt
          });
        });
        
        showToast(`Generated ${result.data.length} pages successfully!`);
        
        // Navigate to the section
        document.getElementById('pages-section').scrollIntoView({ behavior: 'smooth' });
        updateProgress('pages');
        document.querySelector('.nav-item.active').classList.remove('active');
        document.querySelector('.nav-item[href="#pages-section"]').classList.add('active');
  
      } else {
        throw new Error(result.detail || 'Failed to generate pages.');
      }
    } catch (error) {
      console.error('Error generating pages:', error);
      showToast('Error: Could not generate pages.');
    } finally {
      button.disabled = false;
      button.textContent = '🤖 Use AI to Create All Pages';
    }
  }
  
  async function recreateAllImages(event) {
    event.preventDefault();
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = '🎨 Recreating images...';
    showToast('Regenerating all images with full story context. This may take a while...');
    const storyContext = getStoryContext();
    const pageContainers = document.querySelectorAll('#pagesContainer .page-container');
    for (let i = 0; i < pageContainers.length; i++) {
      const pageContainer = pageContainers[i];
      const pageNumber = i + 1;
      try {
        const response = await fetch('/api/gpt/generate_page_image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            story_context: storyContext,
            page_number: pageNumber
          })
        });
        const result = await response.json();
        if (result.success && result.data.url) {
          const imageArea = pageContainer.querySelector('.image-area');
          imageArea.innerHTML = `<img src="${result.data.url}" class="uploaded-image" alt="AI-generated page illustration">`;
          imageArea.classList.add('has-image');
        } else {
          throw new Error(result.detail || 'Failed to generate image.');
        }
      } catch (error) {
        console.error('Error generating image for page', pageNumber, error);
        showToast(`Error: Could not generate image for page ${pageNumber}.`);
      }
    }
    button.disabled = false;
    button.textContent = '🎨 Recreate All Images';
    showToast('All images have been recreated!');
  }
  
  // --- AI Chat ---
  const chatPopup = document.getElementById('ai-chat-popup');
  const openChatBtn = document.getElementById('open-chat-btn');
  const closeChatBtn = document.getElementById('close-chat-btn');
  const chatMessages = document.getElementById('ai-chat-messages');
  const chatInput = document.getElementById('ai-chat-input');
  const sendChatBtn = document.getElementById('ai-chat-send-btn');
  let chatHistory = [];
  
  openChatBtn.addEventListener('click', () => chatPopup.classList.add('show'));
  closeChatBtn.addEventListener('click', () => chatPopup.classList.remove('show'));
  
  sendChatBtn.addEventListener('click', sendChatMessage);
  chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      sendChatMessage();
    }
  });
  
  async function sendChatMessage() {
    const messageText = chatInput.value.trim();
    if (!messageText) return;
  
    // Add user message to UI
    addMessageToChat('user', messageText);
    chatInput.value = '';
  
    // Add user message to history
    chatHistory.push({ role: 'user', content: messageText });
    
    // Add typing indicator
    const typingIndicator = addMessageToChat('typing', '...');
  
    try {
      const response = await fetch('/api/ai/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: messageText, history: chatHistory })
      });
      const result = await response.json();
      
      // Remove typing indicator
      chatMessages.removeChild(typingIndicator);
  
      if (result.success) {
        addMessageToChat('assistant', result.reply);
        // Add assistant reply to history
        chatHistory.push({ role: 'assistant', content: result.reply });
      } else {
        addMessageToChat('assistant', 'Sorry, I had trouble connecting. Please try again.');
      }
    } catch (error) {
      chatMessages.removeChild(typingIndicator);
      addMessageToChat('assistant', 'Sorry, an error occurred.');
      console.error('Chat error:', error);
    }
  }
  
  function addMessageToChat(role, text) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', role);
    messageElement.textContent = text;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
    return messageElement;
  }
  
  async function completeStoryFoundation(event) {
    event.preventDefault();
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = '🤖 Thinking...';
  
    try {
      const response = await fetch('/api/gpt/generate_story_foundation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story_context: getStoryContext() })
      });
  
      const result = await response.json();
  
      if (result.success && result.data) {
        document.getElementById('storyTitle').value = result.data.title || '';
        document.getElementById('coreMessage').value = result.data.coreMessage || '';
        document.getElementById('storyOutline').value = result.data.outline || '';
        document.getElementById('storyTone').value = result.data.tone || 'Gentle & Nurturing';
        document.getElementById('targetAge').value = result.data.age || '4-6 years';
        showToast('AI has completed the story foundation!');
      } else {
        throw new Error(result.detail || 'Failed to generate story foundation.');
      }
    } catch (error) {
      console.error('Error generating story foundation:', error);
      showToast('Error: Could not complete the story foundation.');
    } finally {
      button.disabled = false;
      button.textContent = '🤖 Use AI to Complete Story Foundation';
    }
  }
  
  // --- Story Context Object and Gather Function ---
  function getStoryContext() {
    // Gather story foundation
    const storyContext = {
      title: document.getElementById('storyTitle').value.trim(),
      coreMessage: document.getElementById('coreMessage').value.trim(),
      outline: document.getElementById('storyOutline')?.value.trim() || '',
      totalWords: document.getElementById('totalWords')?.value.trim() || '',
      totalPages: document.getElementById('totalPages')?.value.trim() || '',
      storyTone: document.getElementById('storyTone')?.value || '',
      targetAge: document.getElementById('targetAge')?.value || '',
      characters: [],
      pages: []
    };
    // Gather characters
    document.querySelectorAll('#charactersContainer .character-card').forEach(card => {
      storyContext.characters.push({
        name: card.querySelector('input[id^="characterName"]').value.trim(),
        personality: card.querySelector('textarea[id^="characterPersonality"]').value.trim(),
        visualDescription: card.querySelector('textarea[id^="characterVisualDescription"]').value.trim(),
        imageUrl: card.querySelector('.image-preview img')?.src || ''
      });
    });
    // Gather pages
    document.querySelectorAll('#pagesContainer .page-container').forEach((page, idx) => {
      storyContext.pages.push({
        pageNumber: idx + 1,
        text: page.querySelector('textarea[id^="pageText"]').value.trim(),
        illustrationPrompt: page.querySelector('textarea[id^="pageImagePrompt"]').value.trim(),
        imageUrl: page.querySelector('.uploaded-image')?.src || ''
      });
    });
    return storyContext;
  }  const response = await fetch('/api/gpt/generate_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        });
        const result = await response.json();
  
        if (result.success && result.data.url) {
            const previewContainer = card.querySelector('.image-preview');
            previewContainer.innerHTML = `<img src="${result.data.url}" alt="AI-generated character image">`;
            showToast('AI image created successfully!');
        } else {
            throw new Error(result.detail || 'Failed to generate image.');
        }
  
    } catch (error) {
        console.error('Error generating image:', error);
        showToast('Error: Could not generate the image.');
    } finally {
        button.disabled = false;
        button.textContent = '🎨 Use AI to Create Image';
    }
  }
  
  let pageCount = 0;
  function addPage(page = null) {
    pageCount++;
    const container = document.getElementById('pagesContainer');
    const newPage = document.createElement('div');
    newPage.className = 'page-container';
    newPage.style.position = 'relative';
    
    // Check if we have an AI-generated image
    const hasImage = page && page.illustration_url;
    const imageContent = hasImage ? 
      `<img src="${page.illustration_url}" class="uploaded-image" alt="AI-generated illustration">` : 
      `<span class="image-placeholder-icon">🎨</span>Click to upload image`;
    
    newPage.innerHTML = `
      <span class="page-number">${pageCount}</span>
      <div class="page-image-section">
          <div class="image-area ${hasImage ? 'has-image' : ''}" onclick="uploadPageImage(this)">
            ${imageContent}
          </div>
          <div class="field-group" style="margin-top: 1rem;">
              <label class="field-label">Visual Description for AI Image</label>
              <textarea class="field-input field-textarea" placeholder="e.g., A bunny looking at the moon from a hill." id="pageImagePrompt${pageCount}">${page && page.illustration_prompt ? page.illustration_prompt : ''}</textarea>
          </div>
          <div class="button-group">
              <button class="button" onclick="generatePageImage(this)">🎨 Use AI to Create Image</button>
          </div>
        </div>
      <div class="text-area">
        <textarea class="field-input field-textarea" placeholder="Enter your page text here..." id="pageText${pageCount}">${page ? page.text : ''}</textarea>
         <button class="button" onclick="generatePageText(this)">📝 Use AI to Create Text</button>
      </div>
      <div class="button-group" style="margin-top: 1rem; justify-content: flex-end; width: 100%;">
          <button class="button button-secondary" onclick="removePage(this)">🗑️ Remove Page</button>
      </div>
    `;
    container.appendChild(newPage);
    if (!page) {
      showToast('New page added!');
    }
  }
  
  function removePage(button) {
      if(confirm('Are you sure you want to remove this page?')) {
          button.closest('.page-container').remove();
          showToast('Page removed');
      }
  }
  
  function uploadPageImage(imageArea) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = function(e) {
      if (e.target.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
          imageArea.innerHTML = `<img src="${e.target.result}" class="uploaded-image" alt="Page illustration">`;
          imageArea.classList.add('has-image');
        };
        reader.readAsDataURL(e.target.files[0]);
      }
    };
    input.click();
  }
  
  async function generatePageImage(button) {
    const pageContainer = button.closest('.page-container');
    const pageNumber = parseInt(pageContainer.querySelector('.page-number').textContent);
    const storyContext = getStoryContext();
  
    button.disabled = true;
    button.textContent = '🎨 Creating...';
    showToast('Generating image with full story context. This may take a while...');
  
    try {
      const response = await fetch('/api/gpt/generate_page_image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          story_context: storyContext,
          page_number: pageNumber
        })
      });
      const result = await response.json();
      if (result.success && result.data.url) {
        // Display the image in the image-area
        const imageArea = pageContainer.querySelector('.image-area');
        imageArea.innerHTML = `<img src="${result.data.url}" class="uploaded-image" alt="AI-generated page illustration">`;
        imageArea.classList.add('has-image');
        showToast('AI image created successfully!');
      } else {
        throw new Error(result.detail || 'Failed to generate image.');
      }
    } catch (error) {
      console.error('Error generating page image:', error);
      showToast('Error: Could not generate the image.');
    } finally {
      button.disabled = false;
      button.textContent = '🎨 Use AI to Create Image';
    }
  }
  
  async function generatePageText(button) {
    const pageContainer = button.closest('.page-container');
    const pageTextarea = pageContainer.querySelector('textarea[id^="pageText"]');
    const pageNumber = parseInt(pageContainer.querySelector('.page-number').textContent);
    
    let previousPageText = '';
    if (pageNumber > 1) {
      const prevPageContainer = pageContainer.previousElementSibling;
      if (prevPageContainer && prevPageContainer.classList.contains('page-container')) {
          const prevTextarea = prevPageContainer.querySelector('textarea[id^="pageText"]');
          if (prevTextarea) {
              previousPageText = prevTextarea.value;
          }
      }
    }
  
    const storyContext = getStoryContext();
    const requestBody = {
      story_title: document.getElementById('storyTitle').value,
      core_message: document.getElementById('coreMessage').value,
      page_number: pageNumber,
      total_pages: parseInt(document.getElementById('totalPages').value) || 12,
      previous_text: previousPageText,
      story_context: storyContext
    };
  
    if (!requestBody.story_title || !requestBody.core_message) {
      showToast('Please provide a title and core message in Step 1 first.');
      return;
    }
  
    button.disabled = true;
    button.textContent = '📝 Writing...';
  
    try {
      const response = await fetch('/api/gpt/generate_page_text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      const result = await response.json();
  
      if (result.success && result.data.text) {
        pageTextarea.value = result.data.text;
        showToast(`Page ${pageNumber} text generated!`);
      } else {
        throw new Error(result.detail || 'Failed to generate page text.');
      }
  
    } catch (error) {
      console.error('Error generating page text:', error);
      showToast('Error: Could not generate page text.');
    } finally {
      button.disabled = false;
      button.textContent = '📝 Use AI to Create Text';
    }
  }
  
  function previewBook() {
    // Gather all the data from the form first
    const story = {
      title: document.getElementById('storyTitle').value,
      characters: [],
      pages: []
    };
  
    document.querySelectorAll('#charactersContainer .character-card').forEach(card => {
      const name = card.querySelector(`input[id^="characterName"]`).value;
      if (name) {
        story.characters.push({ name: name });
      }
    });
  
    document.querySelectorAll('#pagesContainer .page-container').forEach((page, index) => {
      const text = page.querySelector(`textarea[id^="pageText"]`).value;
      const imgSrc = page.querySelector('.uploaded-image')?.src;
      if (text || imgSrc) {
        story.pages.push({
          page_number: index + 1,
          text: text,
          imgSrc: imgSrc
        });
      }
    });
  
    // --- Generate the HTML for the new tab ---
    let previewHtml = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview: ${story.title}</title>
        <style>
          body { font-family: 'Segoe UI', sans-serif; margin: 0; background-color: #f0f0f0; }
          .book-container { max-width: 800px; margin: 2rem auto; }
          .page { background-color: white; padding: 2rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; min-height: 400px; align-items: center; }
          .page.text-only { grid-template-columns: 1fr; }
          h1 { text-align: center; margin-bottom: 2rem; color: #333; }
          p { font-size: 1.1rem; line-height: 1.8; color: #444; }
          img { max-width: 100%; border-radius: 8px; }
          .page-number { text-align: center; color: #999; margin-top: 1rem; font-style: italic; }
          @media (max-width: 600px) {
            .page { grid-template-columns: 1fr; }
          }
        </style>
      </head>
      <body>
        <div class="book-container">
          <h1>${story.title || 'Untitled Story'}</h1>
    `;
    
    story.pages.forEach(p => {
      const textSide = `<div class="text-content"><p>${p.text.replace(/\n/g, '<br>')}</p></div>`;
      const imageSide = p.imgSrc ? `<div class="image-content"><img src="${p.imgSrc}" alt="Illustration for page ${p.page_number}"></div>` : '';
      
      previewHtml += `
        <div class="page ${!p.imgSrc ? 'text-only' : ''}">
          ${p.imgSrc ? textSide + imageSide : textSide}
        </div>
        <div class="page-number">${p.page_number}</div>
      `;
    });
  
    previewHtml += `
        </div>
      </body>
      </html>
    `;
  
    // --- Open the new tab and write the content ---
    const previewWindow = window.open('', '_blank');
    previewWindow.document.open();
    previewWindow.document.write(previewHtml);
    previewWindow.document.close();
  }
  
  function startNewStory() {
    if (confirm('This will start a new story, but your current work will be saved. Is that okay?')) {
      startOver(new Event('submit'));
    }
  }
  
  async function generateCharacters(event) {
      event.preventDefault();
      const button = event.currentTarget;
      button.disabled = true;
      button.textContent = '🤖 Thinking...';
  
      try {
          const storyContext = getStoryContext();
          const response = await fetch('/api/gpt/generate_characters', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ story_context: storyContext })
          });
  
          const result = await response.json();
  
          if (result.success && result.data) {
              const charactersContainer = document.getElementById('charactersContainer');
              charactersContainer.innerHTML = ''; // Clear existing characters
              result.data.forEach(char => addCharacter(char));
              showToast('AI-generated characters have been added!');
              
              // Navigate to the section
              document.getElementById('characters-section').scrollIntoView({ behavior: 'smooth' });
              updateProgress('characters');
              document.querySelector('.nav-item.active').classList.remove('active');
              document.querySelector('.nav-item[href="#characters-section"]').classList.add('active');
  
          } else {
              throw new Error(result.detail || 'Failed to generate characters.');
          }
      } catch (error) {
          console.error('Error generating characters:', error);
          showToast('Error: Could not generate characters.');
      } finally {
          button.disabled = false;
          button.textContent = '🤖 Use AI to Create Characters';
      }
  }
  
  async function generatePages(event) {
    event.preventDefault();
    const button = event.currentTarget;
    button.disabled = true;
    button.textContent = '🤖 Creating all pages...';
  
    try {