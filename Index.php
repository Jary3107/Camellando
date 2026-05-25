<!DOCTYPE html>
<html>
<head>
    <title>Registro</title>
</head>
<body>

<h2>Registrar estudiante</h2>

<form action="guardar.php" method="POST">
    Nombre: <input type="text" name="nombre" required><br><br>
    Correo: <input type="email" name="correo" required><br><br>
    
    <button type="submit">Guardar</button>
</form>

<br>
<a href="listar.php">Ver estudiantes</a>

</body>
</html>