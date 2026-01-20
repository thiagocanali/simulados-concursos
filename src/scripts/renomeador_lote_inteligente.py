# renomeador_lote_inteligente_final.py
import os
import re
import fitz  # PyMuPDF
from datetime import datetime

# Pasta onde estão os PDFs
PASTA_PDFS = "pdfs"

# Palavras-chave para identificar órgãos
ORGAOS = {
    "JUDICIARIO": ["judiciário", "tribunal", "TJ", "TRT", "STF", "STJ"],
    "POLICIAL": ["polícia", "civil", "militar", "pc", "pm"],
    "FISCAL": ["fiscal", "receita", "auditor"]
}

# Palavras-chave para identificar tipo
TIPOS = {
    "PROVA": ["prova"],
    "GABARITO": ["gabarito", "respostas"]
}

# Regex para detectar ano (4 dígitos entre 2000 e 2030)
REGEX_ANO = re.compile(r"(20[0-3][0-9])")

def extrair_texto_pdf(caminho_pdf):
    try:
        doc = fitz.open(caminho_pdf)
        texto = ""
        for pagina in doc:
            texto += pagina.get_text()
        return texto.lower()
    except Exception as e:
        print(f"[ERRO] Falha ao ler {caminho_pdf}: {e}")
        return ""

def identificar_orgao(texto):
    for orgao, palavras in ORGAOS.items():
        if any(palavra in texto for palavra in palavras):
            return orgao
    return "OUTRO_ORGAO_DESCONHECIDO"

def identificar_tipo(texto):
    for tipo, palavras in TIPOS.items():
        if any(palavra in texto for palavra in palavras):
            return tipo
    return "DESCONHECIDO"

def identificar_ano(texto):
    anos = REGEX_ANO.findall(texto)
    if anos:
        return max(anos)  # pega o ano mais recente encontrado
    else:
        return "ANO_DESCONHECIDO"

def gerar_nome_arquivo(caminho_pdf):
    texto = extrair_texto_pdf(caminho_pdf)
    orgao = identificar_orgao(texto)
    tipo = identificar_tipo(texto)
    ano = identificar_ano(texto)
    nome_final = f"{orgao}_ORGAO_DESCONHECIDO_{ano}_{tipo}.pdf"
    return nome_final

def renomear_pdfs():
    if not os.path.exists(PASTA_PDFS):
        print(f"[AVISO] Pasta '{PASTA_PDFS}' não encontrada.")
        return

    arquivos = [f for f in os.listdir(PASTA_PDFS) if f.lower().endswith(".pdf")]
    if not arquivos:
        print("[AVISO] Nenhum PDF encontrado na pasta.")
        return

    print(f"[DEBUG] Arquivos encontrados: {arquivos}")

    nomes_existentes = set()

    for arquivo in arquivos:
        caminho_antigo = os.path.join(PASTA_PDFS, arquivo)
        nome_novo_base = gerar_nome_arquivo(caminho_antigo)
        nome_novo = nome_novo_base
        contador = 1

        # Evita sobrescrever arquivos já existentes
        while nome_novo in nomes_existentes or os.path.exists(os.path.join(PASTA_PDFS, nome_novo)):
            nome_novo = nome_novo_base.replace(".pdf", f"({contador}).pdf")
            contador += 1

        nomes_existentes.add(nome_novo)
        caminho_novo = os.path.join(PASTA_PDFS, nome_novo)
        os.rename(caminho_antigo, caminho_novo)
        print(f"[OK] {arquivo} -> {nome_novo}")

if __name__ == "__main__":
    renomear_pdfs()
