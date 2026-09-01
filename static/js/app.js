document.addEventListener('DOMContentLoaded', function () {
    if (typeof $.fn.persianDatepicker !== 'undefined') {
        $('.jalali-date-input').persianDatepicker({
            format: 'YYYY/MM/DD',
            autoClose: true,
            initialValue: false,
            persianDigit: false
        });
    }

    var newCategoryToggle = document.getElementById('toggle-new-category');
    var newCategoryPanel = document.getElementById('new-category-panel');

    if (newCategoryToggle && newCategoryPanel) {
        newCategoryToggle.addEventListener('click', function (e) {
            e.preventDefault();
            newCategoryPanel.classList.toggle('hidden');
        });
    }
});
