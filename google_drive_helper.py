"""
Helper para converter links do Google Drive em links diretos de download
SEM NECESSIDADE DE API KEY - apenas links públicos!
"""

def convert_google_drive_link(share_link: str) -> str:
    """
    Converte link de compartilhamento do Google Drive em link direto de download
    
    Exemplo:
    Input:  https://drive.google.com/file/d/1ABC123XYZ/view?usp=sharing
    Output: https://drive.google.com/uc?export=download&id=1ABC123XYZ
    """
    
    # Extrai o ID do arquivo do link de compartilhamento
    if "/file/d/" in share_link:
        # Formato: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
        file_id = share_link.split("/file/d/")[1].split("/")[0]
    elif "id=" in share_link:
        # Formato alternativo: https://drive.google.com/open?id=FILE_ID
        file_id = share_link.split("id=")[1].split("&")[0]
    else:
        raise ValueError("Link do Google Drive inválido")
    
    # Cria o link direto de download
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    return direct_link


def batch_convert_google_drive_links(share_links: list) -> dict:
    """
    Converte múltiplos links do Google Drive de uma vez
    
    Entrada: Lista de links de compartilhamento
    Saída: Dicionário com links diretos
    """
    converted_links = {}
    
    for i, link in enumerate(share_links):
        try:
            direct_link = convert_google_drive_link(link)
            converted_links[f"arquivo_{i+1}"] = direct_link
            print(f"✅ Arquivo {i+1}: {direct_link}")
        except Exception as e:
            print(f"❌ Erro no arquivo {i+1}: {str(e)}")
            converted_links[f"arquivo_{i+1}"] = None
    
    return converted_links


# EXEMPLO DE USO:
"""
# Seus links de compartilhamento do Google Drive:
links_compartilhamento = [
    "https://drive.google.com/file/d/1ABC123/view?usp=sharing",
    "https://drive.google.com/file/d/1DEF456/view?usp=sharing", 
    "https://drive.google.com/file/d/1GHI789/view?usp=sharing"
]

# Converter para links diretos:
links_diretos = batch_convert_google_drive_links(links_compartilhamento)

# Resultado:
# arquivo_1: https://drive.google.com/uc?export=download&id=1ABC123
# arquivo_2: https://drive.google.com/uc?export=download&id=1DEF456
# arquivo_3: https://drive.google.com/uc?export=download&id=1GHI789
"""


if __name__ == "__main__":
    # Teste a conversão aqui:
    print("🔧 Testador de Links do Google Drive")
    print("Cole seus links de compartilhamento abaixo:")
    
    # Exemplo de teste
    exemplo_link = "https://drive.google.com/file/d/1ABC123XYZ/view?usp=sharing"
    resultado = convert_google_drive_link(exemplo_link)
    print(f"\n📤 Link original: {exemplo_link}")
    print(f"📥 Link direto: {resultado}") 