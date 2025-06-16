#!/usr/bin/env python3
"""
Teste e Demonstração do Sistema Avançado de Extração de PDF
Mostra as melhorias implementadas: PyMuPDF, layout estruturado e OCR
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
import logging

# Import do sistema avançado
from advanced_pdf_extractor import AdvancedPDFExtractor, extract_pdf_advanced

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_pdf_extraction_capabilities():
    """Testa as capacidades do extrator avançado"""
    print("🚀 Teste do Sistema Avançado de Extração de PDF")
    print("=" * 70)
    
    # Cria instância do extrator
    extractor = AdvancedPDFExtractor()
    
    # Mostra configuração do sistema
    print("📋 Configuração do Sistema:")
    print(f"   PyMuPDF disponível: {'✅' if extractor.use_pymupdf else '❌'}")
    print(f"   pdfplumber disponível: {'✅' if extractor.use_pdfplumber else '❌'}")
    print(f"   OCR (Tesseract) disponível: {'✅' if extractor.use_ocr else '❌'}")
    
    # Método de extração ativo
    if extractor.use_pymupdf:
        method = "PyMuPDF (Avançado)"
    elif extractor.use_pdfplumber:
        method = "pdfplumber (Estruturado)"
    else:
        method = "pypdf (Básico)"
    
    print(f"   Método ativo: {method}")
    print()
    
    # Busca PDFs de teste
    enem_folder = Path("./Segundo dia")
    if not enem_folder.exists():
        print("⚠️ Pasta 'Segundo dia' não encontrada. Criando PDFs de teste...")
        create_test_pdfs()
        return
    
    # Busca um PDF de exemplo
    test_pdfs = []
    for year_folder in enem_folder.iterdir():
        if year_folder.is_dir():
            pdfs = list(year_folder.glob("*.pdf"))
            if pdfs:
                test_pdfs.extend(pdfs[:1])  # Um PDF por ano
    
    if not test_pdfs:
        print("⚠️ Nenhum PDF encontrado para teste")
        return
    
    # Testa extração avançada
    for pdf_file in test_pdfs[:2]:  # Limita a 2 PDFs para o teste
        print(f"📄 Testando: {pdf_file.name}")
        print("-" * 50)
        
        try:
            # Extração completa
            structured_text, stats = extract_pdf_advanced(pdf_file)
            
            # Mostra estatísticas
            print("📊 Estatísticas da Extração:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
            
            # Mostra preview do texto
            print(f"\n📖 Preview do Texto Estruturado (primeiros 500 chars):")
            print(structured_text[:500] + "..." if len(structured_text) > 500 else structured_text)
            
            # Análise detalhada se PyMuPDF estiver disponível
            if extractor.use_pymupdf:
                analyze_pdf_structure(extractor, pdf_file)
            
            print()
            
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_file.name}: {e}")
            print()

def analyze_pdf_structure(extractor: AdvancedPDFExtractor, pdf_file: Path):
    """Análise detalhada da estrutura do PDF"""
    print(f"\n🔍 Análise Estrutural Detalhada:")
    
    try:
        pages = extractor.extract_from_pdf(pdf_file)
        
        total_blocks = sum(len(page.text_blocks) for page in pages)
        scanned_pages = sum(1 for page in pages if page.is_scanned)
        total_tables = sum(len(page.tables) for page in pages)
        
        print(f"   📄 Total de páginas: {len(pages)}")
        print(f"   📝 Total de blocos de texto: {total_blocks}")
        print(f"   🖼️ Páginas digitalizadas (OCR): {scanned_pages}")
        print(f"   📊 Tabelas detectadas: {total_tables}")
        
        # Análise por página
        for i, page in enumerate(pages[:3]):  # Primeiras 3 páginas
            print(f"\n   📄 Página {page.page_number}:")
            print(f"      🔤 Blocos de texto: {len(page.text_blocks)}")
            print(f"      📊 Tabelas: {len(page.tables)}")
            print(f"      📐 Colunas detectadas: {page.columns}")
            
            if page.is_scanned:
                print(f"      🔍 OCR - Qualidade: {page.ocr_quality:.1%}")
            
            # Classifica tipos de blocos
            block_types = {}
            confidence_scores = []
            
            for block in page.text_blocks:
                block_types[block.block_type] = block_types.get(block.block_type, 0) + 1
                confidence_scores.append(block.confidence)
            
            if block_types:
                print(f"      📋 Tipos de bloco: {dict(block_types)}")
            
            if confidence_scores:
                avg_confidence = sum(confidence_scores) / len(confidence_scores)
                print(f"      ✅ Confiança média: {avg_confidence:.1%}")
            
            # Mostra alguns blocos de exemplo
            if page.text_blocks:
                print(f"      📄 Exemplo de blocos:")
                for j, block in enumerate(page.text_blocks[:3]):
                    preview = block.text[:100].replace('\n', ' ')
                    if len(block.text) > 100:
                        preview += "..."
                    
                    confidence_str = f" [{block.confidence:.1%}]" if block.confidence < 1.0 else ""
                    print(f"         {j+1}. [{block.block_type}]{confidence_str}: {preview}")
    
    except Exception as e:
        print(f"   ❌ Erro na análise estrutural: {e}")

def create_test_pdfs():
    """Cria PDFs de teste simples para demonstração"""
    print("📄 Criando PDFs de teste...")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Cria pasta de teste
        test_folder = Path("./Segundo dia/2023")
        test_folder.mkdir(parents=True, exist_ok=True)
        
        # PDF de teste 1
        pdf_path = test_folder / "teste_avancado.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        
        # Adiciona conteúdo estruturado
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "QUESTÃO 91")
        
        c.setFont("Helvetica", 12)
        text = """
        Muitas pessoas ainda se espantam com o fato de um passageiro sair ileso de um
        acidente de carro enquanto o veículo onde estava teve perda total.
        
        A função do cinto de segurança é:
        """
        
        y = 700
        for line in text.strip().split('\n'):
            c.drawString(100, y, line.strip())
            y -= 20
        
        # Alternativas
        alternatives = [
            "A) acionar os airbags do veículo.",
            "B) absorver a energia cinética do sistema.", 
            "C) reduzir a velocidade do veículo.",
            "D) aumentar o tempo de colisão.",
            "E) diminuir a força média de impacto."
        ]
        
        y = 600
        for alt in alternatives:
            c.drawString(120, y, alt)
            y -= 30
        
        c.save()
        
        print(f"✅ PDF de teste criado: {pdf_path}")
        
    except ImportError:
        print("⚠️ reportlab não disponível. Use PDFs existentes para teste.")
        print("💡 Instale com: pip install reportlab")

def show_installation_guide():
    """Mostra guia de instalação das dependências"""
    print("\n📦 Guia de Instalação das Dependências Avançadas:")
    print("=" * 60)
    
    dependencies = {
        "PyMuPDF": {
            "command": "pip install PyMuPDF",
            "description": "Extração avançada com informações de layout e fonte",
            "features": ["Detecção de layout", "Informações de fonte", "Extração de imagens"]
        },
        "pdfplumber": {
            "command": "pip install pdfplumber",
            "description": "Extração estruturada com foco em tabelas",
            "features": ["Extração de tabelas", "Posicionamento preciso", "Detecção de colunas"]
        },
        "Tesseract OCR": {
            "command": "pip install pytesseract && apt-get install tesseract-ocr tesseract-ocr-por",
            "description": "OCR para PDFs digitalizados",
            "features": ["Reconhecimento de texto", "Suporte a português", "Pré-processamento de imagem"]
        },
        "OpenCV": {
            "command": "pip install opencv-python",
            "description": "Processamento de imagem para OCR",
            "features": ["Pré-processamento", "Remoção de ruído", "Melhoria de contraste"]
        }
    }
    
    for name, info in dependencies.items():
        print(f"\n🔧 {name}:")
        print(f"   📦 Instalação: {info['command']}")
        print(f"   📋 Descrição: {info['description']}")
        print(f"   ✨ Recursos: {', '.join(info['features'])}")

def demonstrate_ocr_capabilities():
    """Demonstra capacidades de OCR"""
    print("\n🔍 Demonstração de Capacidades OCR:")
    print("=" * 50)
    
    extractor = AdvancedPDFExtractor()
    
    if not extractor.use_ocr:
        print("❌ OCR não disponível. Instale pytesseract e tesseract-ocr")
        print("💡 Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-por")
        print("💡 Windows: Baixe de https://github.com/UB-Mannheim/tesseract/wiki")
        print("💡 macOS: brew install tesseract")
        return
    
    print("✅ OCR disponível e configurado")
    print(f"   Configuração Tesseract: {extractor.tesseract_config}")
    print(f"   Idioma: Português")
    print(f"   Pré-processamento: Contraste + Nitidez + Remoção de ruído")

if __name__ == "__main__":
    # Executa testes completos
    test_pdf_extraction_capabilities()
    
    # Mostra guia de instalação
    show_installation_guide()
    
    # Demonstra OCR
    demonstrate_ocr_capabilities()
    
    print("\n🎯 Resumo das Melhorias Implementadas:")
    print("=" * 50)
    print("✅ PyMuPDF: Extração avançada com layout e formatação")
    print("✅ pdfplumber: Detecção de tabelas e estruturas")
    print("✅ OCR Tesseract: Suporte a PDFs digitalizados")
    print("✅ Pré-processamento: Melhoria automática de qualidade")
    print("✅ Detecção de estrutura: Questões, alternativas, títulos")
    print("✅ Qualidade adaptativa: Scores de confiança")
    print("✅ Fallback inteligente: Múltiplas estratégias de extração")
    
    print("\n🚀 O sistema está pronto para processar PDFs com qualidade superior!") 