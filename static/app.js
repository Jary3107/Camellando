// ================= GLOBAL CONFIGURATION & STATE =================
const API_BASE = '/api';
let currentUser = null;

// On DOM load, check for active session and setup initial views
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    initApp();
});

// ================= UTILITY FUNCTIONS =================

// Show notification toast
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    // Animate in
    toast.classList.remove('hidden');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Convert numbers to COP currency format
function formatCOP(number) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(number);
}

// Toggle between sections/views in SPA
function switchView(viewId) {
    document.querySelectorAll('.view').forEach(view => {
        view.classList.add('hidden');
    });
    const targetView = document.getElementById(viewId);
    if (targetView) {
        targetView.classList.remove('hidden');
    }
}

// ================= SESSION & AUTHENTICATION =================

function checkSession() {
    const storedUser = localStorage.getItem('camellando_user');
    if (storedUser) {
        currentUser = JSON.parse(storedUser);
        updateUserMenu();
        if (currentUser.user_type === 'client') {
            switchView('view-client');
            loadServices();
            loadClientContracts();
        } else {
            switchView('view-worker');
            loadWorkerServices();
            loadWorkerContracts();
        }
    } else {
        currentUser = null;
        updateUserMenu();
        switchView('view-landing');
        document.getElementById('auth-wrapper').classList.add('hidden');
    }
}

function updateUserMenu() {
    const menuContainer = document.getElementById('nav-user-menu');
    if (currentUser) {
        menuContainer.innerHTML = `
            <div class="user-badge" onclick="openProfileModal()" style="cursor: pointer;" title="Editar mi perfil">
                <i class="fa-solid fa-user-circle"></i>
                <span>${currentUser.full_name} (${currentUser.user_type === 'client' ? 'Cliente' : 'Trabajador'})</span>
            </div>
            <button class="btn btn-secondary btn-xs" onclick="handleLogout()">
                <i class="fa-solid fa-right-from-bracket"></i> Salir
            </button>
        `;
    } else {
        menuContainer.innerHTML = `
            <button class="btn btn-secondary btn-xs" onclick="showAuthCard('login')">Ingresar</button>
            <button class="btn btn-primary btn-xs" onclick="showAuthCard('register')">Registrarse</button>
        `;
    }
}


function showAuthCard(type) {
    document.getElementById('auth-wrapper').classList.remove('hidden');
    toggleAuthForms(type);
    
    // Scroll to form smoothly
    document.getElementById('auth-wrapper').scrollIntoView({ behavior: 'smooth' });
}

function toggleAuthForms(type) {
    if (type === 'login') {
        document.getElementById('card-login').classList.remove('hidden');
        document.getElementById('card-register').classList.add('hidden');
    } else {
        document.getElementById('card-login').classList.add('hidden');
        document.getElementById('card-register').classList.remove('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_BASE}/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
            method: 'POST'
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error al iniciar sesión');
        }

        showToast(`¡Bienvenido, ${data.full_name}!`);
        
        const userSession = {
            id: data.user_id,
            user_type: data.user_type,
            full_name: data.full_name,
            email: data.email,
            phone: data.phone
        };


        localStorage.setItem('camellando_user', JSON.stringify(userSession));
        checkSession();
        
        // Reset form
        document.getElementById('form-login').reset();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const phone = document.getElementById('reg-phone').value;
    const password = document.getElementById('reg-password').value;
    const userType = document.querySelector('input[name="reg-type"]:checked').value;

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
                user_type: userType,
                phone
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error en el registro');
        }

        showToast('¡Registro exitoso! Ya puedes iniciar sesión.');
        toggleAuthForms('login');
        document.getElementById('login-email').value = email;
        document.getElementById('form-register').reset();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function handleLogout() {
    localStorage.removeItem('camellando_user');
    showToast('Sesión cerrada correctamente.');
    checkSession();
}

// ================= CLIENT VIEWS & LOGIC =================

async function loadServices() {
    const category = document.getElementById('search-category').value;
    const servicesList = document.getElementById('services-list');
    
    let url = `${API_BASE}/services`;
    if (category) {
        url += `?category=${encodeURIComponent(category)}`;
    }

    try {
        const response = await fetch(url);
        const services = await response.json();

        if (!response.ok) throw new Error('Error al cargar servicios');

        if (services.length === 0) {
            servicesList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-folder-open"></i>
                    <p>No se encontraron servicios disponibles.</p>
                </div>
            `;
            return;
        }

        servicesList.innerHTML = services.map(s => `
            <div class="service-card">
                <div>
                    <div class="service-card-header">
                        <span class="service-title">${s.title}</span>
                        <span class="service-category">${s.category}</span>
                    </div>
                    <p class="service-desc">${s.description}</p>
                </div>
                <div class="service-footer">
                    <div>
                        <span class="service-price">${formatCOP(s.price)}</span>
                        <div class="service-worker-name">
                            <i class="fa-solid fa-toolbox"></i> ${s.worker_name}
                        </div>
                    </div>
                    <button class="btn btn-primary btn-xs" onclick="openContractModal(${s.id}, '${s.title.replace(/'/g, "\\'")}', '${s.worker_name.replace(/'/g, "\\'")}', ${s.price})">
                        Contratar
                    </button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadClientContracts() {
    const contractsList = document.getElementById('client-contracts');
    
    try {
        const response = await fetch(`${API_BASE}/contracts?user_id=${currentUser.id}`);
        const contracts = await response.json();

        if (!response.ok) throw new Error('Error al cargar contratos');

        if (contracts.length === 0) {
            contractsList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-file-invoice"></i>
                    <p>Aún no has realizado ninguna contratación.</p>
                </div>
            `;
            return;
        }

        contractsList.innerHTML = contracts.map(c => `
            <div class="contract-item">
                <div class="contract-header">
                    <span class="contract-svc-title">${c.service_title}</span>
                    <span class="status-badge status-${c.status}">${translateStatus(c.status)}</span>
                </div>
                ${c.details ? `<p class="contract-details"><strong>Nota:</strong> ${c.details}</p>` : ''}
                <div class="contract-info-grid">
                    <div class="contract-info-item">Trabajador: <strong>${c.worker_name}</strong></div>
                    <div class="contract-info-item">Precio: <strong>${formatCOP(c.price)}</strong></div>
                </div>
            </div>
        `).join('');

    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openContractModal(serviceId, title, workerName, defaultPrice) {
    document.getElementById('modal-service-id').value = serviceId;
    document.getElementById('modal-service-title').textContent = `Contratar: ${title}`;
    document.getElementById('modal-service-worker').innerHTML = `<i class="fa-solid fa-user"></i> Ofrecido por: ${workerName}`;
    document.getElementById('contract-price').value = defaultPrice;
    document.getElementById('contract-details').value = '';
    
    document.getElementById('contract-modal').classList.remove('hidden');
}

function closeContractModal() {
    document.getElementById('contract-modal').classList.add('hidden');
}

async function handleCreateContract(e) {
    e.preventDefault();
    const serviceId = parseInt(document.getElementById('modal-service-id').value);
    const price = parseFloat(document.getElementById('contract-price').value);
    const details = document.getElementById('contract-details').value;

    try {
        const response = await fetch(`${API_BASE}/contracts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_id: currentUser.id,
                service_id: serviceId,
                price: price,
                details: details
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al enviar propuesta');
        }

        showToast('Propuesta de contrato enviada con éxito.');
        closeContractModal();
        loadClientContracts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// ================= WORKER VIEWS & LOGIC =================

async function loadWorkerServices() {
    const servicesList = document.getElementById('worker-services');
    
    try {
        const response = await fetch(`${API_BASE}/services`);
        const allServices = await response.json();

        if (!response.ok) throw new Error('Error al cargar tus servicios');

        // Filter only services belonging to current worker
        const myServices = allServices.filter(s => s.worker_id === currentUser.id);

        if (myServices.length === 0) {
            servicesList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <p>Aún no ofreces ningún servicio.</p>
                </div>
            `;
            return;
        }

        servicesList.innerHTML = myServices.map(s => `
            <div class="worker-service-item" style="flex-direction: column; align-items: stretch; gap: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div class="worker-service-info">
                        <span class="worker-service-title" style="font-weight: 700;">${s.title}</span><br>
                        <span class="worker-service-cat" style="font-size: 0.8rem; color: var(--color-text-muted);">${s.category}</span>
                    </div>
                    <span class="worker-service-price" style="font-weight: 700; color: var(--color-primary);">${formatCOP(s.price)}</span>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 8px; border-top: 1px solid var(--color-border); padding-top: 8px; margin-top: 4px;">
                    <button class="btn btn-secondary btn-xs" style="padding: 4px 8px; font-size: 0.75rem;" onclick="openEditServiceModal(${s.id}, '${s.title.replace(/'/g, "\\'")}', '${s.description.replace(/'/g, "\\'")}', '${s.category.replace(/'/g, "\\'")}', ${s.price})">
                        <i class="fa-solid fa-pen"></i> Editar
                    </button>
                    <button class="btn btn-danger btn-xs" style="padding: 4px 8px; font-size: 0.75rem; background-color: var(--color-rejected);" onclick="handleDeleteService(${s.id})">
                        <i class="fa-solid fa-trash"></i> Eliminar
                    </button>
                </div>
            </div>
        `).join('');


    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleCreateService(e) {
    e.preventDefault();
    const title = document.getElementById('svc-title').value;
    const description = document.getElementById('svc-description').value;
    const category = document.getElementById('svc-category').value;
    const price = parseFloat(document.getElementById('svc-price').value);

    try {
        const response = await fetch(`${API_BASE}/services`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                category,
                price,
                worker_id: currentUser.id
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al publicar servicio');
        }

        showToast('Servicio publicado exitosamente.');
        document.getElementById('form-create-service').reset();
        loadWorkerServices();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadWorkerContracts() {
    const contractsList = document.getElementById('worker-contracts');
    
    try {
        const response = await fetch(`${API_BASE}/contracts?user_id=${currentUser.id}`);
        const contracts = await response.json();

        if (!response.ok) throw new Error('Error al cargar contratos');

        if (contracts.length === 0) {
            contractsList.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-inbox"></i>
                    <p>No has recibido ninguna solicitud de trabajo.</p>
                </div>
            `;
            return;
        }

        contractsList.innerHTML = contracts.map(c => `
            <div class="contract-item">
                <div class="contract-header">
                    <span class="contract-svc-title">${c.service_title}</span>
                    <span class="status-badge status-${c.status}">${translateStatus(c.status)}</span>
                </div>
                ${c.details ? `<p class="contract-details"><strong>Instrucciones del Cliente:</strong> ${c.details}</p>` : ''}
                <div class="contract-info-grid">
                    <div class="contract-info-item">Cliente: <strong>${c.client_name}</strong></div>
                    <div class="contract-info-item">Teléfono: <strong>${c.client_phone || 'No registrado'}</strong></div>
                    <div class="contract-info-item">Precio Propuesto: <strong>${formatCOP(c.price)}</strong></div>
                </div>
                ${c.status === 'pending' ? `
                    <div class="contract-actions">
                        <button class="btn btn-secondary btn-xs" onclick="updateContractStatus(${c.id}, 'rejected')">Rechazar</button>
                        <button class="btn btn-primary btn-xs" onclick="updateContractStatus(${c.id}, 'accepted')">Aceptar Trabajo</button>
                    </div>
                ` : ''}
                ${c.status === 'accepted' ? `
                    <div class="contract-actions">
                        <button class="btn btn-accent btn-xs" onclick="updateContractStatus(${c.id}, 'completed')">Marcar como Completado</button>
                    </div>
                ` : ''}
            </div>
        `).join('');

    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function updateContractStatus(contractId, newStatus) {
    try {
        const response = await fetch(`${API_BASE}/contracts/${contractId}?status=${newStatus}`, {
            method: 'PATCH'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al actualizar contrato');
        }

        showToast(`Trabajo ${translateStatus(newStatus).toLowerCase()} exitosamente.`);
        loadWorkerContracts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

// Translate status strings for user presentation
function translateStatus(status) {
    switch(status) {
        case 'pending': return 'Pendiente';
        case 'accepted': return 'Aceptado';
        case 'completed': return 'Completado';
        case 'rejected': return 'Rechazado';
        default: return status;
    }
}

// Initial setups (e.g. key listeners)
function initApp() {
    // Allows pressing enter to filter services
    const categoryInput = document.getElementById('search-category');
    if (categoryInput) {
        categoryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                loadServices();
            }
        });
    }
}

// ================= EDIT PROFILE & SERVICE UI FLOWS =================

function openProfileModal() {
    if (!currentUser) return;
    document.getElementById('edit-profile-name').value = currentUser.full_name || '';
    document.getElementById('edit-profile-email').value = currentUser.email || '';
    document.getElementById('edit-profile-phone').value = currentUser.phone || '';
    document.getElementById('edit-profile-password').value = '';
    
    document.getElementById('profile-modal').classList.remove('hidden');
}

function closeProfileModal() {
    document.getElementById('profile-modal').classList.add('hidden');
}

async function handleEditProfile(e) {
    e.preventDefault();
    const fullName = document.getElementById('edit-profile-name').value;
    const email = document.getElementById('edit-profile-email').value;
    const phone = document.getElementById('edit-profile-phone').value;
    const password = document.getElementById('edit-profile-password').value;

    const payload = {
        full_name: fullName,
        email: email,
        phone: phone
    };
    if (password) {
        payload.password = password;
    }

    try {
        const response = await fetch(`${API_BASE}/users/${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al actualizar perfil');
        }

        showToast('Perfil actualizado correctamente.');
        
        // Update local session
        currentUser.full_name = data.full_name;
        currentUser.email = data.email;
        currentUser.phone = data.phone;
        localStorage.setItem('camellando_user', JSON.stringify(currentUser));
        
        checkSession();
        closeProfileModal();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openEditServiceModal(id, title, description, category, price) {
    document.getElementById('edit-service-id').value = id;
    document.getElementById('edit-svc-title').value = title;
    document.getElementById('edit-svc-description').value = description;
    document.getElementById('edit-svc-category').value = category;
    document.getElementById('edit-svc-price').value = price;
    
    document.getElementById('edit-service-modal').classList.remove('hidden');
}

function closeEditServiceModal() {
    document.getElementById('edit-service-modal').classList.add('hidden');
}

async function handleEditService(e) {
    e.preventDefault();
    const serviceId = document.getElementById('edit-service-id').value;
    const title = document.getElementById('edit-svc-title').value;
    const description = document.getElementById('edit-svc-description').value;
    const category = document.getElementById('edit-svc-category').value;
    const price = parseFloat(document.getElementById('edit-svc-price').value);

    try {
        const response = await fetch(`${API_BASE}/services/${serviceId}?worker_id=${currentUser.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                description,
                category,
                price
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al actualizar servicio');
        }

        showToast('Servicio actualizado correctamente.');
        closeEditServiceModal();
        loadWorkerServices();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function handleDeleteService(serviceId) {
    if (!confirm('¿Estás seguro de que deseas eliminar este servicio?')) return;

    try {
        const response = await fetch(`${API_BASE}/services/${serviceId}?worker_id=${currentUser.id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Error al eliminar el servicio');
        }

        showToast(data.message || 'Servicio eliminado correctamente.');
        loadWorkerServices();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

