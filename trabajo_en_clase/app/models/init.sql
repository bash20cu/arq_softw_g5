-- 1. Roles
INSERT INTO Rol (nombre_rol) VALUES 
('Administrador'),
('Ventas'),
('Soporte');

-- 2. Personas
INSERT INTO Persona (cedula, nombre, apellido, email, telefono)
VALUES 
('101101111', 'Miguel', 'Admin', 'miguel@example.com', '88888888'),
('202220222', 'Carlo', 'Ventas', 'carlo@example.com', '88888889'),
('303330333', 'Brandon', 'Soporte', 'brandon@example.com', '88888890');

-- 3. Usuarios
INSERT INTO Usuario (cedula_persona, username, password_hash, id_rol, activo)
VALUES 
('101101111', 'miguel_admin', 'admin123', 1, TRUE),
('202220222', 'carlo_ventas', 'ventas123', 2, TRUE),
('303330333', 'brandon_soporte', 'soporte123', 3, TRUE);