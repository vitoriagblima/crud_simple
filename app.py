from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'crud_sistema'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

@app.route('/')
def index():
    """Rota principal - renderiza a página HTML"""
    return render_template('index.html')

@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    """Listar todos os usuários"""
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios ORDER BY id DESC")
        usuarios = cursor.fetchall()
        return jsonify(usuarios)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/api/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    """Buscar um usuário específico"""
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        
        if usuario:
            return jsonify(usuario)
        return jsonify({'error': 'Usuário não encontrado'}), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/api/usuarios', methods=['POST'])
def create_usuario():
    """Criar um novo usuário"""
    data = request.json
    
    # Validação básica
    if not data.get('nome') or not data.get('email'):
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        query = "INSERT INTO usuarios (nome, email, telefone) VALUES (%s, %s, %s)"
        values = (data['nome'], data['email'], data.get('telefone', ''))
        
        cursor.execute(query, values)
        connection.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'id': cursor.lastrowid
        }), 201
    except Error as e:
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email já cadastrado'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    """Atualizar um usuário existente"""
    data = request.json
    
    # Validação básica
    if not data.get('nome') or not data.get('email'):
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400
    
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        query = "UPDATE usuarios SET nome = %s, email = %s, telefone = %s WHERE id = %s"
        values = (data['nome'], data['email'], data.get('telefone', ''), id)
        
        cursor.execute(query, values)
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'message': 'Usuário atualizado com sucesso'})
    except Error as e:
        if 'Duplicate entry' in str(e):
            return jsonify({'error': 'Email já cadastrado'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    """Deletar um usuário"""
    connection = get_db_connection()
    if connection is None:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({'message': 'Usuário deletado com sucesso'})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)