IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Administrador')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Administrador')

IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Empleado')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Empleado')

IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Cliente')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Cliente')
