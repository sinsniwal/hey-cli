const commands = {
  uv: 'uv tool install hey-cli-python',
  brew: 'brew tap sinsniwal/hey-cli && brew install hey-cli',
  curl: 'curl -sL https://raw.githubusercontent.com/sinsniwal/hey-cli/main/install.sh | bash',
  scoop: 'scoop install https://raw.githubusercontent.com/sinsniwal/hey-cli/main/scoop/hey-cli.json'
};

function switchInstall(platform) {
  const commandBox = document.getElementById('install-command');
  const buttons = document.querySelectorAll('.tab-btn');
  
  // Update command
  commandBox.innerText = commands[platform];
  
  // Update active button
  buttons.forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
}

function copyCommand() {
  const command = document.getElementById('install-command').innerText;
  const icon = document.getElementById('copy-icon');
  
  navigator.clipboard.writeText(command).then(() => {
    // Basic visual feedback
    const originalIcon = icon.getAttribute('data-lucide');
    icon.setAttribute('data-lucide', 'check');
    lucide.createIcons();
    
    setTimeout(() => {
      icon.setAttribute('data-lucide', 'copy');
      lucide.createIcons();
    }, 2000);
  });
}

// Simple Intersection Observer for animation
document.addEventListener('DOMContentLoaded', () => {
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.feature-card, .install-container').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.6s ease-out';
        observer.observe(el);
    });
});
