-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS crud_sistema;
USE crud_sistema;

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir dados de exemplo
INSERT INTO usuarios (nome, email, telefone) VALUES
('João Silva', 'joao@email.com', '(11) 99999-1234'),
('Maria Santos', 'maria@email.com', '(11) 98888-5678'),
('Pedro Oliveira', 'pedro@email.com', '(11) 97777-9012');