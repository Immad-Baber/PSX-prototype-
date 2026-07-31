document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const themeBtn = document.createElement('button');
    themeBtn.id = 'theme-toggle';
    themeBtn.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: var(--bg-card, #FFFDF7);
        color: var(--text-main, #1B1F23);
        border: 1px solid var(--border-color, #E1DBC8);
        padding: 8px 12px;
        border-radius: 20px;
        cursor: pointer;
        font-family: 'IBM Plex Mono', 'Inter', monospace;
        font-size: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    `;
    
    document.body.appendChild(themeBtn);

    const updateBtnText = (theme) => {
        themeBtn.innerHTML = theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
        if (theme === 'dark') {
            themeBtn.style.background = '#16202C';
            themeBtn.style.color = '#DCE4EC';
            themeBtn.style.borderColor = '#26374A';
        } else {
            themeBtn.style.background = '#FFFDF7';
            themeBtn.style.color = '#1B1F23';
            themeBtn.style.borderColor = '#E1DBC8';
        }
    };

    // Initialize theme from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    updateBtnText(savedTheme);

    // Toggle event
    themeBtn.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateBtnText(newTheme);
    });
});
