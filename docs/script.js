document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Platform Switching Logic ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    const platformPanels = document.querySelectorAll('.platform-panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const platform = btn.getAttribute('data-platform');
            
            // Update active tab button
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update active panel
            platformPanels.forEach(p => p.classList.remove('active'));
            const targetPanel = document.getElementById(`${platform}-panel`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });

    // --- 2. Copy to Clipboard Logic ---
    const copyButtons = document.querySelectorAll('.copy-btn');

    copyButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const textToCopy = btn.getAttribute('data-copy');
            const icon = btn.querySelector('i');

            if (navigator.clipboard && textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Visual feedback: change icon to checkmark
                    const originalIcon = icon.getAttribute('data-lucide');
                    icon.setAttribute('data-lucide', 'check');
                    lucide.createIcons(); // Refresh icons

                    // Revert back after 2 seconds
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', 'copy');
                        lucide.createIcons();
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy: ', err);
                });
            } else if (!navigator.clipboard) {
                console.error('Clipboard API not available');
            }
        });
    });

    // --- 3. Intersection Observer for Scroll Animations ---
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                // Optional: stop observing once shown
                // observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.feature-card, .install-container, .flow-step');
    animatedElements.forEach(el => {
        // Initial state
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });

    // --- 4. Initialize Icons ---
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});
