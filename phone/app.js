// Add spinner animation styles
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(spinnerStyle);

// Set the real current time in the status bar and update every minute
function updateClock() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, '0');
  const minutes = now.getMinutes().toString().padStart(2, '0');
  const timeString = hours + ':' + minutes;
  
  const timeElement = document.querySelector('.statusbar span:first-child');
  if (timeElement) {
    timeElement.textContent = timeString;
  }
}

// Update clock immediately and then every minute
updateClock();
setInterval(updateClock, 60000);

// Track current screen state
let currentScreen = 'home';

// Navigation functions with history support
function navigateTo(screen) {
  // Push to history if not initial load
  if (screen !== currentScreen) {
    history.pushState({ screen: screen }, '', `#${screen}`);
    currentScreen = screen;
  }
  
  // Update UI based on screen
  const tablegramApp = document.getElementById('tablegramApp');
  const arthurChat = document.getElementById('arthurChat');
  const homeScreen = document.querySelector('.home-screen');
  const statusbar = document.querySelector('.statusbar');
  const pageDots = document.querySelector('.page-dots');
  const dock = document.querySelector('.dock');
  const homeIndicator = document.querySelector('.home-indicator');
  
  // Hide all
  tablegramApp.classList.remove('active');
  arthurChat.classList.remove('active');
  homeScreen.classList.add('hidden');
  statusbar.classList.add('hidden');
  pageDots.classList.add('hidden');
  dock.classList.add('hidden');
  homeIndicator.classList.add('hidden');
  closeHamburgerMenu();
  
  // Show based on screen
  switch(screen) {
    case 'home':
      homeScreen.classList.remove('hidden');
      statusbar.classList.remove('hidden');
      pageDots.classList.remove('hidden');
      dock.classList.remove('hidden');
      homeIndicator.classList.remove('hidden');
      break;
    case 'contacts':
      tablegramApp.classList.add('active');
      break;
    case 'chat':
      arthurChat.classList.add('active');
      break;
  }
  
  updateClock();
}

// Also update when the app is opened
function openTablegram() {
  navigateTo('contacts');
  loadArthurMessages();
}

function closeTablegram() {
  navigateTo('home');
}

// Arthur Chat functionality
const ARTHUR_CHAT_KEY = 'arthur_chat_messages';

function openArthurChat() {
  navigateTo('chat');
  loadArthurMessages();
}

// Search functionality
function filterContacts() {
  const searchInput = document.getElementById('contactSearch');
  const searchTerm = searchInput.value.toLowerCase().trim();
  const chatItem = document.querySelector('.tablegram-chat-item');
  
  if (chatItem) {
    const contactName = chatItem.querySelector('.tablegram-chat-name').textContent.toLowerCase();
    if (contactName.includes(searchTerm)) {
      chatItem.style.display = 'flex';
    } else {
      chatItem.style.display = 'none';
    }
  }
}

function closeArthurChat() {
  navigateTo('contacts');
}

function toggleHamburgerMenu() {
  const menu = document.getElementById('hamburgerMenu');
  menu.classList.toggle('active');
}

function closeHamburgerMenu() {
  const menu = document.getElementById('hamburgerMenu');
  menu.classList.remove('active');
}

function emptyChat() {
  localStorage.removeItem(ARTHUR_CHAT_KEY);
  loadArthurMessages();
  closeHamburgerMenu();
}

function loadArthurMessages() {
  const messagesContainer = document.getElementById('arthurMessages');
  const messages = JSON.parse(localStorage.getItem(ARTHUR_CHAT_KEY) || '[]');
  
  messagesContainer.innerHTML = '';
  
  messages.forEach(msg => {
    const messageElement = document.createElement('div');
    messageElement.className = 'arthur-chat-message sent';
    
    if (msg.type === 'image') {
      if (msg.status === 'loading') {
        // Show loading animation
        const loadingElement = document.createElement('div');
        loadingElement.className = 'chat-loading';
        loadingElement.style.display = 'flex';
        loadingElement.style.flexDirection = 'column';
        loadingElement.style.alignItems = 'center';
        loadingElement.style.gap = '8px';
        
        const spinner = document.createElement('div');
        spinner.className = 'chat-spinner';
        spinner.style.width = '40px';
        spinner.style.height = '40px';
        spinner.style.border = '3px solid rgba(0, 122, 255, 0.3)';
        spinner.style.borderTopColor = '#007AFF';
        spinner.style.borderRadius = '50%';
        spinner.style.animation = 'spin 1s linear infinite';
        
        const loadingText = document.createElement('div');
        loadingText.textContent = 'Validating ER diagram...';
        loadingText.style.fontSize = '12px';
        loadingText.style.color = '#888';
        
        loadingElement.appendChild(spinner);
        loadingElement.appendChild(loadingText);
        messageElement.appendChild(loadingElement);
      } else if (msg.status === 'valid') {
        // Show valid image
        const imgElement = document.createElement('img');
        imgElement.src = msg.content;
        imgElement.className = 'chat-image';
        imgElement.style.maxWidth = '200px';
        imgElement.style.maxHeight = '200px';
        imgElement.style.borderRadius = '8px';
        messageElement.appendChild(imgElement);
        
        // Add success message
        const successElement = document.createElement('div');
        successElement.className = 'chat-success';
        successElement.textContent = '✓ Valid ER diagram accepted';
        successElement.style.color = '#34c759';
        successElement.style.fontSize = '12px';
        successElement.style.marginTop = '5px';
        successElement.style.fontFamily = 'monospace';
        messageElement.appendChild(successElement);
      } else if (msg.status === 'error') {
        // Show image with error message
        const imgElement = document.createElement('img');
        imgElement.src = msg.content;
        imgElement.className = 'chat-image';
        imgElement.style.maxWidth = '200px';
        imgElement.style.maxHeight = '200px';
        imgElement.style.borderRadius = '8px';
        imgElement.style.opacity = '0.6';
        messageElement.appendChild(imgElement);
        
        // Add error message with specific reason
        const errorReason = msg.reason || 'INVALID';
        const errorElement = document.createElement('div');
        errorElement.className = 'chat-error';
        errorElement.textContent = `ERROR 406 Not Acceptable: This contact only accepts photos of correct ER diagrams (${errorReason}).`;
        errorElement.style.color = '#ff3b30';
        errorElement.style.fontSize = '12px';
        errorElement.style.marginTop = '5px';
        errorElement.style.fontFamily = 'monospace';
        messageElement.appendChild(errorElement);
      }
    } else {
      messageElement.textContent = msg.content || msg;
    }
    
    messagesContainer.appendChild(messageElement);
  });
  
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('messageInput');
  const message = input.value.trim();
  
  if (message) {
    // Save to localStorage for immediate UI update
    const messages = JSON.parse(localStorage.getItem(ARTHUR_CHAT_KEY) || '[]');
    messages.push({ type: 'text', content: message });
    localStorage.setItem(ARTHUR_CHAT_KEY, JSON.stringify(messages));
    
    input.value = '';
    loadArthurMessages();
    
    // Also send to chat.php to append to chat.txt
    try {
      await fetch('chat.php', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'message=' + encodeURIComponent(message)
      });
    } catch (error) {
      console.error('Error saving to chat.txt:', error);
    }
  }
}

// Allow sending message with Enter key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    
    if (hamburgerMenu && hamburgerMenu.classList.contains('active')) {
      closeHamburgerMenu();
    } else if (currentScreen === 'chat') {
      navigateTo('contacts');
    } else if (currentScreen === 'contacts') {
      navigateTo('home');
    }
  }
  
  // Send message on Enter in Arthur chat
  if (e.key === 'Enter' && currentScreen === 'chat') {
    const input = document.getElementById('messageInput');
    if (input === document.activeElement) {
      e.preventDefault();
      sendMessage();
    }
  }
});

// Close hamburger menu when clicking outside
document.addEventListener('click', function(e) {
  const hamburgerMenu = document.getElementById('hamburgerMenu');
  const hamburgerButton = document.querySelector('.hamburger-menu');
  
  if (hamburgerMenu && hamburgerMenu.classList.contains('active')) {
    if (!hamburgerButton.contains(e.target) && !hamburgerMenu.contains(e.target)) {
      closeHamburgerMenu();
    }
  }
});

// Camera functionality
let cameraStream = null;
let currentFacingMode = 'environment'; // 'environment' for rear, 'user' for front

function openCamera() {
  // Close any existing camera stream
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
  }

  // Create camera modal
  const modal = document.createElement('div');
  modal.id = 'cameraModal';
  modal.style.position = 'fixed';
  modal.style.top = '0';
  modal.style.left = '0';
  modal.style.width = '100%';
  modal.style.height = '100%';
  modal.style.backgroundColor = 'rgba(0,0,0,0.9)';
  modal.style.zIndex = '1000';
  modal.style.display = 'flex';
  modal.style.flexDirection = 'column';
  modal.style.alignItems = 'center';
  modal.style.justifyContent = 'center';

  const video = document.createElement('video');
  video.id = 'cameraVideo';
  video.style.width = '80%';
  video.style.maxHeight = '60%';
  video.style.backgroundColor = '#000';
  video.style.borderRadius = '8px';
  video.autoplay = true;
  video.playsInline = true;

  const captureBtn = document.createElement('button');
  captureBtn.id = 'captureButton';
  captureBtn.textContent = '📸 Send Photo';
  captureBtn.style.marginTop = '20px';
  captureBtn.style.padding = '10px 20px';
  captureBtn.style.backgroundColor = '#007AFF';
  captureBtn.style.color = 'white';
  captureBtn.style.border = 'none';
  captureBtn.style.borderRadius = '20px';
  captureBtn.style.cursor = 'pointer';

  const switchBtn = document.createElement('button');
  switchBtn.id = 'switchCameraButton';
  switchBtn.textContent = '🔄 ALTER VIEW';
  switchBtn.style.marginTop = '10px';
  switchBtn.style.padding = '10px 20px';
  switchBtn.style.backgroundColor = '#4b68e8';
  switchBtn.style.color = 'white';
  switchBtn.style.border = 'none';
  switchBtn.style.borderRadius = '20px';
  switchBtn.style.cursor = 'pointer';
  switchBtn.onclick = switchCameraInModal;

  const closeBtn = document.createElement('button');
  closeBtn.id = 'closeCameraButton';
  closeBtn.textContent = '❌ Close';
  closeBtn.style.marginTop = '10px';
  closeBtn.style.padding = '10px 20px';
  closeBtn.style.backgroundColor = '#ff3b30';
  closeBtn.style.color = 'white';
  closeBtn.style.border = 'none';
  closeBtn.style.borderRadius = '20px';
  closeBtn.style.cursor = 'pointer';

  modal.appendChild(video);
  modal.appendChild(captureBtn);
  modal.appendChild(switchBtn);
  modal.appendChild(closeBtn);
  document.body.appendChild(modal);

  // Request camera access with current facing mode
  const constraints = { 
    video: { facingMode: currentFacingMode },
    audio: false 
  };
  
  navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
      cameraStream = stream;
      video.srcObject = stream;
      
      captureBtn.onclick = () => capturePhoto(video, modal);
      closeBtn.onclick = () => closeCameraModal(modal);
    })
    .catch(err => {
      console.error('Camera Error:', err);
      alert('Camera Access not allowed or no camera available.');
      document.body.removeChild(modal);
    });
}

function capturePhoto(video, modal) {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  
  // Use JPEG format
  const imageDataUrl = canvas.toDataURL('image/jpeg');
  
  // Save photo to chat
  sendPhoto(imageDataUrl);
  
  // Close camera
  closeCameraModal(modal);
}

function closeCameraModal(modal) {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
  
  const video = document.getElementById('cameraVideo');
  if (video && video.srcObject) {
    video.srcObject = null;
  }
  
  if (modal && modal.parentNode) {
    modal.parentNode.removeChild(modal);
  }
}

function switchCameraInModal() {
  // Toggle between front and rear camera
  currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
  
  // Get the current modal and video
  const cameraModal = document.getElementById('cameraModal');
  const video = document.getElementById('cameraVideo');
  
  if (cameraModal && video) {
    // Close current stream
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
    }
    
    if (video.srcObject) {
      video.srcObject = null;
    }
    
    // Request new stream with updated facing mode
    const constraints = { 
      video: { facingMode: currentFacingMode },
      audio: false 
    };
    
    navigator.mediaDevices.getUserMedia(constraints)
      .then(stream => {
        cameraStream = stream;
        video.srcObject = stream;
      })
      .catch(err => {
        console.error('Camera Error:', err);
        alert('Camera Access not allowed or no camera available.');
      });
  }
}



async function validateERDiagram(imageDataUrl) {
  // Extract base64 data from data URL
  const base64Data = imageDataUrl.split(',')[1];
  
  const startTime = performance.now();
  
  try {
    const response = await fetch('llm.php', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({image_data: base64Data})
    });
    
    const result = await response.json();
    
    const endTime = performance.now();
    const durationSeconds = (endTime - startTime) / 1000;
    console.log('LLM request duration:', durationSeconds.toFixed(3), 'seconds');
    
    // Output debug field to console if present
    if (result.debug) {
      console.log('LLM Debug:', result.debug);
    }
    if (result.raw_response) {
      console.log('LLM Raw Response:', result.raw_response);
    }
    
    return result;
  } catch (error) {
    console.error('Validation error:', error);
    return { valid: false, reason: 'CONNECTION_ERROR' };
  }
}

async function sendPhoto(imageDataUrl) {
  const messages = JSON.parse(localStorage.getItem(ARTHUR_CHAT_KEY) || '[]');
  
  // Add loading message immediately
  const loadingId = Date.now().toString();
  messages.push({ 
    type: 'image', 
    content: imageDataUrl,
    status: 'loading',
    id: loadingId
  });
  localStorage.setItem(ARTHUR_CHAT_KEY, JSON.stringify(messages));
  loadArthurMessages();
  
  // Validate the image with LLM
  const validationResult = await validateERDiagram(imageDataUrl);
  
  // Update message with validation result
  const updatedMessages = JSON.parse(localStorage.getItem(ARTHUR_CHAT_KEY) || '[]');
  const index = updatedMessages.findIndex(m => m.id === loadingId);
  
  if (index !== -1) {
    if (validationResult.valid) {
      // Valid ER diagram - show image normally
      updatedMessages[index] = { 
        type: 'image', 
        content: imageDataUrl,
        status: 'valid',
        id: loadingId
      };
    } else {
      // Invalid ER diagram - show error with reason
      updatedMessages[index] = { 
        type: 'image', 
        content: imageDataUrl,
        status: 'error',
        reason: validationResult.reason || 'INVALID',
        id: loadingId
      };
    }
    localStorage.setItem(ARTHUR_CHAT_KEY, JSON.stringify(updatedMessages));
    loadArthurMessages();
  }
}

// Handle browser back/forward navigation
window.addEventListener('popstate', function(e) {
  if (e.state && e.state.screen) {
    navigateTo(e.state.screen);
  } else {
    // No state, go to home
    navigateTo('home');
  }
});

// Initialize navigation on load
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('contactSearch');
  if (searchInput) {
    searchInput.addEventListener('input', filterContacts);
  }
  
  // Add camera button functionality
  const cameraButton = document.querySelector('.camera-button');
  if (cameraButton) {
    cameraButton.onclick = openCamera;
  }
  
  // Check URL hash for initial screen
  const hash = window.location.hash.slice(1);
  if (hash && ['home', 'contacts', 'chat'].includes(hash)) {
    navigateTo(hash);
  } else {
    navigateTo('home');
  }
});
