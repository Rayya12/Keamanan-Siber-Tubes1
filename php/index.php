<?php
session_start();

// CEK LOGIN (WAJIB PALING ATAS TANPA OUTPUT)
if (!isset($_SESSION['logged_in'])) {
    header("Location: login.php");
    exit;
}

// setelah lolos login, load database
include 'app.php';

// handle tambah siswa
if (isset($_POST['add'])) {
    addStudent($_POST['name'], $_POST['age'], $_POST['grade']);
}

// ambil data siswa
$students = selectStudents();
?>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daftar Siswa</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Manajemen Siswa</h1>
            <p>Tambah, Update, Hapus dan Lihat Daftar Siswa</p>
        </header>

        <!-- Form untuk menambahkan siswa -->
        <section class="form-section">
            <h2>Tambah Siswa Baru</h2>
            <form action="index.php" method="POST">
                <label for="name">Nama:</label>
                <input type="text" id="name" name="name" required>

                <label for="age">Usia:</label>
                <input type="number" id="age" name="age" required>

                <label for="grade">Kelas:</label>
                <input type="text" id="grade" name="grade" required>

                <button type="submit" name="add">Tambah Siswa</button>
            </form>
        </section>

        <!-- Tabel untuk menampilkan daftar siswa -->
        <section class="students-list">
            <h2>Daftar Siswa</h2>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nama</th>
                        <th>Usia</th>
                        <th>Kelas</th>
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
                    <?php
                        // Ambil data siswa dari database
                        // $students = selectStudents();
                        if ($students) {
                            foreach ($students as $student) {
                                echo "<tr>
                                    <td>" . htmlspecialchars($student['id']) . "</td>
                                    <td>" . htmlspecialchars($student['name']) . "</td>
                                    <td>" . htmlspecialchars($student['age']) . "</td>
                                    <td>" . htmlspecialchars($student['grade']) . "</td>
                                    <td>
                                        <a href='edit.php?id=" . $student['id'] . "' class='btn btn-update'>Edit</a>
                                        <a href='delete.php?id=" . $student['id'] . "' class='btn btn-delete' onclick='return confirm(\"Yakin ingin menghapus?\")'>Hapus</a>
                                    </td>
                                </tr>";
                            }
                        }
                    ?>
                </tbody>
            </table>
        </section>
<a href="logout.php">Logout</a>
        <footer>
            <p>&copy; 2024 Manajemen Siswa - ALH</p>
        </footer>
    </div>

    <!-- PHP untuk menambahkan siswa -->
    <?php
    if (isset($_POST['add'])) {
        $name = $_POST['name'];
        $age = $_POST['age'];
        $grade = $_POST['grade'];
        addStudent($name, $age, $grade);
    }

    // PHP untuk menghapus siswa berdasarkan ID
    if (isset($_GET['delete'])) {
        $id = $_GET['delete'];
        deleteStudent($id);
    }
    ?>
</body>
</html>
