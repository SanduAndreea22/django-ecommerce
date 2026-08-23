document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('.add-to-cart-form');
    if (!forms.length) return;

    let toastTimer = null;

    function showToast(message, isError) {
        let toast = document.getElementById('cart-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'cart-toast';
            document.body.appendChild(toast);
        }
        toast.textContent = message;
        toast.className = 'cart-toast' + (isError ? ' cart-toast-error' : '') + ' cart-toast-visible';

        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove('cart-toast-visible');
        }, 2500);
    }

    function updateBadge(count) {
        let badge = document.getElementById('cart-badge');
        const cartLink = document.querySelector('.header nav a[href="/cart/"]');
        if (!count) {
            if (badge) badge.remove();
            return;
        }
        if (!badge && cartLink) {
            badge = document.createElement('span');
            badge.id = 'cart-badge';
            badge.className = 'cart-badge';
            cartLink.appendChild(document.createTextNode(' '));
            cartLink.appendChild(badge);
        }
        if (badge) badge.textContent = count;
    }

    forms.forEach(form => {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const formData = new FormData(form);
            const button = form.querySelector('button[type="submit"]');
            if (button) button.disabled = true;

            fetch(form.action, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    showToast(data.message, !data.success);
                    if (typeof data.cart_count !== 'undefined') {
                        updateBadge(data.cart_count);
                    }
                })
                .catch(() => {
                    // Fără JS/fetch funcțional, formularul tot funcționează ca POST clasic —
                    // aici doar informăm userul că ceva n-a mers la partea "instant".
                    form.submit();
                })
                .finally(() => {
                    if (button) button.disabled = false;
                });
        });
    });
});
