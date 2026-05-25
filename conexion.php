<?php
$conexion = mysqli_connect("db", "root", "root", "bd_estudiantes");

if (!$conexion) {
    die("Error de conexión: " . mysqli_connect_error());
}
?>