document.addEventListener('DOMContentLoaded', () => {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.previousElementSibling;
            if (input.type === "password") {
                input.type = "text";
                button.textContent = "🙈";
                button.setAttribute("aria-label", "Hide password");
            } else {
                input.type = "password";
                button.textContent = "👁️";
                button.setAttribute("aria-label", "Show password");
            }
        });
    });
});
