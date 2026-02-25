DROP DATABASE IF EXISTS sistema_ventas;
CREATE DATABASE sistema_ventas;
USE sistema_ventas;
-- =====================================================
-- 1. CATÁLOGOS BASE
-- =====================================================

CREATE TABLE Rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Provincia (
    id_provincia INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Canton (
    id_canton INT PRIMARY KEY,
    id_provincia INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT fk_canton_provincia FOREIGN KEY (id_provincia) REFERENCES Provincia(id_provincia)
);

CREATE TABLE Distrito (
    id_distrito INT PRIMARY KEY,
    id_canton INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT fk_distrito_canton FOREIGN KEY (id_canton) REFERENCES Canton(id_canton)
);

-- =====================================================
-- 2. ENTIDAD PERSONA (Cédula como PK)
-- =====================================================

CREATE TABLE Persona (
    cedula VARCHAR(20) PRIMARY KEY, -- Ahora es tu identificador principal
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    id_distrito INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_persona_distrito FOREIGN KEY (id_distrito) REFERENCES Distrito(id_distrito)
);

CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    cedula_persona VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    id_rol INT NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_usuario_persona FOREIGN KEY (cedula_persona) REFERENCES Persona(cedula),
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES Rol(id_rol)
);

CREATE TABLE Cliente (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    cedula_persona VARCHAR(20) UNIQUE NOT NULL,
    puntos_lealtad INT DEFAULT 0,
    estado_cliente ENUM('Activo', 'Inactivo', 'VIP', 'Moroso') DEFAULT 'Activo',
    CONSTRAINT fk_cliente_persona FOREIGN KEY (cedula_persona) REFERENCES Persona(cedula)
);

-- =====================================================
-- 3. MARKETING Y CAMPAÑAS
-- =====================================================

CREATE TABLE Campania (
    id_campania INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    descripcion TEXT
);

-- Nueva tabla para gestionar el envío/medio de la campaña
CREATE TABLE Campania_Envio (
    id_envio INT AUTO_INCREMENT PRIMARY KEY,
    id_campania INT NOT NULL,
    cedula_persona VARCHAR(20) NOT NULL,
    medio_envio ENUM('Email', 'Telefono', 'WhatsApp', 'SMS') NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exitoso BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_envio_campania FOREIGN KEY (id_campania) REFERENCES Campania(id_campania),
    CONSTRAINT fk_envio_persona FOREIGN KEY (cedula_persona) REFERENCES Persona(cedula)
);

-- =====================================================
-- 4. PRODUCTOS Y VENTAS
-- =====================================================

CREATE TABLE Producto (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    precio_actual DECIMAL(12, 2) NOT NULL,
    stock INT DEFAULT 0,
    id_campania INT, -- Para saber si el producto es parte de una promo
    CONSTRAINT fk_producto_campania FOREIGN KEY (id_campania) REFERENCES Campania(id_campania) ON DELETE SET NULL
);

CREATE TABLE Orden_Compra (
    id_orden INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_usuario INT NOT NULL, -- Vendedor
    fecha_orden DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('Pendiente', 'Procesado', 'Enviado', 'Entregado', 'Cancelado') DEFAULT 'Pendiente',
    CONSTRAINT fk_orden_cliente FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    CONSTRAINT fk_orden_usuario FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Detalle_Orden (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_venta DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_detalle_orden FOREIGN KEY (id_orden) REFERENCES Orden_Compra(id_orden),
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
);

CREATE TABLE Factura (
    id_factura INT AUTO_INCREMENT PRIMARY KEY,
    id_orden INT UNIQUE NOT NULL,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    monto_total DECIMAL(12, 2) NOT NULL,
    fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_factura_orden FOREIGN KEY (id_orden) REFERENCES Orden_Compra(id_orden)
);

-- =====================================================
-- 5. SEGUIMIENTO DE CASOS (SOPORTE)
-- =====================================================

CREATE TABLE Caso_Soporte (
    id_caso INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_usuario_asignado INT,
    id_orden INT,
    titulo VARCHAR(200) NOT NULL,
    descripcion_inicial TEXT,
    prioridad ENUM('Baja', 'Media', 'Alta', 'Urgente') DEFAULT 'Media',
    estado ENUM('Nuevo', 'En Análisis', 'Esperando Cliente', 'Resuelto', 'Cerrado') DEFAULT 'Nuevo',
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_caso_cliente FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    CONSTRAINT fk_caso_usuario FOREIGN KEY (id_usuario_asignado) REFERENCES Usuario(id_usuario),
    CONSTRAINT fk_caso_orden FOREIGN KEY (id_orden) REFERENCES Orden_Compra(id_orden)
);

