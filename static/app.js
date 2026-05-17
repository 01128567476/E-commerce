document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    if (toasts.length) {
        toasts.forEach((toast) => {
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-12px)';
                setTimeout(() => toast.remove(), 300);
            }, 4500);
        });
    }

    const links = document.querySelectorAll('.nav-links a');
    const currentPath = window.location.pathname;
    links.forEach((link) => {
        if (link.getAttribute('href') === currentPath) {
            link.style.backgroundColor = 'rgba(0, 183, 255, 0.2)';
        }
    });

    const buttons = document.querySelectorAll('.button-secondary, .button-primary');
    buttons.forEach((button) => {
        button.addEventListener('mouseenter', () => {
            button.style.filter = 'brightness(1.05)';
        });
        button.addEventListener('mouseleave', () => {
            button.style.filter = 'none';
        });
    });
});