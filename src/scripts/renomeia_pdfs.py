import os
import re
import pdfplumber

PASTA_PDFS = "pdfs"
CATEGORIA = "JUDICIARIO"

def normalizar(texto):
    return re.sub(r"\s+", " ", texto.upper())

def identificar_tipo(texto):
    if "GABARITO" in texto:
        return "GABARITO"
    if "PROVA OBJETIVA" in texto:
        return "PROVA"
    return "DESCONHECIDO"

def extrair_cargo(texto):
    padrao = re.search(
        r"(ASSISTENTE|ANALISTA|TÉCNICO|TECNICO|OFICIAL)[A-Z\s]{0,40}",
        texto
    )
    if padrao:
        cargo = padrao.group(0)
        cargo = re.sub(r"[^A-Z\s]", "", cargo)
        return cargo.strip().replace(" ", "-")
    return "CARGO-DESCONHECIDO"

def extrair_orgao(texto):
    if "TRIBUNAL DE JUSTIÇA DO ESTADO DE SÃO PAULO" in texto:
        return "TJSP"
    return "ORGAO"

def extrair_ano(texto):
    ano = re.search(r"(20\d{2})", texto)
    return ano.group(1) if ano else "ANO"

def processar_pdfs():
    for arquivo in os.listdir(PASTA_PDFS):
        if not arquivo.lower().endswith(".pdf"):
            continue

        caminho = os.path.join(PASTA_PDFS, arquivo)

        try:
            with pdfplumber.open(caminho) as pdf:
                texto = ""
                for i in range(min(2, len(pdf.pages))):
                    texto += pdf.pages[i].extract_text() or ""

            texto = normalizar(texto)

            tipo = identificar_tipo(texto)
            cargo = extrair_cargo(texto)
            orgao = extrair_orgao(texto)
            ano = extrair_ano(texto)

            novo_nome = f"{CATEGORIA}_{orgao}_{cargo}_{ano}_{tipo}.pdf"
            novo_caminho = os.path.join(PASTA_PDFS, novo_nome)

            if not os.path.exists(novo_caminho):
                os.rename(caminho, novo_caminho)
                print(f"✔ {arquivo} → {novo_nome}")
            else:
                print(f"⚠ Já existe: {novo_nome}")

        except Exception as e:
            print(f"❌ Erro em {arquivo}: {e}")

if __name__ == "__main__":
    processar_pdfs()
