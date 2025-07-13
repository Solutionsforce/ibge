from app import db
from datetime import datetime
from sqlalchemy import Text

class ConcursoPublico(db.Model):
    """Model for public contests/exams"""
    __tablename__ = 'concursos_publicos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(Text)
    edital_url = db.Column(db.String(500))
    data_inicio_inscricao = db.Column(db.Date)
    data_fim_inscricao = db.Column(db.Date)
    data_prova = db.Column(db.Date)
    status = db.Column(db.String(50), default='ativo')  # ativo, encerrado, suspenso
    vagas = db.Column(db.Integer)
    salario = db.Column(db.Numeric(10, 2))
    escolaridade = db.Column(db.String(100))
    cargo = db.Column(db.String(150))
    local_prova = db.Column(db.String(200))
    taxa_inscricao = db.Column(db.Numeric(8, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConcursoPublico {self.titulo}>'

class ProcessoSeletivo(db.Model):
    """Model for simplified selection processes"""
    __tablename__ = 'processos_seletivos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(Text)
    tipo = db.Column(db.String(100))  # temporario, terceirizado, etc
    edital_url = db.Column(db.String(500))
    data_inicio_inscricao = db.Column(db.Date)
    data_fim_inscricao = db.Column(db.Date)
    status = db.Column(db.String(50), default='ativo')
    vagas = db.Column(db.Integer)
    salario = db.Column(db.Numeric(10, 2))
    escolaridade = db.Column(db.String(100))
    cargo = db.Column(db.String(150))
    duracao_contrato = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProcessoSeletivo {self.titulo}>'

class VagaEstagio(db.Model):
    """Model for internship opportunities"""
    __tablename__ = 'vagas_estagio'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(Text)
    nivel = db.Column(db.String(50))  # superior, medio
    area = db.Column(db.String(100))
    curso_requerido = db.Column(db.String(150))
    carga_horaria = db.Column(db.String(50))
    bolsa_auxilio = db.Column(db.Numeric(8, 2))
    local = db.Column(db.String(200))
    data_inicio_inscricao = db.Column(db.Date)
    data_fim_inscricao = db.Column(db.Date)
    status = db.Column(db.String(50), default='ativo')
    vagas = db.Column(db.Integer)
    edital_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VagaEstagio {self.titulo}>'

class CookieConsent(db.Model):
    """Model to track cookie consent"""
    __tablename__ = 'cookie_consents'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    consent_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    consent_type = db.Column(db.String(50), default='accepted')
    
    def __repr__(self):
        return f'<CookieConsent {self.ip_address} at {self.consent_timestamp}>'

class PixRequestLimit(db.Model):
    """Model to track PIX request limits by CPF"""
    __tablename__ = 'pix_request_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=False, index=True)  # CPF formatado
    cpf_clean = db.Column(db.String(11), nullable=False, index=True)  # CPF apenas números
    nome_completo = db.Column(db.String(200))
    email = db.Column(db.String(120))
    transaction_id = db.Column(db.String(100))  # ID da transação Cashtime
    amount = db.Column(db.Numeric(10, 2))  # Valor do PIX
    status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PixRequestLimit {self.cpf} - {self.created_at}>'
    
    @staticmethod
    def get_request_count(cpf_clean: str) -> int:
        """Get the number of PIX requests for a CPF"""
        return PixRequestLimit.query.filter_by(cpf_clean=cpf_clean).count()
    
    @staticmethod
    def is_limit_exceeded(cpf_clean: str, limit: int = 8) -> bool:
        """Check if PIX request limit is exceeded for a CPF"""
        return PixRequestLimit.get_request_count(cpf_clean) >= limit
    
    @staticmethod
    def add_request(cpf: str, nome_completo: str, email: str, transaction_id: str, amount: float, ip_address: str = None, user_agent: str = None):
        """Add a new PIX request record"""
        cpf_clean = cpf.replace('.', '').replace('-', '')
        
        new_request = PixRequestLimit(
            cpf=cpf,
            cpf_clean=cpf_clean,
            nome_completo=nome_completo,
            email=email,
            transaction_id=transaction_id,
            amount=amount,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(new_request)
        db.session.commit()
        return new_request