document.addEventListener("DOMContentLoaded", () => {
    const applyBtn = document.getElementById("applyCoupon");
    const couponInput = document.getElementById("couponCode");
    const messageEl = document.getElementById("couponMessage");
    const discountLine = document.getElementById("discountLine");
    const discountSpan = document.getElementById("discount");
    const totalSpan = document.getElementById("total");
    const subtotal = parseFloat(document.getElementById("subtotal").textContent);

    applyBtn.addEventListener("click", () => {
        const code = couponInput.value.trim();
        if (!code) {
            messageEl.textContent = "Please enter a coupon code.";
            messageEl.style.color = "#dc3545";
            return;
        }

        fetch("/orders/apply-coupon/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: `code=${encodeURIComponent(code)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                discountSpan.textContent = parseFloat(data.discount).toFixed(2);
                totalSpan.textContent = (subtotal - parseFloat(data.discount)).toFixed(2);
                discountLine.style.display = "block";
                messageEl.textContent = data.message;
                messageEl.style.color = "#28a745";
            } else {
                messageEl.textContent = data.message;
                messageEl.style.color = "#dc3545";
                discountLine.style.display = "none";
                totalSpan.textContent = subtotal.toFixed(2);
            }
        })
        .catch(err => console.error(err));
    });
});
