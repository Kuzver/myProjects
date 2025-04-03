document.addEventListener('DOMContentLoaded', function() {
    // Обработка кнопок выбора веса
    const weightButtons = document.querySelectorAll('.weight-button');
    weightButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Убираем класс "clicked" со всех кнопок
            weightButtons.forEach(btn => btn.classList.remove('clicked'));
            // Добавляем класс "clicked" к нажатой кнопке
            this.classList.add('clicked');
            
            // Получаем значение веса и устанавливаем его в скрытое поле формы
            const weight = this.dataset.weight;
            document.getElementById('selected_weight').value = weight;
            console.log('Выбран вес:', weight, 'кг');
        });
    });

    // Обработка выбора тарифа
    const rateButtons = document.querySelectorAll('input[name="rate"]');
    rateButtons.forEach(button => {
        button.addEventListener('change', function() {
            console.log('Выбран тариф:', this.value);
        });
    });

    // Обработка выбора тарифа (клик по карточке с тарифом)
    const downloadColumns = document.querySelectorAll('.download-column');
    downloadColumns.forEach(column => {
        column.addEventListener('click', function(event) {
            // Предотвращаем переход по ссылке, если это необходимо
            event.preventDefault();

            // Проверяем, есть ли уже класс download-column-active
            if (this.classList.contains('download-column-active')) {
                this.classList.remove('download-column-active'); // Удаляем класс, если он есть
            } else {
                // Сначала удаляем класс у всех других элементов
                downloadColumns.forEach(col => {
                    col.classList.remove('download-column-active');
                });
                this.classList.add('download-column-active'); // Добавляем класс
            }
        });
    });
});
document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();  // Останавливаем стандартную отправку формы

    // Проверка обязательных полей
    const requiredFields = ['#sender_address', '#sender_phone', '#sender_fio', '#recipient_address', '#recipient_phone', '#recipient_fio'];
    let isValid = true;

    requiredFields.forEach(fieldId => {
        const field = document.querySelector(fieldId);
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('error');
        } else {
            field.classList.remove('error');
        }
    });

    if (!isValid) {
        alert("Пожалуйста, заполните все обязательные поля!");
        return;
    }

    // Формируем данные для отправки
    const formData = new FormData(this);

    // Отправляем данные на сервер с помощью fetch
    fetch('process_order.php', {  
        method: 'POST',
        body: formData
    })
    .then(response => response.json()) // Ожидаем JSON-ответ
    .then(data => {
        if (data.success) {
            alert("Заказ успешно создан!");
            window.location.reload();  // Перезагружаем страницу или перенаправляем пользователя
        } else {
            alert("Ошибка: " + data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert("Произошла ошибка при отправке заказа.");
    });
});
