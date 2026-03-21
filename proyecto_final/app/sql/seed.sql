IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Administrador')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Administrador')

IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Empleado')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Empleado')

IF NOT EXISTS (SELECT 1 FROM dbo.rol WHERE nombre_rol = 'Cliente')
    INSERT INTO dbo.rol (nombre_rol) VALUES ('Cliente')

IF NOT EXISTS (SELECT 1 FROM dbo.persona WHERE cedula = '101010101')
    INSERT INTO dbo.persona (cedula, nombre, apellido, email, telefono)
    VALUES ('101010101', 'Admin', 'Equipo5', 'admin@propat.local', '88880000')

IF NOT EXISTS (SELECT 1 FROM dbo.usuario WHERE username = 'admin')
    INSERT INTO dbo.usuario (cedula_persona, username, password_hash, id_rol, activo)
    VALUES (
        '101010101',
        'admin',
        'scrypt:32768:8:1$LkITk9qFo5KjzbAv$08199bf9a4f3046e4a913415d699a1da7d1c2f3ecc0b22444512f9b0385f386bfdefe86c109a818f8ff39c598c0c5499778232875a0c4ca69c325b9e729adec5',
        1,
        1
    )
