document.addEventListener("DOMContentLoaded", function() {
    const variantSelect = document.getElementById("variantSelect");
    const stockInfo = document.getElementById("stockInfo");

    function updateStock() {
        if (!variantSelect) return;
        const selectedOption = variantSelect.options[variantSelect.selectedIndex];
        const stock = selectedOption.dataset.stock;
        stockInfo.innerText = stock > 0 ? `In stock: ${stock} units` : "Out of stock";
    }

    if (variantSelect) {
        variantSelect.addEventListener("change", updateStock);
        updateStock(); // initial load
    }
});
