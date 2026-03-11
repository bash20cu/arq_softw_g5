USE {{DB_NAME}};

INSERT IGNORE INTO Rol (id_rol, nombre_rol) VALUES
  (1, 'Admin'),
  (2, 'Vendedor'),
  (3, 'Soporte'),
  (4, 'Cliente');

INSERT IGNORE INTO Provincia (id_provincia, nombre) VALUES
  (1, 'San Jose'),
  (2, 'Alajuela'),
  (3, 'Cartago');

INSERT IGNORE INTO Canton (id_canton, id_provincia, nombre) VALUES
  (101, 1, 'Central'),
  (201, 2, 'Central'),
  (301, 3, 'Central');

INSERT IGNORE INTO Distrito (id_distrito, id_canton, nombre) VALUES
  (10101, 101, 'Catedral'),
  (20101, 201, 'Alajuela'),
  (30101, 301, 'Oriental');
