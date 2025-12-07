<?php
session_start();
if (!isset($_SESSION['logged_in'])) {
    header("Location: login.php");
    exit;
}
?>

<?php
    include 'app.php'; 

    if (isset($_GET['id'])) {
        $id = $_GET['id'];
        deleteStudent($id);
    }

?>