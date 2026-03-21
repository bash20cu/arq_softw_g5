-- Disable foreign key checks
SET session_replication_role = 'replica';

TRUNCATE TABLE caso_soporte CASCADE;
TRUNCATE TABLE factura CASCADE;
TRUNCATE TABLE detalle_orden CASCADE;
TRUNCATE TABLE orden_compra CASCADE;
TRUNCATE TABLE producto CASCADE;
TRUNCATE TABLE campania_envio CASCADE;
TRUNCATE TABLE campania CASCADE;
TRUNCATE TABLE cliente CASCADE;
TRUNCATE TABLE usuario CASCADE;
TRUNCATE TABLE persona CASCADE;
TRUNCATE TABLE distrito CASCADE;
TRUNCATE TABLE canton CASCADE;
TRUNCATE TABLE provincia CASCADE;
TRUNCATE TABLE rol CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = 'origin';

INSERT INTO rol (id_rol, nombre_rol) VALUES
  (1, 'Admin'),
  (2, 'Vendedor'),
  (3, 'Soporte'),
  (4, 'Cliente');

INSERT INTO provincia (id_provincia, nombre) VALUES
  (1, 'San Jose'),
  (2, 'Alajuela'),
  (3, 'Cartago');

INSERT INTO canton (id_canton, id_provincia, nombre) VALUES
  (101, 1, 'Central'),
  (201, 2, 'Central'),
  (301, 3, 'Central');

INSERT INTO distrito (id_distrito, id_canton, nombre) VALUES
  (10101, 101, 'Catedral'),
  (20101, 201, 'Alajuela'),
  (30101, 301, 'Oriental');

INSERT INTO persona (cedula, nombre, apellido, email, telefono, id_distrito) VALUES
  ('101110111', 'Miguel', 'Admin', 'miguel.admin@enviosg5.com', '88880001', 10101),
  ('202220222', 'Carlo', 'Vargas', 'carlo.vargas@enviosg5.com', '88880002', 10101),
  ('303330333', 'Brandon', 'Solis', 'brandon.solis@enviosg5.com', '88880003', 10101),
  ('404440444', 'Laura', 'Campos', 'laura.campos@enviosg5.com', '88880004', 10101);

-- password_hash en formato seguro (Werkzeug)
-- usuario: miguel_admin / password: admin123
-- usuario: carlo_ventas / password: ventas123
-- usuario: brandon_soporte / password: soporte123
INSERT INTO usuario (id_usuario, cedula_persona, username, password_hash, id_rol, activo) VALUES
  (1, '101110111', 'miguel_admin', 'scrypt:32768:8:1$XJ9qfMRii5go98Yy$691c68c162df5c6eab07ba33ce76722ebb45567e21e4af57cd6149d9208d7677d56cf107bbd54b42efda66a970c8fd2154f820b07f4bf9caeb8949099a06977a', 1, TRUE),
  (2, '202220222', 'carlo_ventas', 'scrypt:32768:8:1$X7zuO0w6Qy3tpCht$ac7d6f3f1c3f1dcc3eded2eba91aacf7006ef31d1426b39e77d6bf86519484d4c257e58cd8ecfbfe6e4003bb645d5270720d7073c42b52bda5812fa4b80a73a4', 2, TRUE),
  (3, '303330333', 'brandon_soporte', 'scrypt:32768:8:1$m7qgQfX3L0VMeSrF$76b9968fc98421d096ded016240a599c10a305a75ae8a86ead3bc5fad79665ac4006b69ca27fdc1ad605088dec4049c01b0080f4b19204490780ac8c184f0804', 3, TRUE);

INSERT INTO cliente (id_cliente, cedula_persona, tipo_cliente, nombre, apellido, email, telefono, id_distrito, puntos_lealtad, estado_cliente) VALUES
  (1, '202220222', 'Persona', 'Carlo', 'Vargas', 'carlo.vargas@enviosg5.com', '88880002', 10101, 120, 'VIP'),
  (2, '303330333', 'Persona', 'Brandon', 'Solis', 'brandon.solis@enviosg5.com', '88880003', 10101, 25, 'Activo'),
  (3, NULL, 'Empresa', 'Distribuciones Invitadas S.A.', NULL, 'cliente.invitado@enviosg5.com', '88889999', 20101, 0, 'Activo');

INSERT INTO campania (id_campania, nombre, fecha_inicio, fecha_fin, descripcion) VALUES
  (1, 'Promo Envio Express', '2026-02-01', '2026-03-15', 'Descuento para envios urgentes.'),
  (2, 'Temporada Escolar', '2026-03-01', '2026-04-30', 'Campaña comercial para paquetes escolares.');

INSERT INTO campania_envio (id_envio, id_campania, cedula_persona, medio_envio, exitoso) VALUES
  (1, 1, '202220222', 'Email', TRUE),
  (2, 1, '303330333', 'WhatsApp', TRUE);

INSERT INTO producto (id_producto, nombre, precio_actual, stock, id_campania) VALUES
  (1, 'Envio Nacional Estandar', 3500.00, 498, 1),
  (2, 'Envio Internacional Express', 18500.00, 119, 2);

INSERT INTO orden_compra (id_orden, id_cliente, id_usuario, estado) VALUES
  (1, 1, 2, 'Procesado');

INSERT INTO detalle_orden (id_detalle, id_orden, id_producto, cantidad, precio_venta) VALUES
  (1, 1, 1, 2, 3500.00),
  (2, 1, 2, 1, 18500.00);

INSERT INTO factura (id_factura, id_orden, numero_factura, monto_total) VALUES
  (1, 1, 'FAC-2026-0001', 25500.00);

INSERT INTO caso_soporte (id_caso, id_cliente, id_usuario_asignado, id_orden, titulo, descripcion_inicial, prioridad, estado) VALUES
  (1, 1, 3, 1, 'Seguimiento de entrega', 'Cliente solicita confirmacion de entrega.', 'Media', 'En Análisis');

SELECT setval('rol_id_rol_seq', COALESCE((SELECT MAX(id_rol) FROM rol), 1), true);
SELECT setval('usuario_id_usuario_seq', COALESCE((SELECT MAX(id_usuario) FROM usuario), 1), true);
SELECT setval('cliente_id_cliente_seq', COALESCE((SELECT MAX(id_cliente) FROM cliente), 1), true);
SELECT setval('campania_id_campania_seq', COALESCE((SELECT MAX(id_campania) FROM campania), 1), true);
SELECT setval('campania_envio_id_envio_seq', COALESCE((SELECT MAX(id_envio) FROM campania_envio), 1), true);
SELECT setval('producto_id_producto_seq', COALESCE((SELECT MAX(id_producto) FROM producto), 1), true);
SELECT setval('orden_compra_id_orden_seq', COALESCE((SELECT MAX(id_orden) FROM orden_compra), 1), true);
SELECT setval('detalle_orden_id_detalle_seq', COALESCE((SELECT MAX(id_detalle) FROM detalle_orden), 1), true);
SELECT setval('factura_id_factura_seq', COALESCE((SELECT MAX(id_factura) FROM factura), 1), true);
SELECT setval('caso_soporte_id_caso_seq', COALESCE((SELECT MAX(id_caso) FROM caso_soporte), 1), true);
