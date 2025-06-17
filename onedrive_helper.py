"""
Helper para converter links do OneDrive em links diretos de download
"""

def convert_onedrive_link(share_link: str) -> str:
    """
    Converte link de compartilhamento do OneDrive em link direto de download
    
    Exemplo:
    Input: https://1drv.ms/f/s!Abc123...
    Output: https://api.onedrive.com/v1.0/shares/{encoded}/root/content
    """
    import base64
    import urllib.parse
    
    # Codifica o link em base64
    encoded_link = base64.b64encode(share_link.encode()).decode()
    
    # Remove padding do base64 e substitui caracteres
    encoded_link = encoded_link.rstrip('=').replace('/', '_').replace('+', '-')
    
    # Cria o link direto
    direct_link = f"https://api.onedrive.com/v1.0/shares/u!{encoded_link}/root/content"
    
    return direct_link


# EXEMPLOS DE USO:
"""
1. Compartilhe sua pasta no OneDrive
2. Copie o link de compartilhamento
3. Use a função acima para converter

Exemplo:
share_link = "https://1drv.ms/f/s!Abc123..."
direct_link = convert_onedrive_link(share_link)
print(direct_link)
"""

# Para arquivos individuais no OneDrive:
def get_onedrive_direct_link(file_share_link: str) -> str:
    """
    Para links diretos de arquivos individuais no OneDrive
    Substitua 'redir' por 'download' no link
    """
    if "1drv.ms" in file_share_link:
        # Para links curtos do OneDrive
        return file_share_link.replace("1drv.ms", "download.1drv.ms")
    
    if "onedrive.live.com" in file_share_link:
        # Para links longos do OneDrive
        return file_share_link.replace("redir", "download")
    
    return file_share_link 