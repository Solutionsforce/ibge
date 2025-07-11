// Função para buscar endereço pelo CEP
async function buscarEnderecoPorCEP(cep) {
    try {
        const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await response.json();
        
        if (data.erro) {
            console.error('CEP não encontrado');
            return null;
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao buscar CEP:', error);
        return null;
    }
}

// Função para preencher campos de endereço automaticamente
function preencherEndereco(endereco) {
    const logradouro = document.getElementById('logradouro');
    const bairro = document.getElementById('bairro');
    const cidade = document.getElementById('cidade');
    const uf = document.getElementById('uf');
    
    if (logradouro) logradouro.value = endereco.logradouro || '';
    if (bairro) bairro.value = endereco.bairro || '';
    if (cidade) cidade.value = endereco.localidade || '';
    if (uf) uf.value = endereco.uf || '';
}

// Função para formatar CEP
function formatarCEP(cep) {
    cep = cep.replace(/\D/g, '');
    cep = cep.replace(/^(\d{5})(\d{3})$/, '$1-$2');
    return cep;
}

// Função para formatar CPF
function formatarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    return cpf;
}

// Função para formatar telefone
function formatarTelefone(telefone) {
    telefone = telefone.replace(/\D/g, '');
    if (telefone.length === 11) {
        telefone = telefone.replace(/(\d{2})(\d{1})(\d{4})(\d{4})/, '($1) $2 $3-$4');
    } else if (telefone.length === 10) {
        telefone = telefone.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return telefone;
}

// Função para obter data e hora de Brasília
function obterDataHoraBrasilia() {
    try {
        const agora = new Date();
        const opcoes = {
            timeZone: 'America/Sao_Paulo',
            day: '2-digit',
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        };
        
        const formatoBrasilia = new Intl.DateTimeFormat('pt-BR', opcoes);
        const partesData = formatoBrasilia.formatToParts(agora);
        
        const dia = partesData.find(p => p.type === 'day').value;
        const mes = partesData.find(p => p.type === 'month').value;
        const ano = partesData.find(p => p.type === 'year').value;
        const hora = partesData.find(p => p.type === 'hour').value;
        const minuto = partesData.find(p => p.type === 'minute').value;
        
        return `${dia}/${mes}/${ano} às ${hora}:${minuto}`;
    } catch (error) {
        return new Date().toLocaleDateString('pt-BR') + ' às ' + 
               new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }
}

// Função para salvar dados automaticamente
function salvarDados() {
    const dadosUsuario = {
        nome_completo: document.getElementById('nome-completo')?.value || '',
        cpf: document.getElementById('cpf')?.value || '',
        data_nascimento: document.getElementById('data-nascimento')?.value || '',
        nome_mae: document.getElementById('nome-mae')?.value || '',
        sexo: document.getElementById('sexo')?.value || '',
        cep: document.getElementById('cep-endereco')?.value || '',
        logradouro: document.getElementById('logradouro')?.value || '',
        bairro: document.getElementById('bairro')?.value || '',
        cidade: document.getElementById('cidade')?.value || '',
        uf: document.getElementById('uf')?.value || '',
        telefone: document.getElementById('telefone')?.value || '',
        telefone_alt: document.getElementById('telefone-alt')?.value || '',
        email: document.getElementById('email')?.value || ''
    };
    
    // Salvar dados completos
    localStorage.setItem('ibge_dados_usuario', JSON.stringify(dadosUsuario));
    
    // Salvar seções individuais
    localStorage.setItem('ibge_inscricao_secao1', JSON.stringify({
        nome_completo: dadosUsuario.nome_completo,
        cpf: dadosUsuario.cpf,
        data_nascimento: dadosUsuario.data_nascimento,
        nome_mae: dadosUsuario.nome_mae,
        sexo: dadosUsuario.sexo
    }));
    
    localStorage.setItem('ibge_inscricao_secao3', JSON.stringify({
        cep: dadosUsuario.cep,
        logradouro: dadosUsuario.logradouro,
        bairro: dadosUsuario.bairro,
        cidade: dadosUsuario.cidade,
        uf: dadosUsuario.uf
    }));
    
    localStorage.setItem('ibge_inscricao_secao4', JSON.stringify({
        telefone: dadosUsuario.telefone,
        telefone_alt: dadosUsuario.telefone_alt,
        email: dadosUsuario.email
    }));
}

// Função para carregar dados salvos
function carregarDadosSalvos() {
    try {
        const dadosSecao1 = JSON.parse(localStorage.getItem('ibge_inscricao_secao1') || '{}');
        const dadosSecao3 = JSON.parse(localStorage.getItem('ibge_inscricao_secao3') || '{}');
        const dadosSecao4 = JSON.parse(localStorage.getItem('ibge_inscricao_secao4') || '{}');
        
        // Preencher campos Seção I
        if (dadosSecao1.nome_completo) document.getElementById('nome-completo').value = dadosSecao1.nome_completo;
        if (dadosSecao1.cpf) document.getElementById('cpf').value = dadosSecao1.cpf;
        if (dadosSecao1.data_nascimento) document.getElementById('data-nascimento').value = dadosSecao1.data_nascimento;
        if (dadosSecao1.nome_mae) document.getElementById('nome-mae').value = dadosSecao1.nome_mae;
        if (dadosSecao1.sexo) document.getElementById('sexo').value = dadosSecao1.sexo;
        
        // Preencher campos Seção III
        if (dadosSecao3.cep) document.getElementById('cep-endereco').value = dadosSecao3.cep;
        if (dadosSecao3.logradouro) document.getElementById('logradouro').value = dadosSecao3.logradouro;
        if (dadosSecao3.bairro) document.getElementById('bairro').value = dadosSecao3.bairro;
        if (dadosSecao3.cidade) document.getElementById('cidade').value = dadosSecao3.cidade;
        if (dadosSecao3.uf) document.getElementById('uf').value = dadosSecao3.uf;
        
        // Preencher campos Seção IV
        if (dadosSecao4.telefone) document.getElementById('telefone').value = dadosSecao4.telefone;
        if (dadosSecao4.telefone_alt) document.getElementById('telefone-alt').value = dadosSecao4.telefone_alt;
        if (dadosSecao4.email) document.getElementById('email').value = dadosSecao4.email;
        
        console.log('Dados salvos carregados do localStorage');
    } catch (error) {
        console.error('Erro ao carregar dados salvos:', error);
    }
}

// Função para confirmar dados e prosseguir
function confirmarDadosProsseguir() {
    // Salvar dados antes de prosseguir
    salvarDados();
    
    // Redirecionar para próxima página
    window.location.href = '/selecao-local-prova';
}

// Função para voltar
function voltarSelecao() {
    window.history.back();
}

// Função para atualizar data e hora
function atualizarDataHoraBrasilia() {
    try {
        const dataFormatada = obterDataHoraBrasilia();
        const elementoDataHora = document.getElementById('data-hora-inscricao');
        if (elementoDataHora) {
            elementoDataHora.textContent = dataFormatada;
        }
        console.log('Data e hora de Brasília atualizada:', dataFormatada);
    } catch (error) {
        console.error('Erro ao atualizar data/hora:', error);
    }
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados salvos
    carregarDadosSalvos();
    
    // Atualizar data e hora
    atualizarDataHoraBrasilia();
    setInterval(atualizarDataHoraBrasilia, 60000);
    
    // Configurar campo CEP com busca automática
    const cepInput = document.getElementById('cep-endereco');
    if (cepInput) {
        cepInput.addEventListener('input', function(e) {
            let cep = e.target.value.replace(/\D/g, '');
            e.target.value = formatarCEP(cep);
            
            // Buscar endereço automaticamente quando CEP tiver 8 dígitos
            if (cep.length === 8) {
                buscarEnderecoPorCEP(cep).then(endereco => {
                    if (endereco) {
                        preencherEndereco(endereco);
                        salvarDados(); // Salvar automaticamente
                    }
                });
            }
        });
    }
    
    // Configurar formatação do CPF
    const cpfInput = document.getElementById('cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function(e) {
            e.target.value = formatarCPF(e.target.value);
        });
    }
    
    // Configurar formatação dos telefones
    const telefoneInput = document.getElementById('telefone');
    const telefoneAltInput = document.getElementById('telefone-alt');
    
    if (telefoneInput) {
        telefoneInput.addEventListener('input', function(e) {
            e.target.value = formatarTelefone(e.target.value);
        });
    }
    
    if (telefoneAltInput) {
        telefoneAltInput.addEventListener('input', function(e) {
            e.target.value = formatarTelefone(e.target.value);
        });
    }
    
    // Salvar dados automaticamente quando campos são alterados
    const todosInputs = document.querySelectorAll('input, select');
    todosInputs.forEach(input => {
        input.addEventListener('change', salvarDados);
        input.addEventListener('blur', salvarDados);
    });
});