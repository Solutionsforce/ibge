from flask import render_template, request, jsonify, session, redirect
from app import app
from models import ConcursoPublico, ProcessoSeletivo, VagaEstagio, CookieConsent
from app import db

def register_routes(app):
    """Registrar todas as rotas da aplicação"""
    
    @app.route('/')
    def index():
        """Página principal - Trabalhe Conosco IBGE"""
        concursos = ConcursoPublico.query.filter_by(status='ativo').all()
        processos = ProcessoSeletivo.query.filter_by(status='ativo').all()
        estagios = VagaEstagio.query.filter_by(status='ativo').all()
        
        return render_template('index.html', 
                             concursos=concursos,
                             processos=processos, 
                             estagios=estagios)

    @app.route('/concursos')
    def concursos():
        """Página de concursos públicos"""
        concursos_ativos = ConcursoPublico.query.filter_by(status='ativo').all()
        return render_template('concursos.html', concursos=concursos_ativos)

    @app.route('/processos_seletivos')
    def processos_seletivos():
        """Página de processos seletivos"""
        processos_ativos = ProcessoSeletivo.query.filter_by(status='ativo').all()
        return render_template('processos_seletivos.html', processos=processos_ativos)

    @app.route('/estagios')
    def estagios():
        """Página de estágios"""
        estagios_ativos = VagaEstagio.query.filter_by(status='ativo').all()
        return render_template('estagios.html', estagios=estagios_ativos)

    @app.route('/login')
    def login():
        """Página de login gov.br"""
        return render_template('login.html')

    @app.route('/api/validate-cpf', methods=['POST'])
    def validate_cpf():
        """API para validar CPF e carregar dados gov.br"""
        data = request.get_json()
        cpf = data.get('cpf', '').replace('.', '').replace('-', '')
        
        # Simulação de dados gov.br
        user_data = {
            'nome_completo': 'João Silva Santos',
            'nome_mae': 'Maria Silva Santos',
            'data_nascimento': '15/03/1985',
            'cpf': cpf,
            'rg': '12.345.678-9',
            'naturalidade': 'São Paulo - SP',
            'sexo': 'Masculino',
            'estado_civil': 'Casado(a)'
        }
        
        session['user_data'] = user_data
        return jsonify({'success': True, 'data': user_data})



    @app.route('/selecao-cargo')
    def selecao_cargo():
        """Página de seleção de cargo"""
        return render_template('selecao_cargo.html')

    @app.route('/confirmacao-dados')
    def confirmacao_dados():
        """Página de confirmação de dados"""
        return render_template('confirmacao_dados.html')

    @app.route('/selecao-local-prova')
    def selecao_local_prova():
        """Página de seleção do local da prova"""
        return render_template('selecao_local_prova.html')

    @app.route('/api/buscar-escolas')
    def api_buscar_escolas():
        """API simplificada para buscar escolas"""
        cep = request.args.get('cep', '')
        
        # Dados fictícios de escolas
        escolas = [
            {
                'nome': 'Escola Estadual Professor João Silva',
                'endereco': 'Rua das Flores, 123 - Centro',
                'distancia': '2.5 km',
                'dependencia': 'Estadual',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '23456789'
            },
            {
                'nome': 'Colégio Municipal Maria Aparecida',
                'endereco': 'Av. Principal, 456 - Bairro Novo',
                'distancia': '3.2 km',
                'dependencia': 'Municipal',
                'etapas': 'Ensino Fundamental',
                'codigo_inep': '34567890'
            },
            {
                'nome': 'Centro Educacional São José',
                'endereco': 'Rua da Escola, 789 - Vila Santos',
                'distancia': '4.1 km',
                'dependencia': 'Privada',
                'etapas': 'Ensino Fundamental e Médio',
                'codigo_inep': '45678901'
            }
        ]
        
        return jsonify({
            'escolas': escolas,
            'endereco_usuario': 'Endereço consultado via CEP',
            'erro_busca': False
        })

    @app.route('/checkout')
    def checkout():
        """Página de checkout PIX"""
        return render_template('checkout.html')

    @app.route('/gerar-pix', methods=['POST'])
    def gerar_pix():
        """API para gerar pagamento PIX"""
        try:
            from for4_payments import For4PaymentsAPI, PaymentRequestData

            data = request.get_json()

            # Validar dados obrigatórios
            required_fields = ['name', 'email', 'cpf', 'amount']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'erro': f'Campo {field} é obrigatório'}), 400

            # Criar instância da API
            api = For4PaymentsAPI.from_env()

            # Preparar dados do pagamento
            payment_data = PaymentRequestData(
                name=data['name'],
                email=data['email'],
                cpf=data['cpf'],
                amount=int(data['amount']),  # Valor em centavos
                phone=data.get('phone'),
                description="Inscrição IBGE - Concurso Público 2025"
            )

            # Criar pagamento PIX
            response = api.create_pix_payment(payment_data)

            return jsonify({
                'id': response.id,
                'pix_code': response.pix_code,
                'pix_qr_code': response.pix_qr_code,
                'expires_at': response.expires_at,
                'status': response.status
            })

        except Exception as e:
            print(f"Erro ao gerar PIX: {str(e)}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500

    @app.route('/verificar-pagamento/<payment_id>')
    def verificar_pagamento(payment_id):
        """API para verificar status do pagamento"""
        try:
            from for4_payments import For4PaymentsAPI
            
            api = For4PaymentsAPI.from_env()
            status = api.check_payment_status(payment_id)
            
            return jsonify(status)
        except Exception as e:
            print(f"Erro ao verificar pagamento: {str(e)}")
            return jsonify({'erro': 'Erro ao verificar pagamento'}), 500

    @app.route('/accept-cookies', methods=['POST'])
    def accept_cookies():
        """API para aceitar cookies"""
        try:
            consent = CookieConsent(
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                consent_type='accepted'
            )
            db.session.add(consent)
            db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            print(f"Erro ao salvar consent: {str(e)}")
            return jsonify({'success': False}), 500

    # Páginas estáticas
    @app.route('/mais-informacoes')
    def mais_informacoes():
        return render_template('mais_informacoes.html')

    @app.route('/atendimento')
    def atendimento():
        return render_template('atendimento.html')

    @app.route('/apps-ibge')
    def apps_ibge():
        return render_template('apps_ibge.html')

    @app.route('/transparencia')
    def transparencia():
        return render_template('transparencia.html')

    @app.route('/privacidade')
    def privacidade():
        return render_template('privacidade.html')

    @app.route('/orgaos-governo')
    def orgaos_governo():
        return render_template('orgaos_governo.html')

    @app.route('/edital-completo')
    def edital_completo():
        return render_template('edital_completo.html')

    @app.route('/confirmar-local-prova', methods=['POST'])
    def confirmar_local_prova():
        """Confirmar seleção do local da prova"""
        escola_selecionada = request.form.get('escola_selecionada')

        if not escola_selecionada:
            return redirect('/selecao-local-prova')

        # Salvar escola selecionada na sessão
        session['local_prova'] = escola_selecionada

        # Redirecionar para checkout
        return redirect('/checkout')