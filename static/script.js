// Get DOM elements
const urlForm = document.getElementById('urlForm');
const longUrlInput = document.getElementById('longUrl');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const result = document.getElementById('result');
const shortUrlInput = document.getElementById('shortUrl');
const originalUrlLink = document.getElementById('originalUrl');
const shortCodeDisplay = document.getElementById('shortCode');
const copyBtn = document.getElementById('copyBtn');
const newUrlBtn = document.getElementById('newUrlBtn');
const testLink = document.getElementById('testLink');

// Get base URL (current host and port)
const baseUrl = window.location.origin;

// Handle form submission
urlForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results and errors
    hideError();
    hideResult();
    
    // Get URL from input
    const url = longUrlInput.value.trim();
    
    if (!url) {
        showError('Please enter a URL');
        return;
    }
    
    // Show loading state
    setLoading(true);
    
    try {
        // Call API
        const response = await fetch(`${baseUrl}/api/shorten`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Handle error response
            showError(data.detail || 'Failed to shorten URL');
            setLoading(false);
            return;
        }
        
        // Show success result
        displayResult(data);
        setLoading(false);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
        setLoading(false);
    }
});

// Display result
function displayResult(data) {
    shortUrlInput.value = data.short_url;
    originalUrlLink.href = data.original_url;
    originalUrlLink.textContent = data.original_url;
    shortCodeDisplay.textContent = data.short_code;
    testLink.href = data.short_url;
    
    result.style.display = 'block';
    result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Copy to clipboard
copyBtn.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(shortUrlInput.value);
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        
        setTimeout(() => {
            copyBtn.textContent = '📋 Copy';
            copyBtn.classList.remove('copied');
        }, 2000);
    } catch (err) {
        // Fallback for older browsers
        shortUrlInput.select();
        document.execCommand('copy');
        copyBtn.textContent = '✓ Copied!';
        copyBtn.classList.add('copied');
        
        setTimeout(() => {
            copyBtn.textContent = '📋 Copy';
            copyBtn.classList.remove('copied');
        }, 2000);
    }
});

// New URL button
newUrlBtn.addEventListener('click', () => {
    hideResult();
    hideError();
    longUrlInput.value = '';
    longUrlInput.focus();
});

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Hide result
function hideResult() {
    result.style.display = 'none';
}

// Set loading state
function setLoading(loading) {
    submitBtn.disabled = loading;
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Focus input on page load
window.addEventListener('load', () => {
    longUrlInput.focus();
});

