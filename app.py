from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os

# Carregar .env apenas em desenvolvimento local
if os.path.exists('.env') and os.getenv('RENDER') != 'true':
    from dotenv import load_dotenv
    load_dotenv()
    print("🔧 Carregando .env local (desenvolvimento)")
else:
    print("🚀 Rodando em produção (Render) - usando variáveis de ambiente")

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Estabelece conexão com o banco de dados MySQL"""
    try:
        # Pegar variáveis do ambiente (Render) ou do .env (local)
        db_host = os.getenv('DB_HOST', 'localhost')
        db_user = os.getenv('DB_USER', 'root')
        db_password = os.getenv('DB_PASSWORD', '')
        db_name = os.getenv('DB_NAME', 'crud_sistema')
        db_port = int(os.getenv('DB_PORT', 3306))
        
        # Debug para ver qual banco está usando
        print(f"🔍 Conectando ao banco: {db_host}:{db_port}/{db_name} com usuário {db_user}")
        
        # Verificar se está em produção (Render) para forçar SSL
        is_production = os.getenv('RENDER') == 'true'
        
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            ssl_disabled=not is_production,  # SSL apenas em produção
            ssl_ca=None if is_production else None
        )
        
        print("✅ Conexão com banco estabelecida com sucesso!")
        return connection
        
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        print(f"   Host: {db_host}, User: {db_user}, Database: {db_name}")
        return None

def init_db():
    """Cria a tabela usuarios se não existir"""
    print("🔄 Inicializando banco de dados...")
    connection = get_db_connection()
    
    if connection is None:
        print("⚠️ Não foi possível inicializar o banco de dados - conexão falhou")
        return
    
    try:
        cursor = connection.cursor()
        
        # Criar tabela usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                telefone VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
        print("✅ Tabela 'usuarios' criada/verificada com sucesso!")
        
        # Verificar se tem dados
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"📊 Total de registros na tabela: {count}")
        
    except Error as e:
        print(f"❌ Erro ao criar/verificar tabela: {e}")
    finally:
        connection.close()

# Inicializar banco de dados
init_db()

@app.route('/')
def index():
    """Rota principal - renderiza a página HTML"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"❌ Erro ao renderizar index: {e}")
        return "Erro ao carregar página", 500

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
        print(f"📋 Listados {len(usuarios)} usuários")
        return jsonify(usuarios)
    except Error as e:
        print(f"❌ Erro ao listar usuários: {e}")
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
        print(f"❌ Erro ao buscar usuário {id}: {e}")
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
        
        print(f"✅ Usuário criado: {data['nome']} - ID: {cursor.lastrowid}")
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'id': cursor.lastrowid
        }), 201
    except Error as e:
        if 'Duplicate entry' in str(e):
            print(f"⚠️ Tentativa de email duplicado: {data['email']}")
            return jsonify({'error': 'Email já cadastrado'}), 400
        print(f"❌ Erro ao criar usuário: {e}")
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
        
        print(f"✅ Usuário {id} atualizado com sucesso")
        return jsonify({'message': 'Usuário atualizado com sucesso'})
    except Error as e:
        if 'Duplicate entry' in str(e):
            print(f"⚠️ Email duplicado na atualização: {data['email']}")
            return jsonify({'error': 'Email já cadastrado'}), 400
        print(f"❌ Erro ao atualizar usuário {id}: {e}")
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
        
        print(f"✅ Usuário {id} deletado com sucesso")
        return jsonify({'message': 'Usuário deletado com sucesso'})
    except Error as e:
        print(f"❌ Erro ao deletar usuário {id}: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    # Para desenvolvimento local
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)