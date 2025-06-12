-- Crear base de datos
CREATE DATABASE IF NOT EXISTS aura_inventario;
USE aura_inventario;

-- Tabla de categorías
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT INTO categorias (nombre) VALUES
('Hardware'), ('Software');

-- Tabla de proveedores
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100)
);

INSERT INTO proveedores (nombre, contacto) VALUES
('TechZone S.A.', 'contacto@techzone.com'),
('SoftDistribuciones', 'ventas@softdistrib.com'),
('DigitalWare', 'info@digitalware.com'),
('PC World El Salvador', 'soporte@pcworldsv.com');

-- Tabla de activos tecnológicos
CREATE TABLE activos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    modelo VARCHAR(50),
    licencia_clave VARCHAR(100),
    precio DECIMAL(10,2),
    categoria_id INT,
    proveedor_id INT,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

INSERT INTO activos (nombre, modelo, licencia_clave, precio, categoria_id, proveedor_id) VALUES
('Laptop HP ProBook 450', 'HP-450G8', NULL, 750.00, 1, 1),
('Monitor Dell 24"', 'Dell-P2419H', NULL, 180.00, 1, 4),
('Router TP-Link Archer', 'C80', NULL, 65.00, 1, 1),
('Switch Cisco 16p', 'SG110-16', NULL, 120.00, 1, 1),
('Impresora Epson EcoTank', 'L3250', NULL, 160.00, 1, 4),
('Mouse Logitech Inalámbrico', 'M185', NULL, 12.00, 1, 4),
('Teclado Redragon', 'K552', NULL, 35.00, 1, 1),
('Servidor Torre HP', 'ProLiant ML30', NULL, 1150.00, 1, 1),
('Software Microsoft Office', NULL, 'XXXXX-YYYYY-ZZZZZ-AAAAA-BBBBB', 120.00, 2, 2),
('Licencia Windows 10 Pro', NULL, 'ABC12-DEF34-GHI56-JKL78-MNO90', 145.00, 2, 2),
('Antivirus ESET NOD32', NULL, 'NOD32-2025-KEY01', 35.00, 2, 2),
('Photoshop CC 2023', NULL, 'PS-CC23-ACTKEY', 250.00, 2, 3),
('AutoCAD 2022', NULL, 'ACAD-2022-LIC123', 1600.00, 2, 3),
('Sistema Contable QuickBooks', NULL, 'QB-ES-2025-001', 300.00, 2, 3),
('Sistema de Inventario', NULL, 'INVT-SYS-KEY', 280.00, 2, 3),
('Firewall Fortinet', 'FG-40F', NULL, 450.00, 1, 1),
('Access Point Ubiquiti', 'UAP-AC-LR', NULL, 90.00, 1, 1),
('Software de Asistencia', NULL, 'ASST-SYS-KEY', 199.00, 2, 2),
('Laptop Dell Latitude 3420', '3420-i5', NULL, 790.00, 1, 4),
('Licencia Zoom Pro', NULL, 'ZOOM-KEY-2025', 149.00, 2, 2);

-- Tabla de ubicaciones/inventario
CREATE TABLE ubicaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    activo_id INT,
    area VARCHAR(100),
    cantidad INT,
    FOREIGN KEY (activo_id) REFERENCES activos(id)
);

INSERT INTO ubicaciones (activo_id, area, cantidad) VALUES
(1, 'Oficina Administración', 5),
(2, 'Sala de Reuniones', 3),
(3, 'Red Principal', 2),
(4, 'Rack de Comunicaciones', 1),
(5, 'Recepción', 2),
(6, 'Oficina Técnica', 5),
(7, 'Oficina Técnica', 5),
(8, 'Data Center', 1),
(9, 'Todas las PCs', 15),
(10, 'Todas las PCs', 15),
(11, 'Todas las PCs', 15),
(12, 'Diseño Gráfico', 1),
(13, 'Ingeniería', 1),
(14, 'Finanzas', 1),
(15, 'Almacén', 1),
(16, 'Firewall Rack', 1),
(17, 'Red Inalámbrica', 4),
(18, 'Recursos Humanos', 1),
(19, 'Gerencia', 1),
(20, 'Reuniones y Conferencias', 3);
