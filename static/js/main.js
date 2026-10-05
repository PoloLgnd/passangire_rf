document.addEventListener('DOMContentLoaded', function() {
    // Ждем, пока вся страница загрузится
    var modalButtons = document.querySelectorAll('[data-bs-toggle="modal"]');
    
    // Находим все кнопки, которые должны открывать модалки
    modalButtons.forEach(function(button) {
        var targetId = button.getAttribute('data-bs-target');
        var modalElement = document.querySelector(targetId);

        if (modalElement) {
            new bootstrap.Modal(modalElement);
        }
    });
});