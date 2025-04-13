<?php
header('Content-Type: application/json');

require "aes.php";
$aes = new AesEncryption($key);
$key = '';

$servername = "";
$username = "";
$password = "";
$dbname = "";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(['error' => '数据库连接失败: ' . $conn->connect_error]));
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $json = file_get_contents('php://input');
    $data = json_decode($json, true);

    $email = isset($data['email']) ? $data['email'] : null;
    $password = isset($data['password']) ? $data['password'] : null;
    $need_auto_login = isset($data['auto_login']) ? $data['auto_login'] : null;
    $session = isset($data['session']) ? $data['session'] : null;
    
    if (!$session) {
        $sql = "SELECT id, email, password, sessions FROM accounts WHERE email = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $email);
        if (!$email || !$password) {
            http_response_code(400);
            echo json_encode(['error' => 'Email 和 Password 是必需的']);
            exit;
        }
    } else {
        $sql = "SELECT id, email, password, sessions FROM accounts WHERE sessions = ?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $session);
    }
    $stmt->execute();
    $result = $stmt->get_result();
    $row = $result->fetch_assoc();

    if ((!$session) && $row) {
        if ($password === $row['password']) {
            $encrypted_session = "";
            if ($need_auto_login) {
                $session_data = json_encode([
                    'email' => $row['email'],
                    'password' => $row['password'],
                    'user_id' => $row['id'],
                    'time' => time(),
                ]);
                $encrypted_session = $aes->encrypt($session_data);
                $update_sql = "UPDATE accounts SET sessions = ? WHERE id = ?";
                $update_stmt = $conn->prepare($update_sql);
                $update_stmt->bind_param("si", $encrypted_session, $row['id']);
                $update_stmt->execute();
            }
            http_response_code(200);
            if ($row['email'] === "2953911716@qq.com") {
                $role = "dev";
            } else {
                $role = "user";
            }
            echo json_encode(['success' => '登录成功', 'user_id' => $row['id'], "role" => $role, "session" => $encrypted_session, "create_time" => $row['time']]);
        } else {
            http_response_code(401);
            echo json_encode(['error' => '邮箱或密码错误！']);
        }
    } elseif ($session && $row) {
        $decrypt = $aes->decrypt($session);
        $decrypt = json_decode($decrypt, true);
        if ($decrypt) {
            if ($decrypt['password'] === $row['password'] && $decrypt['email'] === $row['email']) {
                http_response_code(200);
                $encrypted_session = "";
                if ($need_auto_login) {
                    $session_data = json_encode([
                        'email' => $row['email'],
                        'password' => $row['password'],
                        'user_id' => $row['id'],
                        'time' => time(),
                    ]);
                    $encrypted_session = $aes->encrypt($session_data);
                    $update_sql = "UPDATE accounts SET sessions = ? WHERE id = ?";
                    $update_stmt = $conn->prepare($update_sql);
                    $update_stmt->bind_param("si", $encrypted_session, $row['id']);
                    $update_stmt->execute();
                }
                if ($row['email'] === "2953911716@qq.com") {
                    $role = "dev";
                } else {
                    $role = "user";
                }
                
                echo json_encode(['success' => '登录成功', 'user_id' => $row['id'], "role" => $role, "session" => $encrypted_session,"create_time" => $row['time']]);
            }
        } else {
            http_response_code(401);
            echo json_encode(['error' => '邮箱或密码错误！']);
        }
    } else {
        http_response_code(401);
        echo json_encode(['error' => '邮箱或密码错误！']);
    }

    $stmt->close();
} else {
    http_response_code(405);
    echo json_encode(['error' => '仅允许 POST 请求']);
}

$conn->close();

?>



