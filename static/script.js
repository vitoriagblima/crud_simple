// URL da API
const API_URL = '/api/usuarios';

// Variáveis globais
let deleteId = null;

// Carregar usuários ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    
    // Configurar eventos
    document.getElementById('open-add-modal').addEventListener('click', () => openModal());
    document.getElementById('close-modal-btn').addEventListener('click', closeModal);
    document.getElementById('confirm-delete').addEventListener('click', confirmDelete);
    document.getElementById('cancel-delete').addEventListener('click', closeConfirmModal);
    document.getElementById('search-input').addEventListener('input', searchUsers);
    
    // Fechar modal ao clicar no X
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });
    
    // Configurar validação do telefone
    const telefoneInput = document.getElementById('telefone');
    telefoneInput.addEventListener('input', formatTelefone);
    telefoneInput.addEventListener('keypress', onlyNumbers);
    
    // Configurar submit do formulário
    document.getElementById('user-form').addEventListener('submit', handleSubmit);
    
    // Fechar modal ao clicar fora
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('user-modal');
        if (e.target === modal) {
            closeModal();
        }
        const confirmModal = document.getElementById('confirm-modal');
        if (e.target === confirmModal) {
            closeConfirmModal();
        }
    });
});

// Função para permitir apenas números
function onlyNumbers(event) {
    const key = event.key;
    // Permitir apenas números, backspace, delete, tab, enter, etc
    if (!/^[0-9]$/.test(key) && 
        key !== 'Backspace' && 
        key !== 'Delete' && 
        key !== 'Tab' && 
        key !== 'Enter' &&
        key !== 'ArrowLeft' &&
        key !== 'ArrowRight') {
        event.preventDefault();
    }
}

// Função para formatar telefone
function formatTelefone(event) {
    let value = event.target.value.replace(/\D/g, ''); // Remove tudo que não é número
    
    if (value.length > 11) {
        value = value.slice(0, 11);
    }
    
    // Formatação: (XX) XXXXX-XXXX
    if (value.length >= 2 && value.length <= 6) {
        value = value.replace(/^(\d{2})(\d)/, '($1) $2');
    } else if (value.length >= 7 && value.length <= 10) {
        value = value.replace(/^(\d{2})(\d{4})(\d)/, '($1) $2-$3');
    } else if (value.length >= 11) {
        value = value.replace(/^(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
    }
    
    event.target.value = value;
}

// Função para abrir modal
function openModal(user = null) {
    const modal = document.getElementById('user-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('user-form');
    
    if (user) {
        // Modo edição
        modalTitle.textContent = 'Editar Usuário';
        document.getElementById('user-id').value = user.id;
        document.getElementById('nome').value = user.nome;
        document.getElementById('email').value = user.email;
        document.getElementById('telefone').value = user.telefone || '';
    } else {
        // Modo criação
        modalTitle.textContent = 'Novo Usuário';
        form.reset();
        document.getElementById('user-id').value = '';
    }
    
    // Limpar mensagens de erro
    clearErrors();
    
    modal.style.display = 'flex';
}

// Função para fechar modal
function closeModal() {
    const modal = document.getElementById('user-modal');
    modal.style.display = 'none';
    document.getElementById('user-form').reset();
    clearErrors();
}

// Função para fechar modal de confirmação
function closeConfirmModal() {
    const modal = document.getElementById('confirm-modal');
    modal.style.display = 'none';
    deleteId = null;
}

// Função para limpar erros
function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
    document.querySelectorAll('.form-group input').forEach(el => el.classList.remove('error'));
}

// Função para mostrar erros
function showError(inputId, message) {
    const input = document.getElementById(inputId);
    const errorElement = document.getElementById(`${inputId}-error`);
    
    input.classList.add('error');
    errorElement.textContent = message;
}

// Função para validar formulário
function validateForm(nome, email, telefone) {
    let isValid = true;
    
    // Validar nome
    if (!nome || nome.trim() === '') {
        showError('nome', 'Nome é obrigatório');
        isValid = false;
    } else if (nome.length < 3) {
        showError('nome', 'Nome deve ter pelo menos 3 caracteres');
        isValid = false;
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!email || email.trim() === '') {
        showError('email', 'Email é obrigatório');
        isValid = false;
    } else if (!emailRegex.test(email)) {
        showError('email', 'Email inválido');
        isValid = false;
    }
    
    // Validar telefone (se preenchido)
    if (telefone && telefone.trim() !== '') {
        const telefoneLimpo = telefone.replace(/\D/g, '');
        if (telefoneLimpo.length < 10 || telefoneLimpo.length > 11) {
            showError('telefone', 'Telefone deve ter 10 ou 11 dígitos');
            isValid = false;
        }
    }
    
    return isValid;
}

// Função para lidar com o envio do formulário
async function handleSubmit(event) {
    event.preventDefault();
    
    const id = document.getElementById('user-id').value;
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const telefone = document.getElementById('telefone').value;
    
    // Validar formulário
    if (!validateForm(nome, email, telefone)) {
        return;
    }
    
    const userData = { 
        nome: nome.trim(), 
        email: email.trim(), 
        telefone: telefone.trim() 
    };
    
    try {
        let response;
        
        if (id) {
            // Atualizar usuário existente
            response = await fetch(`${API_URL}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
        } else {
            // Criar novo usuário
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(userData)
            });
        }
        
        if (response.ok) {
            closeModal();
            loadUsers();
            showNotification(id ? 'Usuário atualizado com sucesso!' : 'Usuário criado com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Erro ao salvar usuário', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
    }
}

// Função para carregar todos os usuários
async function loadUsers() {
    try {
        const response = await fetch(API_URL);
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        showNotification('Erro ao carregar usuários', 'error');
    }
}

// Função para exibir usuários
function displayUsers(users) {
    const usersList = document.getElementById('users-list');
    
    if (users.length === 0) {
        usersList.innerHTML = '<div class="loading">Nenhum usuário encontrado</div>';
        return;
    }
    
    usersList.innerHTML = users.map(user => `
        <div class="user-card">
            <div class="user-info">
                <h3><i class="fas fa-user"></i> ${escapeHtml(user.nome)}</h3>
                <p><i class="fas fa-envelope"></i> ${escapeHtml(user.email)}</p>
                ${user.telefone ? `<p><i class="fas fa-phone"></i> ${escapeHtml(user.telefone)}</p>` : ''}
                <p><i class="fas fa-calendar"></i> ${formatDate(user.data_cadastro)}</p>
            </div>
            <div class="user-actions">
                <button class="btn btn-edit" onclick="editUser(${user.id})">
                    <i class="fas fa-edit"></i> Editar
                </button>
                <button class="btn btn-delete" onclick="showDeleteModal(${user.id})">
                    <i class="fas fa-trash"></i> Excluir
                </button>
            </div>
        </div>
    `).join('');
}

// Função para buscar usuários
async function searchUsers() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    
    if (searchTerm === '') {
        loadUsers();
        return;
    }
    
    try {
        const response = await fetch(API_URL);
        const users = await response.json();
        
        const filteredUsers = users.filter(user => 
            user.nome.toLowerCase().includes(searchTerm) || 
            user.email.toLowerCase().includes(searchTerm)
        );
        
        displayUsers(filteredUsers);
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
    }
}

// Função para editar usuário
async function editUser(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        const user = await response.json();
        openModal(user);
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
        showNotification('Erro ao carregar dados do usuário', 'error');
    }
}

// Função para mostrar modal de exclusão
function showDeleteModal(id) {
    deleteId = id;
    const modal = document.getElementById('confirm-modal');
    modal.style.display = 'flex';
}

// Função para confirmar exclusão
async function confirmDelete() {
    if (!deleteId) return;
    
    try {
        const response = await fetch(`${API_URL}/${deleteId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            closeConfirmModal();
            loadUsers();
            showNotification('Usuário excluído com sucesso!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Erro ao excluir usuário', 'error');
        }
    } catch (error) {
        console.error('Erro:', error);
        showNotification('Erro ao conectar com o servidor', 'error');
    }
}

// Função para mostrar notificação
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Função para formatar data
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Função para escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}