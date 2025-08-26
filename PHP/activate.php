<?php
// Hàm trả về JSON
function json_response($status, $message) {
    echo json_encode([
        "status" => $status,
        "message" => $message
    ]);
    exit;
}

// Cài đặt kết nối CSDL
$servername = "127.0.0.1";
$db_username = "root";
$db_password = "mk";
$dbname = "TDC";
$TIMEOUT = 1; // phút

$pdo = new mysqli($servername, $db_username, $db_password, $dbname);
if ($pdo->connect_error) {
    json_response("error", "DB connection failed: " . $pdo->connect_error);
}
$pdo->set_charset("utf8mb4");

// Nhận dữ liệu POST JSON
$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

$username = $data['username'] ?? '';
$password = $data['password'] ?? '';
$uuid     = $data['uuid'] ?? '';

if (empty($username) || empty($password) || empty($uuid)) {
    json_response("error", "Loi!!!");
}

$username = trim($username);
$password = trim($password);

try {
    // Kiểm tra tài khoản
    $stmt = $pdo->prepare("SELECT * FROM kich_hoat_tk WHERE username = ? LIMIT 1");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    $existing_account = $result->fetch_assoc();

    if ($existing_account && password_verify($password, $existing_account['password'])) {
        // Tìm khóa thiết bị
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
            // Cập nhật uuid + date
            $date_now = $now->format('Y-m-d H:i:s.u');
            $stmt3 = $pdo->prepare("UPDATE quan_ly_key SET uuid = ?, date = ? WHERE username = ?");
            $stmt3->bind_param("sss", $uuid, $date_now, $username);
            $stmt3->execute();

            json_response("success", "Kich hoat thanh cong.");
        } else {
            json_response("error", "Thiet bi khac dang sai.");
        }
    } else {
        json_response("error", "Loi nguoi dung.");
    }
} catch (Exception $e) {
    json_response("error", $e->getMessage());
}
