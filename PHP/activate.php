<?php
header('Content-Type: application/json; charset=UTF-8');

function json_response($status, $message) {
    echo json_encode([
        "status" => $status,
        "message" => htmlspecialchars($message, ENT_QUOTES, 'UTF-8') // Chặn XSS nếu message hiển thị HTML
    ]);
    exit;
}

$servername = "127.0.0.1";
$db_username = "root";
$db_password = "mk";
$dbname = "TDC";
$TIMEOUT = 1;

$pdo = new mysqli($servername, $db_username, $db_password, $dbname);
if ($pdo->connect_error) {
    json_response("error", "Không thể kết nối cơ sở dữ liệu.");
}
$pdo->set_charset("utf8mb4");

$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

$username = trim($data['username'] ?? '');
$password = trim($data['password'] ?? '');
$uuid     = trim($data['uuid'] ?? '');

if (empty($username) || empty($password) || empty($uuid)) {
    json_response("error", "Thiếu dữ liệu.");
}

// Validate username tránh SQL injection và dữ liệu rác
if (!preg_match('/^[a-zA-Z0-9_]{3,50}$/', $username)) {
    json_response("error", "Tên người dùng không hợp lệ.");
}

try {
    $stmt = $pdo->prepare("SELECT * FROM kich_hoat_tk WHERE username = ? LIMIT 1");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $existing_account = $result->fetch_assoc();

    if ($existing_account && password_verify($password, $existing_account['password'])) {
        $stmt2 = $pdo->prepare("SELECT * FROM quan_ly_key WHERE username = ? LIMIT 1");
        $stmt2->bind_param("s", $username);
        $stmt2->execute();
        $result2 = $stmt2->get_result();
        $t2_acc = $result2->fetch_assoc();

        if (!$t2_acc) {
            json_response("error_no_key", "Không tìm thấy key.");
        }

        try {
            $tg = new DateTime($t2_acc['date']);
        } catch (Exception $e) {
            $tg = new DateTime();
            $tg->modify("-" . ($TIMEOUT + 1) . " minutes");
        }

        $now = new DateTime();
        $timeout_limit = (clone $now)->modify("-{$TIMEOUT} minutes");

        if ($t2_acc['uuid'] === $uuid || $tg < $timeout_limit) {
            $date_now = $now->format('Y-m-d H:i:s');
            $stmt3 = $pdo->prepare("UPDATE quan_ly_key SET uuid = ?, date = ? WHERE username = ?");
            $stmt3->bind_param("sss", $uuid, $date_now, $username);
            $stmt3->execute();

            json_response("success", "Kích hoạt thành công.");
        } else {
            json_response("error", "Thiết bị khác đang sử dụng.");
        }
    } else {
        json_response("error", "Sai tài khoản hoặc mật khẩu.");
    }
} catch (Exception $e) {
    json_response("error", "Lỗi hệ thống.");
}
