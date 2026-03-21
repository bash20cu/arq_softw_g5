INSERT INTO rol (id_rol, nombre_rol) VALUES
  (1, 'Admin'),
  (2, 'Vendedor'),
  (3, 'Soporte'),
  (4, 'Cliente')
ON CONFLICT (id_rol) DO NOTHING;

INSERT INTO provincia (id_provincia, nombre) VALUES
  (1, 'San Jose'),
  (2, 'Alajuela'),
  (3, 'Cartago')
ON CONFLICT (id_provincia) DO NOTHING;

INSERT INTO canton (id_canton, id_provincia, nombre) VALUES
  (101, 1, 'Central'),
  (201, 2, 'Central'),
  (301, 3, 'Central')
ON CONFLICT (id_canton) DO NOTHING;

INSERT INTO distrito (id_distrito, id_canton, nombre) VALUES
  (10101, 101, 'Catedral'),
  (20101, 201, 'Alajuela'),
  (30101, 301, 'Oriental')
ON CONFLICT (id_distrito) DO NOTHING;
