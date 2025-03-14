// Check if the app is installed
let deferredPrompt;
const installButton = document.createElement('button');
installButton.style.display = 'none';

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later
    deferredPrompt = e;
    // Show the install button
    installButton.style.display = 'block';
});

// Installation must be done by a user gesture (e.g. button click)
installButton.addEventListener('click', async () => {
    if (deferredPrompt) {
        // Show the prompt
        deferredPrompt.prompt();
        // Wait for the user to respond to the prompt
        const { outcome } = await deferredPrompt.userChoice;
        // Clear the deferredPrompt variable
        deferredPrompt = null;
        // Hide the install button
        installButton.style.display = 'none';
    }
});

// Handle PWA updates
if ('serviceWorker' in navigator) {
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
            refreshing = true;
            window.location.reload();
        }
    });
}

// Add to home screen button
document.addEventListener('DOMContentLoaded', () => {
    const addToHomeScreen = document.getElementById('add-to-home-screen');
    if (addToHomeScreen) {
        addToHomeScreen.style.display = 'none';
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            addToHomeScreen.style.display = 'block';
            
            addToHomeScreen.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    deferredPrompt = null;
                    addToHomeScreen.style.display = 'none';
                }
            });
        });
    }
});

// Add to homescreen for Safari on iOS
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(userAgent);
};

const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

if (isIos() && !isInStandaloneMode()) {
    // Show iOS install prompt
    const iosPrompt = document.createElement('div');
    iosPrompt.className = 'ios-prompt';
    iosPrompt.innerHTML = `
        <div class="ios-prompt-message">
            <i class="fas fa-plus-square"></i>
            برای نصب اپلیکیشن، روی <strong>Share</strong> و سپس <strong>Add to Home Screen</strong> کلیک کنید
            <button class="ios-prompt-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    document.body.appendChild(iosPrompt);
}

// Add offline functionality notification
window.addEventListener('online', () => {
    showNotification('اتصال به اینترنت برقرار شد', 'success');
});

window.addEventListener('offline', () => {
    showNotification('اتصال به اینترنت قطع شد', 'warning');
});

// Show notification function
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add styles for notifications and iOS prompt
const style = document.createElement('style');
style.textContent = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        animation: slideIn 0.5s ease;
    }
    
    .ios-prompt {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        backdrop-filter: blur(10px);
    }
    
    .ios-prompt-message {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .ios-prompt-close {
        margin-left: auto;
        background: none;
        border: none;
        color: var(--text-color);
        cursor: pointer;
    }
    
    .install-button {
        margin-left: 15px;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style); 