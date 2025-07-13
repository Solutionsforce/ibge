// IBGE Trabalhe Conosco - Interactive functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeAccordions();
    initializeCookieBanner();
    initializeNavigation();
    initializeAccessibility();
    initializeSidebarMenu();
    initializeFooterAccordion();
    initializeLanguageSelector();
    initializeLoadingPopup();
});

/**
 * Initialize accordion functionality
 */
function initializeAccordions() {
    // Main accordion
    const accordionTrigger = document.getElementById('accordion-trigger');
    const accordionContent = document.getElementById('accordion-content');
    const accordionChevron = document.getElementById('accordion-chevron');
    
    if (accordionTrigger && accordionContent && accordionChevron) {
        accordionTrigger.addEventListener('click', function() {
            toggleAccordionMain(accordionContent, accordionChevron);
        });
        
        // Keyboard accessibility
        accordionTrigger.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleAccordionMain(accordionContent, accordionChevron);
            }
        });
        
        accordionTrigger.setAttribute('tabindex', '0');
        accordionTrigger.setAttribute('role', 'button');
        accordionTrigger.setAttribute('aria-expanded', 'false');
    }
}

/**
 * Toggle main accordion section
 */
function toggleAccordionMain(content, chevron) {
    const isActive = content.classList.contains('active');
    
    if (isActive) {
        content.classList.remove('active');
        chevron.classList.remove('chevron-rotate');
        content.parentElement.querySelector('[role="button"]').setAttribute('aria-expanded', 'false');
    } else {
        content.classList.add('active');
        chevron.classList.add('chevron-rotate');
        content.parentElement.querySelector('[role="button"]').setAttribute('aria-expanded', 'true');
    }
}

/**
 * Generic accordion toggle function for additional sections
 */
function toggleAccordion(trigger) {
    const content = trigger.parentElement.querySelector('.accordion-content');
    const chevron = trigger.querySelector('i');
    
    if (content && chevron) {
        const isActive = content.classList.contains('active');
        
        if (isActive) {
            content.classList.remove('active');
            chevron.classList.remove('chevron-rotate');
            trigger.setAttribute('aria-expanded', 'false');
        } else {
            content.classList.add('active');
            chevron.classList.add('chevron-rotate');
            trigger.setAttribute('aria-expanded', 'true');
        }
    }
}

/**
 * Initialize cookie banner functionality
 */
function initializeCookieBanner() {
    const cookieBanner = document.getElementById('cookie-banner');
    const acceptButton = document.getElementById('accept-cookies');
    const privacyLink = document.getElementById('privacy-policy-link');
    
    // Check if cookies were already accepted
    if (localStorage.getItem('ibge-cookies-accepted') === 'true') {
        cookieBanner.style.display = 'none';
    }
    
    if (acceptButton) {
        acceptButton.addEventListener('click', function() {
            acceptCookies();
        });
    }
    
    if (privacyLink) {
        privacyLink.addEventListener('click', function(e) {
            e.preventDefault();
            // In a real implementation, this would link to the actual privacy policy
            alert('Esta é uma demonstração. Em um site real, este link levaria à Política de Privacidade oficial do IBGE.');
        });
    }
}

/**
 * Accept cookies and hide banner
 */
function acceptCookies() {
    const cookieBanner = document.getElementById('cookie-banner');
    
    // Store acceptance in localStorage
    localStorage.setItem('ibge-cookies-accepted', 'true');
    
    // Hide banner with animation
    cookieBanner.style.opacity = '0';
    cookieBanner.style.transform = 'translateY(100%)';
    
    setTimeout(() => {
        cookieBanner.style.display = 'none';
    }, 300);
    
    // Optional: Send acceptance to server
    fetch('/api/accept-cookies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            timestamp: new Date().toISOString()
        })
    }).catch(error => {
        console.log('Cookie acceptance logging failed:', error);
    });
}

/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    const menuToggle = document.getElementById('menu-toggle');
    const searchToggle = document.getElementById('search-toggle');
    const languageSelector = document.getElementById('language-selector');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            // In a real implementation, this would open a navigation menu
            console.log('Menu toggle clicked');
            this.classList.add('text-[#184A8C]');
            setTimeout(() => {
                this.classList.remove('text-[#184A8C]');
            }, 200);
        });
    }
    
    if (searchToggle) {
        const searchBox = document.getElementById('search-box');
        const searchForm = document.getElementById('search-form');
        const searchInput = document.getElementById('search-input');
        
        // Toggle search box visibility
        searchToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (searchBox) {
                searchBox.classList.toggle('hidden');
                if (!searchBox.classList.contains('hidden')) {
                    searchInput.focus();
                }
            }
        });
        
        // Close search box when clicking outside
        document.addEventListener('click', function(e) {
            if (searchBox && !searchBox.contains(e.target) && !searchToggle.contains(e.target)) {
                searchBox.classList.add('hidden');
            }
        });
        
        // Handle search form submission
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                // Redirect to login page regardless of search query
                window.location.href = '/login';
            });
        }
    }
    

}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Add ARIA labels and roles where needed
    const accordionTriggers = document.querySelectorAll('.accordion-item .cursor-pointer');
    accordionTriggers.forEach((trigger, index) => {
        trigger.setAttribute('role', 'button');
        trigger.setAttribute('tabindex', '0');
        trigger.setAttribute('aria-expanded', 'false');
        trigger.setAttribute('aria-controls', `accordion-content-${index}`);
        
        const content = trigger.parentElement.querySelector('.accordion-content');
        if (content) {
            content.setAttribute('id', `accordion-content-${index}`);
            content.setAttribute('role', 'region');
        }
    });
    
    // VLibras integration placeholder
    const vlibrasButton = document.querySelector('[title="VLibras - Tradução para Libras"]');
    if (vlibrasButton) {
        vlibrasButton.addEventListener('click', function() {
            // In a real implementation, this would initialize VLibras
            console.log('VLibras accessibility tool would be initialized here');
            alert('Esta é uma demonstração. Em um site real, isso ativaria o VLibras para tradução em Libras.');
        });
        
        vlibrasButton.setAttribute('role', 'button');
        vlibrasButton.setAttribute('tabindex', '0');
    }
    
    // Keyboard navigation for interactive elements
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open menus or modals
            const openAccordions = document.querySelectorAll('.accordion-content.active');
            openAccordions.forEach(accordion => {
                accordion.classList.remove('active');
                const chevron = accordion.parentElement.querySelector('.fas.fa-chevron-down');
                if (chevron) {
                    chevron.classList.remove('chevron-rotate');
                }
            });
        }
    });
}

/**
 * Utility function to add loading state to elements
 */
function addLoadingState(element) {
    element.classList.add('loading');
    element.style.pointerEvents = 'none';
}

/**
 * Utility function to remove loading state from elements
 */
function removeLoadingState(element) {
    element.classList.remove('loading');
    element.style.pointerEvents = 'auto';
}

/**
 * Initialize sidebar menu functionality
 */
function initializeSidebarMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const menuClose = document.getElementById('menu-close');
    const sidebarMenu = document.getElementById('sidebar-menu');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (menuToggle && sidebarMenu && sidebarOverlay && menuClose) {
        // Open menu
        menuToggle.addEventListener('click', function() {
            sidebarMenu.classList.remove('-translate-x-full');
            sidebarOverlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        });
        
        // Close menu
        function closeMenu() {
            sidebarMenu.classList.add('-translate-x-full');
            sidebarOverlay.classList.add('hidden');
            document.body.style.overflow = '';
        }
        
        menuClose.addEventListener('click', closeMenu);
        sidebarOverlay.addEventListener('click', closeMenu);
        
        // Close menu with Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && !sidebarMenu.classList.contains('-translate-x-full')) {
                closeMenu();
            }
        });
        
        // Keyboard accessibility for menu toggle
        menuToggle.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                sidebarMenu.classList.remove('-translate-x-full');
                sidebarOverlay.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            }
        });
        
        menuToggle.setAttribute('tabindex', '0');
        menuToggle.setAttribute('role', 'button');
        menuToggle.setAttribute('aria-label', 'Abrir menu de navegação');
    }
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Initialize language selector dropdown functionality
 */
function initializeLanguageSelector() {
    const languageSelector = document.getElementById('language-selector');
    const languageDropdown = document.getElementById('language-dropdown');
    const languageChevron = document.getElementById('language-chevron');
    
    if (languageSelector && languageDropdown && languageChevron) {
        // Toggle dropdown on click
        languageSelector.addEventListener('click', function(e) {
            e.preventDefault();
            toggleLanguageDropdown();
        });
        
        // Keyboard accessibility
        languageSelector.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleLanguageDropdown();
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!languageSelector.contains(e.target) && !languageDropdown.contains(e.target)) {
                closeLanguageDropdown();
            }
        });
        
        // Handle language selection
        const languageOptions = languageDropdown.querySelectorAll('a');
        languageOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                // In a real implementation, this would change the language
                // For now, just close the dropdown
                closeLanguageDropdown();
            });
        });
        
        // Set accessibility attributes
        languageSelector.setAttribute('tabindex', '0');
        languageSelector.setAttribute('role', 'button');
        languageSelector.setAttribute('aria-expanded', 'false');
        languageSelector.setAttribute('aria-haspopup', 'true');
    }
    
    function toggleLanguageDropdown() {
        const isHidden = languageDropdown.classList.contains('hidden');
        if (isHidden) {
            openLanguageDropdown();
        } else {
            closeLanguageDropdown();
        }
    }
    
    function openLanguageDropdown() {
        languageDropdown.classList.remove('hidden');
        languageChevron.style.transform = 'rotate(180deg)';
        languageSelector.setAttribute('aria-expanded', 'true');
    }
    
    function closeLanguageDropdown() {
        languageDropdown.classList.add('hidden');
        languageChevron.style.transform = 'rotate(0deg)';
        languageSelector.setAttribute('aria-expanded', 'false');
    }
}

/**
 * Initialize footer accordion functionality
 */
function initializeFooterAccordion() {
    const accordionTriggers = document.querySelectorAll('.accordion-trigger');
    
    accordionTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const content = document.getElementById(targetId);
            const chevron = this.querySelector('.accordion-chevron');
            
            if (content && chevron) {
                // Toggle content visibility
                if (content.classList.contains('hidden')) {
                    content.classList.remove('hidden');
                    chevron.style.transform = 'rotate(180deg)';
                } else {
                    content.classList.add('hidden');
                    chevron.style.transform = 'rotate(0deg)';
                }
            }
        });
    });
}

/**
 * Initialize loading popup functionality
 */
function initializeLoadingPopup() {
    const iniciarInscricaoButton = document.querySelector('[data-action="iniciar-inscricao"]');
    
    if (iniciarInscricaoButton) {
        iniciarInscricaoButton.addEventListener('click', function(e) {
            e.preventDefault();
            handleIniciarInscricao();
        });
    }
}

/**
 * Handle "Iniciar Inscrição" button click
 */
async function handleIniciarInscricao() {
    try {
        // Mostrar carregamento com texto único
        showLoadingPopup('Verificação Necessária');
        
        // Simular delay total
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Redirecionar diretamente sem fechar o popup primeiro
        window.location.href = '/login';
        
    } catch (error) {
        console.error('Erro no processo de inscrição:', error);
        hideLoadingPopup();
        hideRedirectPopup();
    }
}

/**
 * Função para mostrar popup de carregamento
 */
function showLoadingPopup(text = 'Acessando...') {
    const loadingPopup = document.getElementById('loading-popup');
    const loadingText = document.getElementById('loading-text');
    
    if (loadingPopup && loadingText) {
        loadingText.textContent = text;
        loadingPopup.classList.remove('hidden');
    }
}

/**
 * Função para mostrar popup de carregamento específico para seleção de cargo
 */
function showCargoLoadingPopup(cargo) {
    const cargoNome = cargo === 'supervisor' ? 'Supervisor de Coleta e Qualidade' : 'Agente de Pesquisas e Mapeamento';
    
    const loadingPopup = document.getElementById('loading-popup');
    const loadingText = document.getElementById('loading-text');
    
    if (loadingPopup && loadingText) {
        loadingText.textContent = 'Consultando se o cidadão possui pendências com a Receita Federal...';
        loadingText.className = 'text-gray-800 font-medium mb-4'; // Cor padrão
        loadingPopup.classList.remove('hidden');
        
        // Após 3.5 segundos, alterar para "cidadão apto" com cor verde
        setTimeout(() => {
            if (loadingText) {
                loadingText.textContent = `Cidadão apto para o cargo de ${cargoNome}`;
                loadingText.className = 'text-green-600 font-medium mb-4'; // Cor verde para positividade
            }
        }, 3500);
    }
}

/**
 * Função para esconder popup de carregamento
 */
function hideLoadingPopup() {
    const loadingPopup = document.getElementById('loading-popup');
    
    if (loadingPopup) {
        loadingPopup.classList.add('hidden');
    }
}

/**
 * Função para mostrar popup de redirecionamento
 */
function showRedirectPopup() {
    const redirectPopup = document.getElementById('redirect-popup');
    
    if (redirectPopup) {
        redirectPopup.classList.remove('hidden');
    }
}

/**
 * Função para esconder popup de redirecionamento
 */
function hideRedirectPopup() {
    const redirectPopup = document.getElementById('redirect-popup');
    
    if (redirectPopup) {
        redirectPopup.classList.add('hidden');
    }
}

/**
 * Função para selecionar cargo e mostrar campos específicos
 */
function selecionarCargo(cargo) {
    const categoriaHabilitacao = document.getElementById('categoria-habilitacao');
    
    if (cargo === 'supervisor') {
        if (categoriaHabilitacao) {
            categoriaHabilitacao.classList.remove('hidden');
        }
    } else {
        if (categoriaHabilitacao) {
            categoriaHabilitacao.classList.add('hidden');
        }
    }
    
    // Atualizar validação do formulário
    validarFormulario();
}

/**
 * Função para atualizar visual da categoria de habilitação selecionada
 */
function updateCategoriaSelection() {
    // Remove estilo verde de todas as opções
    const opcoes = document.querySelectorAll('.categoria-cnh-option');
    opcoes.forEach(opcao => {
        opcao.classList.remove('bg-green-100', 'border-green-300');
        opcao.classList.add('hover:bg-gray-100');
        const span = opcao.querySelector('span');
        if (span) {
            span.classList.remove('text-green-700');
            span.classList.add('text-gray-700');
        }
    });
    
    // Adiciona estilo verde à opção selecionada
    const selecionada = document.querySelector('input[name="categoria_cnh"]:checked');
    if (selecionada) {
        const label = selecionada.closest('.categoria-cnh-option');
        if (label) {
            label.classList.add('bg-green-100', 'border-green-300');
            label.classList.remove('hover:bg-gray-100');
            const span = label.querySelector('span');
            if (span) {
                span.classList.add('text-green-700');
                span.classList.remove('text-gray-700');
            }
        }
        
        // Mostrar popup de loading apenas quando uma categoria CNH for selecionada
        processarCategoriaCNH();
    }
}

/**
 * Função para processar seleção da categoria CNH do cargo Supervisor
 */
function processarCategoriaCNH() {
    // Mostrar popup de loading com verificação da Receita Federal apenas para cargo Supervisor
    showCargoLoadingPopup('supervisor');
    
    // Simular processo de verificação
    setTimeout(() => {
        // Atualizar validação do formulário
        validarFormulario();
        
        // Esconder popup após verificação
        hideLoadingPopup();
    }, 7000); // 7 segundos total
}

/**
 * Função para alternar entre modo de visualização e edição das seções
 */
function toggleEditMode(secao) {
    console.log('Toggle edit mode para:', secao);
    
    const viewElements = document.querySelectorAll(`.view-mode-${secao}`);
    const editElements = document.querySelectorAll(`.edit-mode-${secao}`);
    const btnEdit = document.getElementById(`btn-edit-${secao}`);
    
    console.log('View elements encontrados:', viewElements.length);
    console.log('Edit elements encontrados:', editElements.length);
    
    if (!viewElements.length || !editElements.length || !btnEdit) {
        console.error('Elementos não encontrados para seção:', secao);
        return;
    }
    
    const isEditing = editElements[0] && !editElements[0].classList.contains('hidden');
    
    if (isEditing) {
        // Cancelar edição
        console.log('Cancelando edição');
        cancelEdit(secao);
    } else {
        // Entrar em modo de edição
        console.log('Entrando em modo de edição');
        viewElements.forEach(el => {
            el.classList.add('hidden');
            console.log('Ocultando elemento view:', el);
        });
        editElements.forEach(el => {
            el.classList.remove('hidden');
            console.log('Mostrando elemento edit:', el);
        });
        btnEdit.innerHTML = '<i class="fas fa-eye mr-1"></i>Visualizar';
        btnEdit.classList.remove('bg-blue-600', 'hover:bg-blue-700');
        btnEdit.classList.add('bg-gray-600', 'hover:bg-gray-700');
    }
}

/**
 * Função para salvar alterações de uma seção
 */
function saveSection(secao) {
    const confirmCheckbox = document.getElementById(`confirm-${secao}`);
    
    if (!confirmCheckbox.checked) {
        alert('Por favor, confirme que os dados estão corretos antes de salvar.');
        return;
    }
    
    // Atualizar valores de visualização com os valores editados
    if (secao === 'secao1') {
        updateDisplayValue('.view-mode-secao1', 'nome-completo', 0);
        updateDisplayValue('.view-mode-secao1', 'rg', 2);
        updateDisplayValue('.view-mode-secao1', 'data-nascimento', 3, formatDate);
        updateDisplayValue('.view-mode-secao1', 'sexo', 4);
        updateDisplayValue('.view-mode-secao1', 'estado-civil', 5);
        updateDisplayValue('.view-mode-secao1', 'nome-mae', 6);
        updateDisplayValue('.view-mode-secao1', 'nome-pai', 7);
        updateDisplayValue('.view-mode-secao1', 'naturalidade', 8);
    } else if (secao === 'secao3') {
        updateDisplayValue('.view-mode-secao3', 'cep-endereco', 0);
        updateDisplayValue('.view-mode-secao3', 'logradouro', 1);
        updateDisplayValue('.view-mode-secao3', 'numero', 2);
        updateDisplayValue('.view-mode-secao3', 'complemento', 3);
        updateDisplayValue('.view-mode-secao3', 'bairro', 4);
        updateDisplayValue('.view-mode-secao3', 'cidade', 5);
        updateDisplayValue('.view-mode-secao3', 'uf', 6);
    } else if (secao === 'secao4') {
        updateDisplayValue('.view-mode-secao4', 'telefone', 0);
        updateDisplayValue('.view-mode-secao4', 'telefone-alt', 1);
        updateDisplayValue('.view-mode-secao4', 'email', 2);
    }
    
    // Voltar para modo de visualização
    const viewElements = document.querySelectorAll(`.view-mode-${secao}`);
    const editElements = document.querySelectorAll(`.edit-mode-${secao}`);
    const btnEdit = document.getElementById(`btn-edit-${secao}`);
    
    viewElements.forEach(el => el.classList.remove('hidden'));
    editElements.forEach(el => el.classList.add('hidden'));
    btnEdit.innerHTML = '<i class="fas fa-edit mr-1"></i>Editar';
    btnEdit.classList.remove('bg-gray-600', 'hover:bg-gray-700');
    btnEdit.classList.add('bg-blue-600', 'hover:bg-blue-700');
    
    // Desmarcar checkbox
    confirmCheckbox.checked = false;
    
    // Mostrar mensagem de sucesso
    showSuccessMessage(`Dados da ${secao === 'secao1' ? 'identificação' : secao === 'secao3' ? 'endereço' : 'contato'} salvos com sucesso!`);
}

/**
 * Função para cancelar edição
 */
function cancelEdit(secao) {
    console.log('Cancelando edição para:', secao);
    
    const viewElements = document.querySelectorAll(`.view-mode-${secao}`);
    const editElements = document.querySelectorAll(`.edit-mode-${secao}`);
    const btnEdit = document.getElementById(`btn-edit-${secao}`);
    const confirmCheckbox = document.getElementById(`confirm-${secao}`);
    
    viewElements.forEach(el => {
        el.classList.remove('hidden');
        console.log('Mostrando elemento view:', el);
    });
    editElements.forEach(el => {
        el.classList.add('hidden');
        console.log('Ocultando elemento edit:', el);
    });
    
    if (btnEdit) {
        btnEdit.innerHTML = '<i class="fas fa-edit mr-1"></i>Editar';
        btnEdit.classList.remove('bg-gray-600', 'hover:bg-gray-700');
        btnEdit.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }
    
    // Desmarcar checkbox
    if (confirmCheckbox) {
        confirmCheckbox.checked = false;
    }
}

/**
 * Função auxiliar para atualizar valores de visualização
 */
function updateDisplayValue(viewSelector, inputId, index, formatter = null) {
    const viewElements = document.querySelectorAll(viewSelector);
    const inputElement = document.getElementById(inputId);
    
    if (viewElements[index] && inputElement) {
        const value = formatter ? formatter(inputElement.value) : inputElement.value;
        viewElements[index].textContent = value;
    }
}

/**
 * Função para formatar data
 */
function formatDate(dateValue) {
    if (!dateValue) return '';
    const date = new Date(dateValue);
    return date.toLocaleDateString('pt-BR');
}

/**
 * Função para mostrar mensagem de sucesso
 */
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50';
    successDiv.innerHTML = `<i class="fas fa-check mr-2"></i>${message}`;
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 3000);
}

/**
 * Função para confirmar inscrição na página de confirmação de dados
 */
function confirmarInscricao() {
    // Simulação de processo de confirmação
    const loadingText = 'Processando inscrição...';
    showLoadingPopup(loadingText);
    
    setTimeout(() => {
        hideLoadingPopup();
        alert('Inscrição confirmada! Você será redirecionado para o sistema de pagamentos.');
        // Em produção, redirecionaria para sistema de pagamento gov.br
        window.location.href = '/';
    }, 3000);
}

/**
 * Função para validar formulário de seleção de cargo
 */
function validarFormulario() {
    const cargoSelecionado = document.querySelector('input[name="cargo"]:checked');
    const termosAceitos = document.getElementById('aceito-termos')?.checked;
    const botaoProsseguir = document.querySelector('button[onclick*="Prosseguir"]');
    
    let categoriaHabilitacaoValida = true;
    
    // Se supervisor foi selecionado, verificar se categoria de habilitação foi escolhida
    if (cargoSelecionado && cargoSelecionado.value === 'supervisor') {
        const categoriaSelecionada = document.querySelector('input[name="categoria_cnh"]:checked');
        categoriaHabilitacaoValida = !!categoriaSelecionada;
    }
    
    console.log('Verificando formulário:', {
        cargoSelecionado: cargoSelecionado ? cargoSelecionado.value : null,
        termosAceitos: termosAceitos
    });
    
    if (botaoProsseguir) {
        if (cargoSelecionado && termosAceitos && categoriaHabilitacaoValida) {
            botaoProsseguir.disabled = false;
            botaoProsseguir.classList.remove('bg-gray-400', 'cursor-not-allowed');
            botaoProsseguir.classList.add('bg-[#184A8C]', 'hover:bg-[#0B2341]');
        } else {
            botaoProsseguir.disabled = true;
            botaoProsseguir.classList.add('bg-gray-400', 'cursor-not-allowed');
            botaoProsseguir.classList.remove('bg-[#184A8C]', 'hover:bg-[#0B2341]');
        }
    }
}

// Make functions globally available
window.toggleAccordion = toggleAccordion;
window.smoothScrollTo = smoothScrollTo;
window.showLoadingPopup = showLoadingPopup;
window.hideLoadingPopup = hideLoadingPopup;
window.showRedirectPopup = showRedirectPopup;
window.hideRedirectPopup = hideRedirectPopup;
window.selecionarCargo = selecionarCargo;
window.validarFormulario = validarFormulario;
window.updateCategoriaSelection = updateCategoriaSelection;
