<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/api/innerMethods/isUserAuth.php';  // Проверка авторизации

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Получаем данные из формы
    $rate = $_POST['rate'] ?? '';
    $weight = $_POST['weight'] ?? '';
    $sender_address = $_POST['sender_address'] ?? '';
    $sender_phone = $_POST['sender_phone'] ?? '';
    $sender_fio = $_POST['sender_fio'] ?? '';
    $recipient_address = $_POST['recipient_address'] ?? '';
    $recipient_phone = $_POST['recipient_phone'] ?? '';
    $recipient_fio = $_POST['recipient_fio'] ?? '';

    // Проводим проверки (например, на пустые значения)
    if (!$rate || !$weight || !$sender_address || !$sender_phone || !$sender_fio || !$recipient_address || !$recipient_phone || !$recipient_fio) {
        die("Ошибка: Пожалуйста, заполните все обязательные поля!");
    }

    // Здесь можно записать данные в базу данных
    // Например, вызов функции для сохранения заказа в БД
    // saveOrder($rate, $weight, $sender_address, $sender_phone, $sender_fio, $recipient_address, $recipient_phone, $recipient_fio);

    echo "<h1>Ваш заказ успешно оформлен!</h1>";
    echo "<p>Тариф: $rate ₽</p>";
    echo "<p>Вес: $weight кг</p>";
    echo "<p><strong>Отправитель:</strong> $sender_fio, $sender_phone, $sender_address</p>";
    echo "<p><strong>Получатель:</strong> $recipient_fio, $recipient_phone, $recipient_address</p>";

    // Или перенаправить на страницу с успешным заказом
    // header("Location: success.php");
}
?>