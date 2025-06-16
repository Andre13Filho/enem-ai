#!/usr/bin/env python3
"""
Configuração adaptativa para ENEM AI Helper
Funciona tanto localmente quanto no Streamlit Cloud
"""

import os
import streamlit as st
from typing import Dict, Any, Optional
import tempfile
import shutil
from pathlib import Path

class CloudConfig:
    """Gerenciador de configuração para ambiente cloud e local"""
    
    def __init__(self):
        self.is_cloud = self._detect_cloud_environment()
        self.temp_dir = None
        
    def _detect_cloud_environment(self) -> bool:
        """Detecta se está rodando no Streamlit Cloud"""
        # Streamlit Cloud tem essas variáveis de ambiente
        cloud_indicators = [
            'STREAMLIT_SHARING_MODE',
            'STREAMLIT_SERVER_PORT', 
            'HOSTNAME'
        ]
        
        # Verifica se algum indicador está presente
        for indicator in cloud_indicators:
            if os.getenv(indicator):
                return True
                
        # Verifica se está no diretório típico do Streamlit Cloud
        if '/mount/src/' in os.getcwd():
            return True
            
        return False
    
    def get_api_key(self, key_name: str = "GROQ_API_KEY") -> Optional[str]:
        """Obtém chave de API de forma adaptativa"""
        try:
            if self.is_cloud:
                # No Streamlit Cloud, usa st.secrets
                return st.secrets.get(key_name)
            else:
                # Localmente, usa variáveis de ambiente ou .env
                return os.getenv(key_name)
        except Exception as e:
            st.error(f"Erro ao obter chave de API: {e}")
            return None
    
    def get_vectorstore_path(self, subject: str) -> str:
        """Obtém caminho do vectorstore de forma adaptativa"""
        if self.is_cloud:
            # No cloud, usa diretório temporário
            if not self.temp_dir:
                self.temp_dir = tempfile.mkdtemp()
            return os.path.join(self.temp_dir, f"chroma_{subject}_vectorstore")
        else:
            # Localmente, usa diretório padrão
            return f"./chroma_{subject}_vectorstore"
    
    def get_documents_path(self, subject: str) -> str:
        """Obtém caminho dos documentos de forma adaptativa"""
        if self.is_cloud:
            # No cloud, verifica se existe pasta de documentos
            cloud_path = f"./{subject}"
            if os.path.exists(cloud_path):
                return cloud_path
            else:
                # Se não existir, cria pasta temporária com documentos de exemplo
                return self._create_sample_documents(subject)
        else:
            # Localmente, usa pasta padrão
            return f"./{subject}"
    
    def _create_sample_documents(self, subject: str) -> str:
        """Cria documentos de exemplo para o cloud"""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp()
            
        subject_dir = os.path.join(self.temp_dir, subject)
        os.makedirs(subject_dir, exist_ok=True)
        
        # Cria documento de exemplo baseado na matéria
        sample_content = self._get_sample_content(subject)
        
        sample_file = os.path.join(subject_dir, f"{subject}_exemplo.txt")
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
            
        return subject_dir
    
    def _get_sample_content(self, subject: str) -> str:
        """Retorna conteúdo de exemplo para cada matéria"""
        samples = {
            "matemática": """
            # Matemática - Conceitos Fundamentais para o ENEM
            
            ## Função Quadrática
            Uma função quadrática é definida por f(x) = ax² + bx + c, onde a ≠ 0.
            
            ### Fórmula de Bhaskara
            x = (-b ± √(b² - 4ac)) / 2a
            
            ### Discriminante
            Δ = b² - 4ac
            
            ## Geometria
            ### Área do Círculo
            A = πr²
            
            ### Volume do Cilindro
            V = πr²h
            """,
            
            "física": """
            # Física - Conceitos Fundamentais para o ENEM
            
            ## Cinemática
            ### Velocidade Média
            v = Δs/Δt
            
            ### Movimento Uniformemente Variado
            v = v₀ + at
            s = s₀ + v₀t + (1/2)at²
            v² = v₀² + 2aΔs
            
            ## Dinâmica
            ### Segunda Lei de Newton
            F = ma
            
            ### Força de Atrito
            Fat = μN
            
            ## Energia
            ### Energia Cinética
            Ec = (1/2)mv²
            
            ### Energia Potencial Gravitacional
            Epg = mgh
            """,
            
            "química": """
            # Química - Conceitos Fundamentais para o ENEM
            
            ## Estrutura Atômica
            O átomo é composto por prótons, nêutrons e elétrons.
            
            ## Tabela Periódica
            Os elementos são organizados por número atômico crescente.
            
            ## Ligações Químicas
            ### Ligação Iônica
            Transferência de elétrons entre átomos.
            
            ### Ligação Covalente
            Compartilhamento de elétrons entre átomos.
            """,
            
            "biologia": """
            # Biologia - Conceitos Fundamentais para o ENEM
            
            ## Citologia
            A célula é a unidade básica da vida.
            
            ## Genética
            ### Leis de Mendel
            Primeira Lei: Lei da Segregação
            Segunda Lei: Lei da Segregação Independente
            
            ## Ecologia
            ### Cadeia Alimentar
            Produtores → Consumidores Primários → Consumidores Secundários
            """,
            
            "história": """
            # História - Conceitos Fundamentais para o ENEM
            
            ## Brasil Colonial
            O período colonial brasileiro durou de 1500 a 1822.
            
            ## Independência do Brasil
            Proclamada em 7 de setembro de 1822 por Dom Pedro I.
            
            ## República
            Proclamada em 15 de novembro de 1889.
            """,
            
            "geografia": """
            # Geografia - Conceitos Fundamentais para o ENEM
            
            ## Geografia Física
            ### Relevo Brasileiro
            Planaltos, planícies e depressões.
            
            ### Clima
            Tropical, subtropical, equatorial, semiárido.
            
            ## Geografia Humana
            ### Urbanização
            Processo de crescimento das cidades.
            
            ### Demografia
            Estudo da população.
            """
        }
        
        return samples.get(subject, f"# {subject.title()}\n\nConteúdo de exemplo para {subject}.")
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Verifica se uma feature está habilitada"""
        try:
            if self.is_cloud:
                return st.secrets.get("features", {}).get(feature, True)
            else:
                return os.getenv(f"ENABLE_{feature.upper()}", "true").lower() == "true"
        except:
            return True
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Obtém configurações de performance"""
        default_config = {
            "max_tokens": 4000,
            "temperature": 0.7,
            "max_retries": 3
        }
        
        try:
            if self.is_cloud:
                performance = st.secrets.get("performance", {})
                return {**default_config, **performance}
            else:
                return {
                    "max_tokens": int(os.getenv("MAX_TOKENS", default_config["max_tokens"])),
                    "temperature": float(os.getenv("TEMPERATURE", default_config["temperature"])),
                    "max_retries": int(os.getenv("MAX_RETRIES", default_config["max_retries"]))
                }
        except:
            return default_config
    
    def cleanup(self):
        """Limpa recursos temporários"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

# Instância global
config = CloudConfig()

def get_config() -> CloudConfig:
    """Retorna a instância de configuração"""
    return config 