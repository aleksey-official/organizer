<?php
session_start();
require_once 'config.php'; // файл с подключением к БД

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $login = $_POST['login'];
    $password = $_POST['password'];

    // Используем подготовленное выражение
    $stmt = $db->prepare("SELECT id, password_hash FROM users WHERE username = ?");
    $stmt->bind_param("s", $login);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($row = $result->fetch_assoc()) {
        // Пользователь найден, проверяем пароль
        if (password_verify($password, $row['password_hash'])) {
            $_SESSION['user_id'] = $row['id'];
            $_SESSION['username'] = $login;
            header("Location: index.php");
            exit;
        } else {
            $error = "Неверный пароль";
        }
    } else {
        $error = "Пользователь не найден";
    }
    $stmt->close();
}
?>
<!-- Форма входа -->
<form method="post">
    Логин: <input type="text" name="login"><br>
    Пароль: <input type="password" name="password"><br>
    <input type="submit" value="Войти">
    <?php if (isset($error)) echo "<p style='color:red;'>$error</p>"; ?>
</form>