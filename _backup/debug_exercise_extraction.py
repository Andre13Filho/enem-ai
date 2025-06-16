import PyPDF2
import re
import json

def debug_pdf_content(pdf_path: str):
    """Debug do conteúdo de um PDF específico"""
    print(f"🔍 DEBUGANDO: {pdf_path}")
    print("="*60)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Analisa as primeiras páginas que contêm matemática
            for page_num in range(min(5, len(pdf_reader.pages))):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                print(f"\n--- PÁGINA {page_num + 1} ---")
                
                # Procura por questões numeradas
                question_matches = re.findall(r'(QUESTÃO\s+\d+|(?:^|\n)\s*(\d{3})\s*[.\-)])', text, re.MULTILINE)
                print(f"Questões encontradas: {question_matches}")
                
                # Procura por alternativas
                alternatives = re.findall(r'\([A-E]\)', text)
                print(f"Alternativas encontradas: {len(alternatives)} - {alternatives}")
                
                # Mostra uma amostra do texto bruto
                print(f"\nAMOSTRA DO TEXTO (primeiros 500 caracteres):")
                print(repr(text[:500]))
                
                # Procura especificamente por questão 136 (primeira de matemática)
                q136_match = re.search(r'(136|QUESTÃO\s+136).*?(?=137|QUESTÃO\s+137|$)', text, re.DOTALL)
                if q136_match:
                    print(f"\n🎯 QUESTÃO 136 ENCONTRADA:")
                    q136_text = q136_match.group(0)
                    print(f"Tamanho: {len(q136_text)} caracteres")
                    print(f"Conteúdo: {repr(q136_text[:300])}...")
                    
                    # Analisa alternativas nesta questão
                    q136_alts = re.findall(r'\([A-E]\)', q136_text)
                    print(f"Alternativas na Q136: {q136_alts}")
                
                if page_num == 2:  # Para após algumas páginas
                    break
                    
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def analyze_specific_question_pattern(pdf_path: str):
    """Analisa padrões específicos de questões"""
    print(f"\n🔬 ANÁLISE DETALHADA DE PADRÕES")
    print("="*60)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extrai todo o texto
            full_text = ""
            for page in pdf_reader.pages[:10]:  # Primeiras 10 páginas
                full_text += page.extract_text() + "\n"
            
            # Procura por diferentes padrões de questão
            patterns = [
                r'QUESTÃO\s+(\d+)',
                r'(?:^|\n)\s*(\d{3})\s*[.\-)]',
                r'(?:^|\n)\s*(\d+)\s*[.\-)](?=\s*[A-Z])',
                r'(\d{3})\s+',
            ]
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, full_text, re.MULTILINE)
                print(f"Padrão {i+1} ({pattern}): {len(matches)} matches")
                if matches:
                    print(f"  Números encontrados: {matches[:10]}...")  # Primeiros 10
            
            # Analisa blocos com alternativas
            print(f"\n📝 ANÁLISE DE BLOCOS COM ALTERNATIVAS:")
            
            # Encontra todos os blocos que têm pelo menos 3 alternativas
            alt_pattern = r'(?=\([A-E]\).*?\([A-E]\).*?\([A-E]\))'
            blocks = re.split(alt_pattern, full_text)
            
            valid_blocks = []
            for block in blocks:
                if len(block.strip()) > 100:  # Blocos substanciais
                    alts = re.findall(r'\([A-E]\)', block)
                    if len(alts) >= 3:
                        valid_blocks.append(block)
            
            print(f"Blocos com alternativas válidas: {len(valid_blocks)}")
            
            # Mostra o primeiro bloco como exemplo
            if valid_blocks:
                print(f"\n📋 EXEMPLO DE BLOCO VÁLIDO:")
                example_block = valid_blocks[0]
                print(f"Tamanho: {len(example_block)} caracteres")
                print(f"Alternativas: {re.findall(r'\\([A-E]\\)', example_block)}")
                print(f"Primeiros 200 caracteres: {repr(example_block[:200])}...")
                
                # Tenta separar enunciado e alternativas
                alt_matches = list(re.finditer(r'\([A-E]\)', example_block))
                if alt_matches:
                    statement = example_block[:alt_matches[0].start()].strip()
                    print(f"\nEnunciado extraído ({len(statement)} chars): {repr(statement[:100])}...")
                    
                    alternatives = []
                    for i, match in enumerate(alt_matches):
                        start = match.start()
                        end = alt_matches[i + 1].start() if i + 1 < len(alt_matches) else len(example_block)
                        alt_text = example_block[start:end].strip()
                        clean_alt = re.sub(r'^\([A-E]\)\s*', '', alt_text).strip()
                        alternatives.append(clean_alt)
                    
                    print(f"\nAlternativas extraídas:")
                    for i, alt in enumerate(alternatives):
                        letter = chr(65 + i)
                        print(f"  {letter}) {alt[:60]}{'...' if len(alt) > 60 else ''}")
            
    except Exception as e:
        print(f"❌ Erro na análise: {str(e)}")

def main():
    """Função principal de debug"""
    test_files = [
        "Segundo dia/2024/dia02_2024.pdf",
        "Segundo dia/2023/enem_2023_2.pdf",
    ]
    
    for pdf_file in test_files:
        try:
            debug_pdf_content(pdf_file)
            analyze_specific_question_pattern(pdf_file)
            print("\n" + "="*80 + "\n")
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_file}: {str(e)}")

if __name__ == "__main__":
    main() 