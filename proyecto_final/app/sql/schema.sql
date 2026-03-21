IF OBJECT_ID('dbo.pago', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.pago (
        id_pago INT IDENTITY(1,1) PRIMARY KEY,
        id_orden INT NOT NULL,
        proveedor NVARCHAR(50) NOT NULL,
        referencia_externa NVARCHAR(120) NULL,
        monto DECIMAL(12,2) NOT NULL,
        estado NVARCHAR(30) NOT NULL DEFAULT 'Pendiente',
        fecha_pago DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
END

IF OBJECT_ID('dbo.detalle_orden', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.detalle_orden (
        id_detalle INT IDENTITY(1,1) PRIMARY KEY,
        id_orden INT NOT NULL,
        id_producto INT NOT NULL,
        cantidad INT NOT NULL,
        precio_venta DECIMAL(12,2) NOT NULL
    )
END

IF OBJECT_ID('dbo.orden_compra', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orden_compra (
        id_orden INT IDENTITY(1,1) PRIMARY KEY,
        id_cliente INT NOT NULL,
        id_usuario INT NOT NULL,
        fecha_orden DATETIME2 NOT NULL DEFAULT SYSDATETIME(),
        estado NVARCHAR(40) NOT NULL DEFAULT 'En preparacion'
    )
END

IF OBJECT_ID('dbo.producto', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.producto (
        id_producto INT IDENTITY(1,1) PRIMARY KEY,
        nombre NVARCHAR(150) NOT NULL,
        descripcion NVARCHAR(500) NULL,
        fotografia_url NVARCHAR(255) NULL,
        color_estilo NVARCHAR(150) NULL,
        codigo_barras NVARCHAR(80) NULL,
        precio_base DECIMAL(12,2) NOT NULL,
        iva_porcentaje DECIMAL(5,2) NOT NULL DEFAULT 13.00,
        precio_actual DECIMAL(12,2) NOT NULL,
        stock INT NOT NULL DEFAULT 0,
        activo BIT NOT NULL DEFAULT 1
    )
END

IF OBJECT_ID('dbo.usuario', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.usuario (
        id_usuario INT IDENTITY(1,1) PRIMARY KEY,
        cedula_persona NVARCHAR(20) NOT NULL,
        username NVARCHAR(50) NOT NULL,
        password_hash NVARCHAR(255) NOT NULL,
        id_rol INT NOT NULL,
        activo BIT NOT NULL DEFAULT 1
    )
END

IF OBJECT_ID('dbo.cliente', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.cliente (
        id_cliente INT IDENTITY(1,1) PRIMARY KEY,
        cedula_persona NVARCHAR(20) NULL,
        tipo_cliente NVARCHAR(20) NOT NULL DEFAULT 'Persona',
        nombre NVARCHAR(100) NOT NULL,
        apellido NVARCHAR(100) NULL,
        email NVARCHAR(150) NOT NULL,
        telefono NVARCHAR(20) NULL,
        direccion NVARCHAR(255) NULL,
        id_distrito INT NULL,
        puntos_lealtad INT NOT NULL DEFAULT 0,
        estado_cliente NVARCHAR(20) NOT NULL DEFAULT 'Activo'
    )
END

IF OBJECT_ID('dbo.persona', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.persona (
        cedula NVARCHAR(20) PRIMARY KEY,
        nombre NVARCHAR(100) NOT NULL,
        apellido NVARCHAR(100) NOT NULL,
        email NVARCHAR(150) NOT NULL,
        telefono NVARCHAR(20) NULL,
        id_distrito INT NULL,
        fecha_registro DATETIME2 NOT NULL DEFAULT SYSDATETIME()
    )
END

IF OBJECT_ID('dbo.distrito', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.distrito (
        id_distrito INT PRIMARY KEY,
        id_canton INT NOT NULL,
        nombre NVARCHAR(50) NOT NULL
    )
END

IF OBJECT_ID('dbo.canton', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.canton (
        id_canton INT PRIMARY KEY,
        id_provincia INT NOT NULL,
        nombre NVARCHAR(50) NOT NULL
    )
END

IF OBJECT_ID('dbo.provincia', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.provincia (
        id_provincia INT PRIMARY KEY,
        nombre NVARCHAR(50) NOT NULL
    )
END

IF OBJECT_ID('dbo.rol', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.rol (
        id_rol INT IDENTITY(1,1) PRIMARY KEY,
        nombre_rol NVARCHAR(50) NOT NULL
    )
END

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'uq_persona_email' AND object_id = OBJECT_ID('dbo.persona'))
    CREATE UNIQUE INDEX uq_persona_email ON dbo.persona(email)

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'uq_usuario_username' AND object_id = OBJECT_ID('dbo.usuario'))
    CREATE UNIQUE INDEX uq_usuario_username ON dbo.usuario(username)

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'uq_usuario_cedula_persona' AND object_id = OBJECT_ID('dbo.usuario'))
    CREATE UNIQUE INDEX uq_usuario_cedula_persona ON dbo.usuario(cedula_persona)

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'uq_cliente_cedula_persona' AND object_id = OBJECT_ID('dbo.cliente'))
    CREATE UNIQUE INDEX uq_cliente_cedula_persona ON dbo.cliente(cedula_persona) WHERE cedula_persona IS NOT NULL

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'uq_producto_nombre' AND object_id = OBJECT_ID('dbo.producto'))
    CREATE UNIQUE INDEX uq_producto_nombre ON dbo.producto(nombre)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_canton_provincia')
    ALTER TABLE dbo.canton ADD CONSTRAINT fk_canton_provincia FOREIGN KEY (id_provincia) REFERENCES dbo.provincia(id_provincia)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_distrito_canton')
    ALTER TABLE dbo.distrito ADD CONSTRAINT fk_distrito_canton FOREIGN KEY (id_canton) REFERENCES dbo.canton(id_canton)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_persona_distrito')
    ALTER TABLE dbo.persona ADD CONSTRAINT fk_persona_distrito FOREIGN KEY (id_distrito) REFERENCES dbo.distrito(id_distrito)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_cliente_persona')
    ALTER TABLE dbo.cliente ADD CONSTRAINT fk_cliente_persona FOREIGN KEY (cedula_persona) REFERENCES dbo.persona(cedula)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_cliente_distrito')
    ALTER TABLE dbo.cliente ADD CONSTRAINT fk_cliente_distrito FOREIGN KEY (id_distrito) REFERENCES dbo.distrito(id_distrito)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_usuario_persona')
    ALTER TABLE dbo.usuario ADD CONSTRAINT fk_usuario_persona FOREIGN KEY (cedula_persona) REFERENCES dbo.persona(cedula)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_usuario_rol')
    ALTER TABLE dbo.usuario ADD CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES dbo.rol(id_rol)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_orden_cliente')
    ALTER TABLE dbo.orden_compra ADD CONSTRAINT fk_orden_cliente FOREIGN KEY (id_cliente) REFERENCES dbo.cliente(id_cliente)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_orden_usuario')
    ALTER TABLE dbo.orden_compra ADD CONSTRAINT fk_orden_usuario FOREIGN KEY (id_usuario) REFERENCES dbo.usuario(id_usuario)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_detalle_orden')
    ALTER TABLE dbo.detalle_orden ADD CONSTRAINT fk_detalle_orden FOREIGN KEY (id_orden) REFERENCES dbo.orden_compra(id_orden)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_detalle_producto')
    ALTER TABLE dbo.detalle_orden ADD CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES dbo.producto(id_producto)

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'fk_pago_orden')
    ALTER TABLE dbo.pago ADD CONSTRAINT fk_pago_orden FOREIGN KEY (id_orden) REFERENCES dbo.orden_compra(id_orden)
