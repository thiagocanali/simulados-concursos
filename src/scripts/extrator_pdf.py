import pdfplumber
import json
import re

def extrair_dados_pdf(caminho_prova, caminho_gabarito):
    questoes_final = []
    
    # 1. Extrair Texto da Prova
    texto_prova = ""
    with pdfplumber.open(caminho_prova) as pdf:
        for pagina in pdf.pages:
            texto_prova += pagina.extract_text() + "\n"

    # 2. Extrair Gabarito (Lógica para PDFs do Cebraspe/FGV)
    gabaritos = {}
    with pdfplumber.open(caminho_gabarito) as pdf:
        texto_gab = ""
        for pagina in pdf.pages:
            texto_gab += pagina.extract_text()
        
        # Busca padrões como "Questão 1 C" ou tabelas de gabarito
        matches = re.findall(r'(\d+)\s+([A-E])', texto_gab)
        for num, letra in matches:
            gabaritos[num] = letra

    # 3. Parsear Questões (Regex para separar por "Questão X")
    blocos = re.split(r'Questão\s+(\d+)', texto_prova)
    
    for i in range(1, len(blocos), 2):
        num_q = blocos[i]
        conteudo = blocos[i+1]
        
        # Separar enunciado das opções
        partes_opcoes = re.split(r'\n([A-E])\s', conteudo)
        enunciado = partes_opcoes[0].strip()
        opcoes = [partes_opcoes[j].strip() for j in range(2, len(partes_opcoes), 2)]

        if len(opcoes) >= 4: # Garante que é uma questão completa
            letra_correta = gabaritos.get(num_q, "A")
            idx_correto = ord(letra_correta.upper()) - 65
            
            questoes_final.append({
                "id": int(num_q),
                "concurso": "SEFAZ-RJ 2025", # Exemplo dinâmico
                "materia": "Administração Pública",
                "pergunta": enunciado,
                "opcoes": opcoes[:5],
                "correta": idx_correto,
                "explicacao": f"Questão {num_q} extraída do caderno oficial."
            })

    return questoes_final

# Execução
dados = extrair_dados_pdf('49368.pdf', '49368 (1).pdf')
with open('src/data/questoes_extraidas.json', 'w', encoding='utf-8') as f:
    json.dump(dados, f, indent=2, ensure_ascii=False)

print(f"Processadas {len(dados)} questões!")