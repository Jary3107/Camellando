<?php
include("conexion.php");

$nombre = $_POST['nombre'];
$correo = $_POST['correo'];

$sql = "INSERT INTO estudiantes(nombre, correo) VALUES('$nombre', '$correo')";

$resultado = mysqli_query($conexion, $sql);

if ($resultado) {
    echo "Guardado correctamente <br>";
    echo "<a href='index.php'>Volver</a>";
} else {
    echo "Error: " . mysqli_error($conexion);
}
?>