document.addEventListener('DOMContentLoaded', function () {
    if (typeof $.fn.persianDatepicker !== 'undefined') {
        $('.jalali-date-input').persianDatepicker({
            format: 'YYYY/MM/DD',
            autoClose: true,
            initialValue: false,
            persianDigit: false
        });
    }

    var amountInput = document.getElementById('id_amount');
    var categorySelect = document.getElementById('id_category');
    var newCategoryToggle = document.getElementById('toggle-new-category');
    var newCategoryPanel = document.getElementById('new-category-panel');

    if (newCategoryToggle && newCategoryPanel) {
        newCategoryToggle.addEventListener('click', function (e) {
            e.preventDefault();
            newCategoryPanel.classList.toggle('hidden');
        });
    }

    function filterCategories() {
        if (!amountInput || !categorySelect) return;
        var amount = parseFloat(amountInput.value);
        if (isNaN(amount) || amount === 0) return;
        var type = amount > 0 ? 'income' : 'expense';
        fetch('/transactions/api/categories/?type=' + type)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var current = categorySelect.value;
                categorySelect.innerHTML = '<option value="">---------</option>';
                data.categories.forEach(function (c) {
                    var opt = document.createElement('option');
                    opt.value = c.id;
                    opt.textContent = c.name;
                    if (String(c.id) === current) opt.selected = true;
                    categorySelect.appendChild(opt);
                });
            });
    }

    if (amountInput) {
        amountInput.addEventListener('change', filterCategories);
        amountInput.addEventListener('blur', filterCategories);
    }
});
