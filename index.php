<?php require_once 'functions.php';
$currentMonth = $_GET['month'] ?? date('Y-m');
$timestamp = strtotime($currentMonth . '-01');
$month = date('m', $timestamp);
$year = date('Y', $timestamp);
$prevMonth = date('Y-m', strtotime('-1 month', $timestamp));
$nextMonth = date('Y-m', strtotime('+1 month', $timestamp));
$firstDayOfMonth = date('w', $timestamp);
$daysInMonth = date('t', $timestamp);
$monthName = date('F Y', $timestamp);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Organizer</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        td, th { border: 1px solid #ccc; padding: 10px; text-align: center; }
        td { height: 80px; cursor: pointer; }
        .other-month { background-color: #f0f0f0; }
        #info-panel { margin-top: 20px; border: 1px solid #ccc; padding: 10px; }
        #info-content { white-space: pre-wrap; }
    </style>
</head>
<body>
    <div>
        <?php if (isLoggedIn()): ?>
            Hello, <?= htmlspecialchars(getUserName()) ?>! <a href="logout.php">Logout</a>
        <?php else: ?>
            <a href="login.php">Login</a> | <a href="register.php">Register</a>
        <?php endif; ?>
    </div>
    <h2><?= $monthName ?></h2>
    <div>
        <a href="?month=<?= $prevMonth ?>">Previous</a> |
        <a href="?month=<?= $nextMonth ?>">Next</a>
    </div>
    <table>
        <tr><th>Sun</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th></tr>
        <tr>
        <?php
        for ($i = 0; $i < $firstDayOfMonth; $i++) echo '<td class="other-month"></td>';
        for ($day = 1; $day <= $daysInMonth; $day++) {
            $date = sprintf('%04d-%02d-%02d', $year, $month, $day);
            echo "<td data-date=\"$date\">$day</td>";
            if (($firstDayOfMonth + $day) % 7 == 0) echo '</tr><tr>';
        }
        $remaining = 7 - (($firstDayOfMonth + $daysInMonth) % 7);
        if ($remaining < 7) for ($i = 0; $i < $remaining; $i++) echo '<td class="other-month"></td>';
        ?>
        </tr>
    </table>
    <div id="info-panel">
        <h3>Information for <span id="selected-date"></span></h3>
        <div id="info-content"></div>
        <?php if (isLoggedIn()): ?>
            <div id="edit-area" style="display:none;">
                <textarea id="edit-description" rows="5" cols="50"></textarea><br>
                <button id="save-btn">Save</button>
                <button id="cancel-btn">Cancel</button>
            </div>
            <button id="edit-btn" style="display:none;">Edit</button>
        <?php endif; ?>
    </div>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const cells = document.querySelectorAll('td[data-date]');
        const selectedDateSpan = document.getElementById('selected-date');
        const infoContent = document.getElementById('info-content');
        <?php if (isLoggedIn()): ?>
        const editBtn = document.getElementById('edit-btn');
        const editArea = document.getElementById('edit-area');
        const editDescription = document.getElementById('edit-description');
        const saveBtn = document.getElementById('save-btn');
        const cancelBtn = document.getElementById('cancel-btn');
        let currentDate = null;
        <?php endif; ?>

        function loadDate(date) {
            fetch('api/get_day.php?date=' + date)
                .then(response => response.json())
                .then(data => {
                    selectedDateSpan.textContent = date;
                    infoContent.textContent = data.description || 'No information for this day.';
                    <?php if (isLoggedIn()): ?>
                    currentDate = date;
                    if (data.can_edit) {
                        editBtn.style.display = 'block';
                        editArea.style.display = 'none';
                    } else {
                        editBtn.style.display = 'none';
                    }
                    <?php endif; ?>
                });
        }

        cells.forEach(cell => cell.addEventListener('click', () => loadDate(cell.dataset.date)));

        <?php if (isLoggedIn()): ?>
        editBtn.addEventListener('click', () => {
            editDescription.value = infoContent.textContent === 'No information for this day.' ? '' : infoContent.textContent;
            editBtn.style.display = 'none';
            editArea.style.display = 'block';
        });

        saveBtn.addEventListener('click', () => {
            fetch('api/save_day.php', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'date=' + encodeURIComponent(currentDate) + '&description=' + encodeURIComponent(editDescription.value)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    infoContent.textContent = editDescription.value || 'No information for this day.';
                    editArea.style.display = 'none';
                    editBtn.style.display = 'block';
                } else {
                    alert('Error: ' + data.error);
                }
            });
        });

        cancelBtn.addEventListener('click', () => {
            editArea.style.display = 'none';
            editBtn.style.display = 'block';
        });
        <?php endif; ?>
    });
    </script>
</body>
</html>