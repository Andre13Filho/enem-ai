import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

HISTORICO_PATH = "conversas.json"

def carregar_historico() -> List[Dict[str, Any]]:
    try:
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def salvar_historico(historico: List[Dict[str, Any]]):
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def adicionar_conversa(titulo: str, materia: str, mensagens: List[Dict[str, str]]):
    historico = carregar_historico()
    nova = {
        "id": str(uuid.uuid4()),
        "titulo": titulo,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "materia": materia,
        "mensagens": mensagens
    }
    historico.insert(0, nova)
    salvar_historico(historico)
    return nova["id"]

def apagar_conversa(conversa_id: str):
    historico = carregar_historico()
    historico = [c for c in historico if c["id"] != conversa_id]
    salvar_historico(historico)

def atualizar_conversa(conversa_id: str, mensagens: List[Dict[str, str]]):
    historico = carregar_historico()
    for c in historico:
        if c["id"] == conversa_id:
            c["mensagens"] = mensagens
            c["data"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    salvar_historico(historico)

def obter_conversa(conversa_id: str) -> Dict[str, Any]:
    historico = carregar_historico()
    for c in historico:
        if c["id"] == conversa_id:
            return c
    return None 