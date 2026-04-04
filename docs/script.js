document.addEventListener('DOMContentLoaded', () => {
    console.log('hey-cli: Initializing interactive components...');

    const installContainer = document.querySelector('.install-container');
    if (!installContainer) {
        console.error('hey-cli: Error - .install-container not found.');
        return;
    }

    // --- 1. Global Event Delegation for Install Section ---
    installContainer.addEventListener('click', (event) => {
        // Target identification (check self or parents)
        const tabBtn = event.target.closest('.tab-btn');
        const copyBtn = event.target.closest('.copy-btn');

        // Case A: Platform Tab Click
        if (tabBtn) {
            const platform = tabBtn.getAttribute('data-platform');
            if (platform) {
                switchPlatform(platform, tabBtn);
            }
        }

        // Case B: Copy Button Click
        if (copyBtn) {
            const textToCopy = copyBtn.getAttribute('data-copy');
            if (textToCopy) {
                copyToClipboard(textToCopy, copyBtn);
            }
        }
    });

    function switchPlatform(platform, activeBtn) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        activeBtn.classList.add('active');

        // Update platform panels
        document.querySelectorAll('.platform-panel').forEach(panel => panel.classList.remove('active'));
        const targetPanel = document.getElementById(`${platform}-panel`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
    }

    function copyToClipboard(text, btn) {
        const icon = btn.querySelector('i');
        if (!navigator.clipboard) {
            console.warn('hey-cli: Clipboard API not available. Falling back to alternative methods is complex in this environment.');
            return;
        }

        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback: change icon to checkmark
            const originalIcon = icon.getAttribute('data-lucide');
            icon.setAttribute('data-lucide', 'check');
            if (typeof lucide !== 'undefined') lucide.createIcons();

            // Revert back after 2 seconds
            setTimeout(() => {
                icon.setAttribute('data-lucide', 'copy');
                if (typeof lucide !== 'undefined') lucide.createIcons();
            }, 2000);
        }).catch(err => {
            console.error('hey-cli: Failed to copy text: ', err);
        });
    }

    // --- 3. Architecture Node Swapping ---
    const nodeData = {
        input: {
            title: "Plain English",
            description: "The entry point. Users input their objective in natural language or pipe-in error logs. hey-cli uses built-in OS heuristics to understand the context before generating a solution."
        },
        governance: {
            title: "Governance Engine",
            description: "The core of hey-cli's safety. It intercepts every command before execution, checking it against <code>~/.hey-rules.json</code>. Dangerous commands (like <code>rm -rf /</code>) are blocked or restricted, requiring manual keyword confirmation to proceed."
        },
        ollama: {
            title: "Ollama (Local LLM)",
            description: "The intelligence engine. Runs locally via <code>localhost:11434</code>. It processes your request using private, high-performance models (like <code>gpt-oss</code>) without any data ever leaving your machine."
        },
        runner: {
            title: "Command Runner",
            description: "The execution layer. It translates the LLM's logical plan into final, OS-specific shell commands and handles execution levels—from 'Dry-run' (Level 0) to automated 'Troubleshooter' (Level 3)."
        }
    };

    const flowContainer = document.querySelector('.flow-container');
    const nodeTitle = document.getElementById('node-title');
    const nodeDescription = document.getElementById('node-description');
    const nodeDetails = document.querySelector('.node-details-container');

    if (flowContainer) {
        flowContainer.addEventListener('click', (event) => {
            const step = event.target.closest('.flow-step');
            if (!step) return;

            const nodeId = step.getAttribute('data-node');
            if (nodeData[nodeId]) {
                // Update active state
                document.querySelectorAll('.flow-step').forEach(s => s.classList.remove('active'));
                step.classList.add('active');

                // Update content with a quick fade animation refresh
                nodeDetails.style.animation = 'none';
                nodeDetails.offsetHeight; // trigger reflow
                nodeDetails.style.animation = null;

                nodeTitle.innerText = nodeData[nodeId].title;
                nodeDescription.innerHTML = nodeData[nodeId].description;
            }
        });
    }

    // --- 4. Intersection Observer for Scroll Animations ---
    const observerOptions = { threshold: 0.1 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .install-container, .flow-step, .node-details-container').forEach(el => {
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });

    // --- 3. Initial Icon Render ---
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    console.log('hey-cli: Initialization complete.');
});
