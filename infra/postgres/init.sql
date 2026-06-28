-- ==========================================
-- 1. CONCEPTION DU MODÈLE DE DONNÉES (DDL)
-- ==========================================

-- Création de la table des utilisateurs (Analystes, Admins)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Création de la table des incidents de sécurité
CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    severity VARCHAR(10) CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
    status VARCHAR(20) DEFAULT 'Open',
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 2. STRATÉGIES DE CONTRÔLE D'ACCÈS (DCL)
-- ==========================================

-- Création des rôles de sécurité
CREATE ROLE admin_role;
CREATE ROLE analyst_role;

-- L'administrateur a tous les droits sur les tables
GRANT ALL PRIVILEGES ON TABLE users, incidents TO admin_role;

-- L'analyste peut voir les utilisateurs, mais ne peut modifier que les incidents
GRANT SELECT ON TABLE users TO analyst_role;
GRANT SELECT, INSERT, UPDATE ON TABLE incidents TO analyst_role;