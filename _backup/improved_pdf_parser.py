import re
import PyPDF2
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ParsedExercise:
    """Estrutura para um exercício bem formatado"""
    question_number: int
    main_statement: str
    alternatives: List[str]
    year: int
    page_info: str = ""

class ImprovedPDFParser:
    """Parser melhorado para extrair exercícios bem formatados dos PDFs do ENEM"""
    
    def __init__(self):
        self.unwanted_patterns = [
            r'ENEM\d{4}' * 20,  # Remove repetições de ENEM2024
            r'\*\d+\*',  # Remove códigos como *020325AZ5*
            r'CIÊNCIAS DA NATUREZA.*?AZUL.*?\d+',  # Remove headers
            r'ENEM\d{4}ENEM\d{4}.*?(?=\n)',  # Remove linhas de códigos repetidos
            r'020325AZ\.indb.*?\d{2}:\d{2}:\d{2}',  # Remove informações de arquivo
        ]
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrai texto do PDF de forma limpa"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    
                    # Adiciona informação da página para contexto
                    text += f"\n--- PÁGINA {page_num + 1} ---\n"
                    text += page_text + "\n"
                
                return self._clean_extracted_text(text)
                
        except Exception as e:
            print(f"Erro ao extrair texto de {pdf_path}: {str(e)}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Remove padrões indesejados do texto extraído"""
        cleaned_text = text
        
        # Remove padrões indesejados
        for pattern in self.unwanted_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove linhas com muitas repetições
        lines = cleaned_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Remove linhas que são principalmente repetições de código
            if not self._is_code_repetition_line(line):
                filtered_lines.append(line)
        
        # Reconstrói o texto
        cleaned_text = '\n'.join(filtered_lines)
        
        # Remove múltiplas quebras de linha
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def _is_code_repetition_line(self, line: str) -> bool:
        """Verifica se uma linha é principalmente repetição de códigos"""
        # Se mais de 70% da linha for repetição de padrões
        repetition_patterns = [
            r'ENEM\d{4}',
            r'[A-Z]{2}\d+',
            r'\d{6}AZ',
        ]
        
        total_chars = len(line)
        if total_chars < 10:
            return False
        
        repetition_chars = 0
        for pattern in repetition_patterns:
            matches = re.findall(pattern, line)
            repetition_chars += sum(len(match) for match in matches)
        
        return (repetition_chars / total_chars) > 0.7
    
    def parse_exercises_from_text(self, text: str, year: int) -> List[ParsedExercise]:
        """Extrai exercícios bem formatados do texto"""
        exercises = []
        
        # Padrão melhorado para identificar questões
        question_patterns = [
            r'QUESTÃO\s+(\d+)',
            r'(?:^|\n)\s*(\d+)\s*[.)\-]',  # Números de questão isolados
            r'(?:^|\n)\s*Questão\s+(\d+)',
        ]
        
        # Tenta diferentes padrões
        for pattern in question_patterns:
            matches = list(re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE))
            
            if matches:
                exercises.extend(self._extract_exercises_from_matches(text, matches, year))
                break
        
        # Se não encontrou questões numeradas, tenta método alternativo
        if not exercises:
            exercises = self._extract_exercises_alternative_method(text, year)
        
        return exercises
    
    def _extract_exercises_from_matches(self, text: str, matches: List, year: int) -> List[ParsedExercise]:
        """Extrai exercícios baseado em matches de números de questão"""
        exercises = []
        
        for i, match in enumerate(matches):
            question_num = int(match.group(1))
            
            # Define o início e fim do exercício
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            
            exercise_text = text[start_pos:end_pos].strip()
            
            # Só processa se for questão de matemática (questões 136-180 no segundo dia)
            if self._is_math_question_number(question_num):
                parsed_exercise = self._parse_single_exercise(
                    exercise_text, question_num, year
                )
                if parsed_exercise:
                    exercises.append(parsed_exercise)
        
        return exercises
    
    def _extract_exercises_alternative_method(self, text: str, year: int) -> List[ParsedExercise]:
        """Método alternativo para extrair exercícios quando não há numeração clara"""
        exercises = []
        
        # Divide o texto em blocos baseado em padrões de alternativas
        alternative_pattern = r'(?=\([A-E]\))'
        blocks = re.split(alternative_pattern, text)
        
        for i, block in enumerate(blocks):
            if len(block.strip()) > 50:  # Só processa blocos substanciais
                # Estima número da questão baseado na posição
                estimated_question_num = 136 + i  # Começa em 136 (início da matemática)
                
                if self._contains_math_content(block):
                    parsed_exercise = self._parse_single_exercise(
                        block, estimated_question_num, year
                    )
                    if parsed_exercise:
                        exercises.append(parsed_exercise)
        
        return exercises
    
    def _parse_single_exercise(self, exercise_text: str, question_num: int, year: int) -> Optional[ParsedExercise]:
        """Parse de um único exercício"""
        try:
            # Limpa o texto do exercício
            clean_text = self._clean_exercise_text(exercise_text)
            
            # Separa enunciado e alternativas
            statement, alternatives = self._separate_statement_and_alternatives(clean_text)
            
            if statement and len(alternatives) >= 3:  # Pelo menos 3 alternativas
                return ParsedExercise(
                    question_number=question_num,
                    main_statement=statement.strip(),
                    alternatives=alternatives,
                    year=year,
                    page_info=""
                )
            
            return None
            
        except Exception as e:
            print(f"Erro ao processar exercício {question_num}: {str(e)}")
            return None
    
    def _clean_exercise_text(self, text: str) -> str:
        """Limpa o texto de um exercício específico"""
        # Remove padrões específicos de questão
        patterns_to_remove = [
            r'Disponível em:.*?Acesso em:.*?\d{4}.*?(?=\n|$)',  # Remove referências
            r'\*[A-Z0-9]+\*',  # Remove códigos entre asteriscos
            r'--- PÁGINA \d+ ---',  # Remove marcadores de página
            r'(?:^|\n)\s*[A-Z\s]{20,}(?=\n|$)',  # Remove linhas de cabeçalho em maiúscula
        ]
        
        cleaned = text
        for pattern in patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Normaliza espaços e quebras de linha
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)  # Remove linhas vazias duplas
        cleaned = re.sub(r' {2,}', ' ', cleaned)  # Remove espaços múltiplos
        
        return cleaned.strip()
    
    def _separate_statement_and_alternatives(self, text: str) -> Tuple[str, List[str]]:
        """Separa enunciado principal das alternativas"""
        # Procura por padrão de alternativas (A) (B) (C) (D) (E)
        alternative_pattern = r'\([A-E]\)'
        
        # Encontra todas as posições das alternativas
        alternative_matches = list(re.finditer(alternative_pattern, text))
        
        if not alternative_matches:
            # Se não encontrou alternativas, retorna texto completo como enunciado
            return text, []
        
        # O enunciado vai até a primeira alternativa
        statement_end = alternative_matches[0].start()
        statement = text[:statement_end].strip()
        
        # Extrai as alternativas
        alternatives = []
        for i, match in enumerate(alternative_matches):
            start_pos = match.start()
            
            # Fim da alternativa: início da próxima ou fim do texto
            if i + 1 < len(alternative_matches):
                end_pos = alternative_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            alternative_text = text[start_pos:end_pos].strip()
            
            # Remove a letra da alternativa e limpa o texto
            alternative_clean = re.sub(r'^\([A-E]\)\s*', '', alternative_text).strip()
            
            if alternative_clean:  # Só adiciona se não estiver vazio
                alternatives.append(alternative_clean)
        
        return statement, alternatives
    
    def _is_math_question_number(self, question_num: int) -> bool:
        """Verifica se o número da questão corresponde a matemática"""
        # No ENEM, matemática geralmente está nas questões 136-180 do segundo dia
        return 136 <= question_num <= 180
    
    def _contains_math_content(self, text: str) -> bool:
        """Verifica se o texto contém conteúdo matemático"""
        math_keywords = [
            'função', 'equação', 'gráfico', 'geometria', 'triângulo',
            'círculo', 'área', 'volume', 'probabilidade', 'estatística',
            'porcentagem', 'juros', 'progressão', 'logaritmo', 'raiz',
            'potência', 'fração', 'decimal', 'número', 'cálculo',
            'matriz', 'vetor', 'ângulo', 'medida', 'unidade'
        ]
        
        text_lower = text.lower()
        math_count = sum(1 for keyword in math_keywords if keyword in text_lower)
        
        # Se tem pelo menos 2 palavras-chave matemáticas
        return math_count >= 2
    
    def format_exercise_for_display(self, exercise: ParsedExercise) -> str:
        """Formata um exercício para exibição"""
        formatted = f"QUESTÃO {exercise.question_number} - ENEM {exercise.year}\n"
        formatted += "=" * 50 + "\n\n"
        formatted += f"ENUNCIADO:\n{exercise.main_statement}\n\n"
        formatted += "ALTERNATIVAS:\n"
        
        for i, alt in enumerate(exercise.alternatives):
            letter = chr(65 + i)  # A, B, C, D, E
            formatted += f"{letter}) {alt}\n"
        
        return formatted

def main():
    """Função para testar o parser melhorado"""
    import os
    parser = ImprovedPDFParser()
    
    # Testa com um PDF
    test_files = [
        "Segundo dia/2024/dia02_2024.pdf",
        "Segundo dia/2023/enem_2023_2.pdf",
    ]
    
    for pdf_file in test_files:
        if os.path.exists(pdf_file):
            print(f"\n🔍 Processando {pdf_file}...")
            
            # Extrai texto
            text = parser.extract_text_from_pdf(pdf_file)
            
            # Extrai exercícios
            year = int(re.search(r'(\d{4})', pdf_file).group(1))
            exercises = parser.parse_exercises_from_text(text, year)
            
            print(f"✅ Encontrados {len(exercises)} exercícios bem formatados")
            
            # Mostra os primeiros 2 exercícios como exemplo
            for i, exercise in enumerate(exercises[:2]):
                print(f"\n--- EXEMPLO {i+1} ---")
                print(parser.format_exercise_for_display(exercise))
                print("-" * 70)
        
        else:
            print(f"❌ Arquivo não encontrado: {pdf_file}")

if __name__ == "__main__":
    main()
