DROP DATABASE IF EXISTS {{DB_NAME}};
CREATE DATABASE {{DB_NAME}};
-- =====================================================
-- 1. CATÁLOGOS BASE
-- =====================================================

CREATE TABLE rol (
    id_rol SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE provincia (
    id_provincia INTEGER PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE canton (
    id_canton INTEGER PRIMARY KEY,
    id_provincia INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT fk_canton_provincia FOREIGN KEY (id_provincia) REFERENCES provincia(id_provincia)
);

CREATE TABLE distrito (
    id_distrito INTEGER PRIMARY KEY,
    id_canton INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    CONSTRAINT fk_distrito_canton FOREIGN KEY (id_canton) REFERENCES canton(id_canton)
);

-- =====================================================
-- 2. ENTIDAD PERSONA (Cédula como PK)
-- =====================================================

CREATE TABLE persona (
    cedula VARCHAR(20) PRIMARY KEY, -- Ahora es tu identificador principal
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    id_distrito INTEGER,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_persona_distrito FOREIGN KEY (id_distrito) REFERENCES distrito(id_distrito)
);

CREATE TABLE usuario (
    id_usuario SERIAL PRIMARY KEY,
    cedula_persona VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    id_rol INTEGER NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_usuario_persona FOREIGN KEY (cedula_persona) REFERENCES persona(cedula),
    CONSTRAINT fk_usuario_rol FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

CREATE TABLE cliente (
    id_cliente SERIAL PRIMARY KEY,
    cedula_persona VARCHAR(20) UNIQUE,
    tipo_cliente VARCHAR(20) NOT NULL DEFAULT 'Persona' CHECK (tipo_cliente IN ('Persona', 'Empresa')),
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100),
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    id_distrito INTEGER,
    puntos_lealtad INTEGER DEFAULT 0,
    estado_cliente VARCHAR(20) DEFAULT 'Activo' CHECK (estado_cliente IN ('Activo', 'Inactivo', 'VIP', 'Moroso')),
    CONSTRAINT fk_cliente_persona FOREIGN KEY (cedula_persona) REFERENCES persona(cedula),
    CONSTRAINT fk_cliente_distrito FOREIGN KEY (id_distrito) REFERENCES distrito(id_distrito)
);

-- =====================================================
-- 3. MARKETING Y CAMPAÑAS
-- =====================================================

CREATE TABLE campania (
    id_campania SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    descripcion TEXT
);

-- Nueva tabla para gestionar el envío/medio de la campaña
CREATE TABLE campania_envio (
    id_envio SERIAL PRIMARY KEY,
    id_campania INTEGER NOT NULL,
    cedula_persona VARCHAR(20) NOT NULL,
    medio_envio VARCHAR(20) NOT NULL CHECK (medio_envio IN ('Email', 'Telefono', 'WhatsApp', 'SMS')),
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exitoso BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_envio_campania FOREIGN KEY (id_campania) REFERENCES campania(id_campania),
    CONSTRAINT fk_envio_persona FOREIGN KEY (cedula_persona) REFERENCES persona(cedula)
);

-- =====================================================
-- 4. PRODUCTOS Y VENTAS
-- =====================================================

CREATE TABLE producto (
    id_producto SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL UNIQUE,
    precio_actual DECIMAL(12, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    id_campania INTEGER, -- Para saber si el producto es parte de una promo
    CONSTRAINT fk_producto_campania FOREIGN KEY (id_campania) REFERENCES campania(id_campania) ON DELETE SET NULL
);

CREATE TABLE orden_compra (
    id_orden SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL, -- Vendedor
    fecha_orden TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'Procesado', 'Enviado', 'Entregado', 'Cancelado')),
    CONSTRAINT fk_orden_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    CONSTRAINT fk_orden_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE detalle_orden (
    id_detalle SERIAL PRIMARY KEY,
    id_orden INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_venta DECIMAL(12, 2) NOT NULL,
    CONSTRAINT fk_detalle_orden FOREIGN KEY (id_orden) REFERENCES orden_compra(id_orden),
    CONSTRAINT fk_detalle_producto FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

CREATE TABLE factura (
    id_factura SERIAL PRIMARY KEY,
    id_orden INTEGER UNIQUE NOT NULL,
    numero_factura VARCHAR(50) UNIQUE NOT NULL,
    monto_total DECIMAL(12, 2) NOT NULL,
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_factura_orden FOREIGN KEY (id_orden) REFERENCES orden_compra(id_orden)
);

-- =====================================================
-- 5. SEGUIMIENTO DE CASOS (SOPORTE)
-- =====================================================

CREATE TABLE caso_soporte (
    id_caso SERIAL PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    id_usuario_asignado INTEGER,
    id_orden INTEGER,
    titulo VARCHAR(200) NOT NULL,
    descripcion_inicial TEXT,
    prioridad VARCHAR(20) DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Urgente')),
    estado VARCHAR(20) DEFAULT 'Nuevo' CHECK (estado IN ('Nuevo', 'En Análisis', 'Esperando Cliente', 'Resuelto', 'Cerrado')),
    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_caso_cliente FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente),
    CONSTRAINT fk_caso_usuario FOREIGN KEY (id_usuario_asignado) REFERENCES usuario(id_usuario),
    CONSTRAINT fk_caso_orden FOREIGN KEY (id_orden) REFERENCES orden_compra(id_orden)
);
