#!/usr/bin/env python3
"""
Sistema Avançado de Extração de PDF para Exercícios do ENEM
Integra PyMuPDF, detecção de layout estruturado e OCR com Tesseract
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json

# PDF processing libraries
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("⚠️ PyMuPDF não disponível. Instale com: pip install PyMuPDF")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("⚠️ pdfplumber não disponível. Instale com: pip install pdfplumber")

# OCR libraries
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR não disponível. Instale com: pip install pytesseract pillow")

# Fallback to basic PDF
from pypdf import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TextBlock:
    """Representa um bloco de texto extraído com informações de layout"""
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font_size: float
    font_name: str
    is_bold: bool = False
    is_italic: bool = False
    confidence: float = 1.0
    block_type: str = "text"  # text, title, question, alternative

@dataclass
class PageLayout:
    """Representa o layout estruturado de uma página"""
    page_number: int
    text_blocks: List[TextBlock]
    tables: List[Dict[str, Any]]
    images: List[Dict[str, Any]]
    columns: int
    is_scanned: bool = False
    ocr_quality: float = 1.0

class AdvancedPDFExtractor:
    """Extrator avançado de PDF com detecção de layout e OCR"""
    
    def __init__(self):
        self.use_pymupdf = PYMUPDF_AVAILABLE
        self.use_pdfplumber = PDFPLUMBER_AVAILABLE
        self.use_ocr = OCR_AVAILABLE
        
        # Configurações OCR
        self.tesseract_config = '--oem 3 --psm 6 -l por'
        
        # Padrões para identificação de tipos de bloco
        self.question_patterns = [
            r'QUESTÃO\s+\d+',
            r'^\d+\s*[\.\)]\s*',
            r'Questão\s+\d+'
        ]
        
        self.alternative_patterns = [
            r'^[A-E][\)\.\s]',
            r'^\([A-E]\)',
            r'^[A-E]\s+[A-Z]'
        ]
        
    def extract_from_pdf(self, pdf_path: Path) -> List[PageLayout]:
        """
        Extrai conteúdo estruturado de um PDF usando a melhor estratégia disponível
        """
        logger.info(f"🔍 Iniciando extração avançada de PDF: {pdf_path.name}")
        
        try:
            # Prioridade: PyMuPDF > pdfplumber > pypdf
            if self.use_pymupdf:
                return self._extract_with_pymupdf(pdf_path)
            elif self.use_pdfplumber:
                return self._extract_with_pdfplumber(pdf_path)
            else:
                return self._extract_with_pypdf_fallback(pdf_path)
                
        except Exception as e:
            logger.error(f"❌ Erro na extração de PDF: {e}")
            # Fallback para método básico
            return self._extract_with_pypdf_fallback(pdf_path)
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> List[PageLayout]:
        """Extração avançada usando PyMuPDF com detecção de layout"""
        logger.info("📖 Usando PyMuPDF para extração avançada")
        
        pages = []
        doc = fitz.open(str(pdf_path))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            logger.info(f"   📄 Processando página {page_num + 1}")
            
            # Verifica se a página é digitalizada
            is_scanned = self._is_scanned_page(page)
            
            if is_scanned and self.use_ocr:
                # Usa OCR para páginas digitalizadas
                page_layout = self._extract_with_ocr(page, page_num)
            else:
                # Extração direta do texto
                page_layout = self._extract_text_layout(page, page_num)
            
            # Detecta estrutura da página
            self._detect_page_structure(page_layout)
            
            pages.append(page_layout)
        
        doc.close()
        return pages
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> List[PageLayout]:
        """Extração usando pdfplumber com foco em tabelas e layout"""
        logger.info("📊 Usando pdfplumber para extração estruturada")
        
        pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                logger.info(f"   📄 Processando página {page_num + 1}")
                
                # Extrai texto com posições
                text_blocks = self._extract_pdfplumber_text(page)
                
                # Extrai tabelas
                tables = self._extract_pdfplumber_tables(page)
                
                # Cria layout da página
                page_layout = PageLayout(
                    page_number=page_num + 1,
                    text_blocks=text_blocks,
                    tables=tables,
                    images=[],
                    columns=self._detect_columns(text_blocks),
                    is_scanned=False
                )
                
                # Detecta estrutura
                self._detect_page_structure(page_layout)
                
                pages.append(page_layout)
        
        return pages
    
    def _extract_with_pypdf_fallback(self, pdf_path: Path) -> List[PageLayout]:
        """Método de fallback usando pypdf básico"""
        logger.info("📄 Usando pypdf como fallback")
        
        pages = []
        reader = PdfReader(str(pdf_path))
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            
            # Cria bloco de texto básico
            text_block = TextBlock(
                text=text,
                bbox=(0, 0, 100, 100),
                font_size=12.0,
                font_name="default",
                confidence=0.8
            )
            
            page_layout = PageLayout(
                page_number=page_num + 1,
                text_blocks=[text_block],
                tables=[],
                images=[],
                columns=1,
                is_scanned=False
            )
            
            pages.append(page_layout)
        
        return pages
    
    def _is_scanned_page(self, page) -> bool:
        """Detecta se uma página é digitalizada (imagem)"""
        try:
            # Verifica ratio de texto vs imagens
            text_dict = page.get_text("dict")
            text_length = sum(len(block.get("lines", [])) for block in text_dict.get("blocks", []))
            
            # Se há muito pouco texto estruturado, provavelmente é digitalizada
            image_list = page.get_images()
            has_large_images = len(image_list) > 0
            has_little_text = text_length < 10
            
            return has_large_images and has_little_text
            
        except Exception:
            return False
    
    def _extract_text_layout(self, page, page_num: int) -> PageLayout:
        """Extrai texto com informações de layout usando PyMuPDF"""
        text_blocks = []
        
        # Extrai blocos de texto com formatação
        blocks = page.get_text("dict")
        
        for block in blocks.get("blocks", []):
            if "lines" in block:  # Bloco de texto
                block_text = ""
                
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        block_text += span.get("text", "")
                
                if block_text.strip():
                    # Obtém informações de formatação do primeiro span
                    first_span = None
                    for line in block["lines"]:
                        if line.get("spans"):
                            first_span = line["spans"][0]
                            break
                    
                    if first_span:
                        text_block = TextBlock(
                            text=block_text.strip(),
                            bbox=(block["bbox"][0], block["bbox"][1], 
                                 block["bbox"][2], block["bbox"][3]),
                            font_size=first_span.get("size", 12.0),
                            font_name=first_span.get("font", "default"),
                            is_bold="Bold" in first_span.get("font", ""),
                            is_italic="Italic" in first_span.get("font", ""),
                            confidence=1.0
                        )
                        text_blocks.append(text_block)
        
        # Detecta colunas
        columns = self._detect_columns(text_blocks)
        
        return PageLayout(
            page_number=page_num + 1,
            text_blocks=text_blocks,
            tables=[],
            images=[],
            columns=columns,
            is_scanned=False
        )
    
    def _extract_with_ocr(self, page, page_num: int) -> PageLayout:
        """Extrai texto usando OCR para páginas digitalizadas"""
        logger.info(f"   🔍 Aplicando OCR na página {page_num + 1}")
        
        if not self.use_ocr:
            logger.warning("OCR não disponível, retornando página vazia")
            return PageLayout(page_num + 1, [], [], [], 1, True, 0.0)
        
        try:
            # Converte página para imagem
            mat = fitz.Matrix(2, 2)  # Zoom 2x para melhor qualidade
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Carrega imagem com PIL
            from io import BytesIO
            image = Image.open(BytesIO(img_data))
            
            # Pré-processamento da imagem
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Aplica OCR
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Converte dados OCR para blocos de texto
            text_blocks = self._convert_ocr_to_blocks(ocr_data)
            
            # Calcula qualidade do OCR
            ocr_quality = self._calculate_ocr_quality(ocr_data)
            
            return PageLayout(
                page_number=page_num + 1,
                text_blocks=text_blocks,
                tables=[],
                images=[],
                columns=self._detect_columns(text_blocks),
                is_scanned=True,
                ocr_quality=ocr_quality
            )
            
        except Exception as e:
            logger.error(f"Erro no OCR: {e}")
            return PageLayout(page_num + 1, [], [], [], 1, True, 0.0)
    
    def _preprocess_image_for_ocr(self, image) -> 'Image.Image':
        """Pré-processa imagem para melhorar qualidade do OCR"""
        
        if not OCR_AVAILABLE:
            return image
            
        try:
            # Converte para grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Aumenta contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Aumenta nitidez
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Remove ruído
            image = image.filter(ImageFilter.MedianFilter(size=3))
        except Exception:
            pass  # Retorna imagem original se houver erro
        
        return image
    
    def _convert_ocr_to_blocks(self, ocr_data: Dict) -> List[TextBlock]:
        """Converte dados do OCR em blocos de texto estruturados"""
        text_blocks = []
        
        # Agrupa palavras em linhas/blocos
        current_block = ""
        current_bbox = None
        current_conf = []
        
        for i, text in enumerate(ocr_data['text']):
            if text.strip():
                conf = int(ocr_data['conf'][i])
                if conf > 30:  # Filtro de confiança mínima
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    if current_block and self._should_merge_ocr_blocks(current_bbox, (x, y, x+w, y+h)):
                        # Mergeia com bloco atual
                        current_block += " " + text
                        current_bbox = self._merge_bboxes(current_bbox, (x, y, x+w, y+h))
                        current_conf.append(conf)
                    else:
                        # Finaliza bloco anterior se existir
                        if current_block:
                            avg_conf = sum(current_conf) / len(current_conf) / 100.0
                            text_blocks.append(TextBlock(
                                text=current_block.strip(),
                                bbox=current_bbox,
                                font_size=12.0,  # Estimativa
                                font_name="ocr",
                                confidence=avg_conf
                            ))
                        
                        # Inicia novo bloco
                        current_block = text
                        current_bbox = (x, y, x+w, y+h)
                        current_conf = [conf]
        
        # Finaliza último bloco
        if current_block:
            avg_conf = sum(current_conf) / len(current_conf) / 100.0
            text_blocks.append(TextBlock(
                text=current_block.strip(),
                bbox=current_bbox,
                font_size=12.0,
                font_name="ocr",
                confidence=avg_conf
            ))
        
        return text_blocks
    
    def _should_merge_ocr_blocks(self, bbox1: Tuple, bbox2: Tuple) -> bool:
        """Determina se dois blocos OCR devem ser unidos"""
        if not bbox1:
            return False
        
        # Calcula distância vertical
        y_dist = abs(bbox1[1] - bbox2[1])
        
        # Mergeia se estão na mesma linha (distância vertical pequena)
        return y_dist < 20
    
    def _merge_bboxes(self, bbox1: Tuple, bbox2: Tuple) -> Tuple:
        """Mergeia duas bounding boxes"""
        return (
            min(bbox1[0], bbox2[0]),  # x0
            min(bbox1[1], bbox2[1]),  # y0
            max(bbox1[2], bbox2[2]),  # x1
            max(bbox1[3], bbox2[3])   # y1
        )
    
    def _calculate_ocr_quality(self, ocr_data: Dict) -> float:
        """Calcula qualidade média do OCR"""
        confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences) / 100.0
    
    def _extract_pdfplumber_text(self, page) -> List[TextBlock]:
        """Extrai texto usando pdfplumber com informações de posição"""
        text_blocks = []
        
        # Extrai caracteres com posições
        chars = page.chars
        
        if not chars:
            return text_blocks
        
        # Agrupa caracteres em palavras e linhas
        current_word = ""
        current_bbox = None
        current_font_size = 12.0
        current_font_name = "default"
        
        for char in chars:
            if char['text'].strip():
                x0, y0, x1, y1 = char['x0'], char['top'], char['x1'], char['bottom']
                
                if current_bbox and self._chars_are_continuous(current_bbox, (x0, y0, x1, y1)):
                    # Continua palavra atual
                    current_word += char['text']
                    current_bbox = self._merge_bboxes(current_bbox, (x0, y0, x1, y1))
                else:
                    # Finaliza palavra anterior
                    if current_word.strip():
                        text_blocks.append(TextBlock(
                            text=current_word.strip(),
                            bbox=current_bbox,
                            font_size=current_font_size,
                            font_name=current_font_name,
                            confidence=1.0
                        ))
                    
                    # Inicia nova palavra
                    current_word = char['text']
                    current_bbox = (x0, y0, x1, y1)
                    current_font_size = char.get('size', 12.0)
                    current_font_name = char.get('fontname', 'default')
        
        # Finaliza última palavra
        if current_word.strip():
            text_blocks.append(TextBlock(
                text=current_word.strip(),
                bbox=current_bbox,
                font_size=current_font_size,
                font_name=current_font_name,
                confidence=1.0
            ))
        
        return text_blocks
    
    def _chars_are_continuous(self, bbox1: Tuple, bbox2: Tuple) -> bool:
        """Verifica se dois caracteres são contínuos"""
        # Distância horizontal pequena e mesma linha
        x_dist = abs(bbox1[2] - bbox2[0])
        y_overlap = min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1])
        
        return x_dist < 5 and y_overlap > 0
    
    def _extract_pdfplumber_tables(self, page) -> List[Dict[str, Any]]:
        """Extrai tabelas usando pdfplumber"""
        tables = []
        
        try:
            page_tables = page.find_tables()
            
            for i, table in enumerate(page_tables):
                table_data = table.extract()
                
                if table_data:
                    tables.append({
                        'id': i,
                        'bbox': table.bbox,
                        'data': table_data,
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0
                    })
        
        except Exception as e:
            logger.warning(f"Erro ao extrair tabelas: {e}")
        
        return tables
    
    def _detect_columns(self, text_blocks: List[TextBlock]) -> int:
        """Detecta número de colunas baseado na distribuição horizontal dos blocos"""
        if not text_blocks:
            return 1
        
        # Coleta posições x dos blocos
        x_positions = [block.bbox[0] for block in text_blocks if block.bbox]
        
        if not x_positions:
            return 1
        
        # Agrupa posições próximas
        x_positions.sort()
        clusters = []
        current_cluster = [x_positions[0]]
        
        for x in x_positions[1:]:
            if x - current_cluster[-1] < 50:  # Threshold para mesma coluna
                current_cluster.append(x)
            else:
                clusters.append(current_cluster)
                current_cluster = [x]
        
        clusters.append(current_cluster)
        
        return len(clusters)
    
    def _detect_page_structure(self, page_layout: PageLayout):
        """Detecta e classifica estrutura da página (questões, alternativas, etc.)"""
        import re
        
        for block in page_layout.text_blocks:
            text = block.text.strip()
            
            # Classifica tipo do bloco
            if any(re.search(pattern, text, re.IGNORECASE) for pattern in self.question_patterns):
                block.block_type = "question"
            elif any(re.search(pattern, text) for pattern in self.alternative_patterns):
                block.block_type = "alternative"
            elif block.font_size > 14 or block.is_bold:
                block.block_type = "title"
            else:
                block.block_type = "text"

    def get_structured_text(self, pages: List[PageLayout]) -> str:
        """Converte páginas estruturadas em texto organizado"""
        full_text = ""
        
        for page in pages:
            full_text += f"\n\n=== PÁGINA {page.page_number} ===\n"
            
            if page.is_scanned:
                full_text += f"[OCR - Qualidade: {page.ocr_quality:.1%}]\n"
            
            # Ordena blocos por posição (top-to-bottom, left-to-right)
            sorted_blocks = sorted(
                page.text_blocks, 
                key=lambda b: (b.bbox[1], b.bbox[0]) if b.bbox else (0, 0)
            )
            
            for block in sorted_blocks:
                if block.text.strip():
                    # Adiciona marcação baseada no tipo
                    prefix = ""
                    if block.block_type == "question":
                        prefix = "\n🔹 "
                    elif block.block_type == "alternative":
                        prefix = "\n   "
                    elif block.block_type == "title":
                        prefix = "\n📋 "
                    
                    confidence_indicator = ""
                    if block.confidence < 0.8:
                        confidence_indicator = f" [⚠️ {block.confidence:.1%}]"
                    
                    full_text += f"{prefix}{block.text}{confidence_indicator}\n"
            
            # Adiciona informações sobre tabelas
            if page.tables:
                full_text += f"\n📊 {len(page.tables)} tabela(s) detectada(s)\n"
        
        return full_text

# Função de conveniência para uso fácil
def extract_pdf_advanced(pdf_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Função principal para extração avançada de PDF
    Retorna: (texto_estruturado, estatísticas)
    """
    extractor = AdvancedPDFExtractor()
    pages = extractor.extract_from_pdf(pdf_path)
    
    structured_text = extractor.get_structured_text(pages)
    stats = {
        "total_pages": len(pages),
        "extraction_method": "PyMuPDF" if extractor.use_pymupdf else "pdfplumber" if extractor.use_pdfplumber else "pypdf",
        "ocr_enabled": extractor.use_ocr
    }
    
    return structured_text, stats
