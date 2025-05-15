// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Helper function to copy text to clipboard
    function copyToClipboard(text) {
        // Create a temporary textarea element
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        
        // Select and copy text
        textarea.select();
        document.execCommand('copy');
        
        // Remove temporary element
        document.body.removeChild(textarea);
        
        return true;
    }
    
    // Show tooltip when content is copied
    function showTooltip(element, message) {
        // Create tooltip if it doesn't exist
        let tooltip = element.querySelector('.copy-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.className = 'copy-tooltip';
            element.appendChild(tooltip);
        }
        
        // Set tooltip position
        const rect = element.getBoundingClientRect();
        tooltip.textContent = message;
        tooltip.style.top = Math.min(rect.height + 5, rect.height / 2) + 'px';
        tooltip.style.left = rect.width / 2 + 'px';
        tooltip.style.transform = 'translateX(-50%)';
        
        // Show tooltip
        tooltip.classList.add('show');
        
        // Hide tooltip after 1.5 seconds
        setTimeout(function() {
            tooltip.classList.remove('show');
        }, 1500);
    }
    
    // Helper function for copy buttons
    function setupCopyButton(buttonId, inputId) {
        const copyBtn = document.getElementById(buttonId);
        const inputElement = document.getElementById(inputId);
        
        if (copyBtn && inputElement) {
            copyBtn.addEventListener('click', function() {
                inputElement.select();
                document.execCommand('copy');
                
                // Show temporary success feedback
                const originalText = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                copyBtn.classList.add('btn-success');
                copyBtn.classList.remove('btn-outline-secondary');
                
                setTimeout(function() {
                    copyBtn.innerHTML = originalText;
                    copyBtn.classList.remove('btn-success');
                    copyBtn.classList.add('btn-outline-secondary');
                }, 2000);
            });
        }
    }
    
    // Setup click-to-copy for content elements
    const clickableCopyElements = document.querySelectorAll('.clickable-copy');
    clickableCopyElements.forEach(function(element) {
        element.addEventListener('click', function() {
            const textToCopy = element.textContent.trim();
            if (copyToClipboard(textToCopy)) {
                showTooltip(element, '已复制！');
            }
        });
    });
    
    // Setup copy functionality for webhook URL
    setupCopyButton('copy-webhook-url', 'webhook-url');
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Limit the height of webhook content displays
    const webhookContents = document.querySelectorAll('.webhook-content');
    webhookContents.forEach(function(content) {
        if (content.offsetHeight > 200) {
            content.style.maxHeight = '200px';
            content.style.overflowY = 'auto';
        }
    });
});
