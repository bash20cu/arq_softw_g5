SET QUOTED_IDENTIFIER ON
SET ANSI_NULLS ON

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
        (SELECT id_rol FROM dbo.rol WHERE nombre_rol = 'Administrador'),
        1
    )

IF NOT EXISTS (SELECT 1 FROM dbo.provincia WHERE id_provincia = 1)
    INSERT INTO dbo.provincia (id_provincia, nombre) VALUES (1, 'San Jose')

IF NOT EXISTS (SELECT 1 FROM dbo.provincia WHERE id_provincia = 2)
    INSERT INTO dbo.provincia (id_provincia, nombre) VALUES (2, 'Alajuela')

IF NOT EXISTS (SELECT 1 FROM dbo.canton WHERE id_canton = 101)
    INSERT INTO dbo.canton (id_canton, id_provincia, nombre) VALUES (101, 1, 'Central')

IF NOT EXISTS (SELECT 1 FROM dbo.canton WHERE id_canton = 201)
    INSERT INTO dbo.canton (id_canton, id_provincia, nombre) VALUES (201, 2, 'Central')

IF NOT EXISTS (SELECT 1 FROM dbo.distrito WHERE id_distrito = 10101)
    INSERT INTO dbo.distrito (id_distrito, id_canton, nombre) VALUES (10101, 101, 'Carmen')

IF NOT EXISTS (SELECT 1 FROM dbo.distrito WHERE id_distrito = 20101)
    INSERT INTO dbo.distrito (id_distrito, id_canton, nombre) VALUES (20101, 201, 'Alajuela')

IF NOT EXISTS (SELECT 1 FROM dbo.persona WHERE cedula = '202020202')
    INSERT INTO dbo.persona (cedula, nombre, apellido, email, telefono, id_distrito)
    VALUES ('202020202', 'Mariana', 'Solano', 'mariana.solano@propat.local', '87770001', 10101)

IF NOT EXISTS (SELECT 1 FROM dbo.persona WHERE cedula = '303030303')
    INSERT INTO dbo.persona (cedula, nombre, apellido, email, telefono, id_distrito)
    VALUES ('303030303', 'Carlos', 'Mora', 'carlos.mora@propat.local', '87770002', 20101)

IF NOT EXISTS (SELECT 1 FROM dbo.persona WHERE cedula = '404040404')
    INSERT INTO dbo.persona (cedula, nombre, apellido, email, telefono, id_distrito)
    VALUES ('404040404', 'Laura', 'Vargas', 'laura.vargas@propat.local', '87770003', 10101)

IF NOT EXISTS (SELECT 1 FROM dbo.usuario WHERE username = 'empleado')
    INSERT INTO dbo.usuario (cedula_persona, username, password_hash, id_rol, activo)
    VALUES (
        '202020202',
        'empleado',
        'scrypt:32768:8:1$LkITk9qFo5KjzbAv$08199bf9a4f3046e4a913415d699a1da7d1c2f3ecc0b22444512f9b0385f386bfdefe86c109a818f8ff39c598c0c5499778232875a0c4ca69c325b9e729adec5',
        (SELECT id_rol FROM dbo.rol WHERE nombre_rol = 'Empleado'),
        1
    )

IF NOT EXISTS (SELECT 1 FROM dbo.usuario WHERE username = 'cliente')
    INSERT INTO dbo.usuario (cedula_persona, username, password_hash, id_rol, activo)
    VALUES (
        '303030303',
        'cliente',
        'scrypt:32768:8:1$LkITk9qFo5KjzbAv$08199bf9a4f3046e4a913415d699a1da7d1c2f3ecc0b22444512f9b0385f386bfdefe86c109a818f8ff39c598c0c5499778232875a0c4ca69c325b9e729adec5',
        (SELECT id_rol FROM dbo.rol WHERE nombre_rol = 'Cliente'),
        1
    )

IF NOT EXISTS (SELECT 1 FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
    INSERT INTO dbo.cliente (
        cedula_persona, tipo_cliente, nombre, apellido, email, telefono, direccion,
        id_distrito, puntos_lealtad, estado_cliente
    )
    VALUES (
        '303030303', 'Persona', 'Carlos', 'Mora', 'carlos.mora@propat.local',
        '87770002', 'Avenida central, casa 24', 20101, 120, 'Activo'
    )

IF NOT EXISTS (SELECT 1 FROM dbo.cliente WHERE email = 'laura.vargas@propat.local')
    INSERT INTO dbo.cliente (
        cedula_persona, tipo_cliente, nombre, apellido, email, telefono, direccion,
        id_distrito, puntos_lealtad, estado_cliente
    )
    VALUES (
        '404040404', 'Persona', 'Laura', 'Vargas', 'laura.vargas@propat.local',
        '87770003', 'Barrio Escalante, local 8', 10101, 45, 'Activo'
    )

IF NOT EXISTS (SELECT 1 FROM dbo.producto WHERE nombre = 'Caja organizadora modular')
    INSERT INTO dbo.producto (
        nombre, descripcion, fotografia_url, color_estilo, codigo_barras,
        precio_base, iva_porcentaje, precio_actual, stock, activo
    )
    VALUES (
        'Caja organizadora modular',
        'Caja plastica apilable para almacenamiento domestico y oficina.',
        '/static/img/productos/caja-organizadora.jpg',
        'Transparente con tapa azul',
        '7440001000011',
        7500.00,
        13.00,
        8475.00,
        35,
        1
    )

IF NOT EXISTS (SELECT 1 FROM dbo.producto WHERE nombre = 'Estante metalico reforzado')
    INSERT INTO dbo.producto (
        nombre, descripcion, fotografia_url, color_estilo, codigo_barras,
        precio_base, iva_porcentaje, precio_actual, stock, activo
    )
    VALUES (
        'Estante metalico reforzado',
        'Estante de cuatro niveles para bodega, taller o comercio.',
        '/static/img/productos/estante-metalico.jpg',
        'Gris industrial',
        '7440001000028',
        42000.00,
        13.00,
        47460.00,
        12,
        1
    )

IF NOT EXISTS (SELECT 1 FROM dbo.producto WHERE nombre = 'Kit etiquetas adhesivas')
    INSERT INTO dbo.producto (
        nombre, descripcion, fotografia_url, color_estilo, codigo_barras,
        precio_base, iva_porcentaje, precio_actual, stock, activo
    )
    VALUES (
        'Kit etiquetas adhesivas',
        'Set de etiquetas resistentes para rotulacion de inventario.',
        '/static/img/productos/etiquetas-adhesivas.jpg',
        'Blanco mate',
        '7440001000035',
        3200.00,
        13.00,
        3616.00,
        80,
        1
    )

IF NOT EXISTS (
    SELECT 1
    FROM dbo.orden_compra
    WHERE id_cliente = (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
      AND estado = 'Pagada'
)
    INSERT INTO dbo.orden_compra (id_cliente, id_usuario, estado)
    VALUES (
        (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local'),
        (SELECT id_usuario FROM dbo.usuario WHERE username = 'empleado'),
        'Pagada'
    )

IF NOT EXISTS (
    SELECT 1
    FROM dbo.detalle_orden
    WHERE id_orden = (
        SELECT TOP 1 id_orden
        FROM dbo.orden_compra
        WHERE id_cliente = (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
          AND estado = 'Pagada'
        ORDER BY id_orden
    )
)
BEGIN
    INSERT INTO dbo.detalle_orden (id_orden, id_producto, cantidad, precio_venta)
    VALUES (
        (
            SELECT TOP 1 id_orden
            FROM dbo.orden_compra
            WHERE id_cliente = (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
              AND estado = 'Pagada'
            ORDER BY id_orden
        ),
        (SELECT id_producto FROM dbo.producto WHERE nombre = 'Caja organizadora modular'),
        2,
        8475.00
    )

    INSERT INTO dbo.detalle_orden (id_orden, id_producto, cantidad, precio_venta)
    VALUES (
        (
            SELECT TOP 1 id_orden
            FROM dbo.orden_compra
            WHERE id_cliente = (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
              AND estado = 'Pagada'
            ORDER BY id_orden
        ),
        (SELECT id_producto FROM dbo.producto WHERE nombre = 'Kit etiquetas adhesivas'),
        3,
        3616.00
    )
END

IF NOT EXISTS (SELECT 1 FROM dbo.pago WHERE referencia_externa = 'SEED-PAYPAL-0001')
    INSERT INTO dbo.pago (
        id_orden, proveedor, referencia_externa, approve_url, monto, estado
    )
    VALUES (
        (
            SELECT TOP 1 id_orden
            FROM dbo.orden_compra
            WHERE id_cliente = (SELECT id_cliente FROM dbo.cliente WHERE email = 'carlos.mora@propat.local')
              AND estado = 'Pagada'
            ORDER BY id_orden
        ),
        'paypal',
        'SEED-PAYPAL-0001',
        'https://sandbox.paypal.com/checkoutnow?token=SEED-PAYPAL-0001',
        27798.00,
        'Completado'
    )
