import pdfplumber
import json
import re

def identificar_tipo_e_extrair(texto_questao):
    # Procura por padrões de múltipla escolha: "A) ", "B) " ou "A " no início da linha
    if re.search(r'\n[A-E][\)\s\.]', texto_questao):
        return "multipla_escolha"
    return "certo_errado"

def extrair_inteligente(caminho_prova, caminho_gabarito, concurso_nome):
    questoes_final = []
    
    # 1. Extração do Gabarito (Mapeia número -> letra/correto)
    gabaritos = {}
    with pdfplumber.open(caminho_gabarito) as pdf:
        texto_gab = ""
        for page in pdf.pages: texto_gab += page.extract_text()
        
        # Padrão Cebraspe: "51 E", "52 C" etc.
        matches = re.findall(r'(\d+)\s+([CEABD])', texto_gab)
        for num, resp in matches:
            gabaritos[num] = resp.upper()

    # 2. Extração da Prova
    with pdfplumber.open(caminho_prova) as pdf:
        texto_completo = ""
        for page in pdf.pages: texto_completo += page.extract_text() + "\n"

    # 3. Divisão por questões (Tenta achar "Questão X" ou apenas o número no início da linha)
    blocos = re.split(r'\n(?=\d+[\.\s])', texto_completo)

    for bloco in blocos:
        # Pega o número da questão no início do bloco
        match_num = re.match(r'^(\d+)', bloco.strip())
        if not match_num: continue
        
        num_q = match_num.group(1)
        tipo = identificar_tipo_e_extrair(bloco)
        
        if num_q in gabaritos:
            gab = gabaritos[num_q]
            
            if tipo == "multipla_escolha":
                # Lógica de Múltipla Escolha (FGV/Vunesp/Cebraspe ABCDE)
                partes = re.split(r'\n[A-E][\)\s\.]', bloco)
                enunciado = partes[0].strip()
                opcoes = [p.strip() for p in partes[1:] if p.strip()]
                correta_idx = ord(gab) - 65 # A=0, B=1...
            else:
                # Lógica de Certo/Errado (Cebraspe)
                enunciado = bloco.strip()
                opcoes = ["Certo", "Errado"]
                correta_idx = 0 if gab == "C" else 1

            questoes_final.append({
                "id": int(num_q),
                "concurso": concurso_nome,
                "materia": "Geral (Ajustar manualmente)",
                "pergunta": enunciado,
                "opcoes": opcoes,
                "correta": correta_idx,
                "explicacao": f"Questão {num_q} extraída automaticamente."
            })

    return questoes_final

# Exemplo de uso:
# Para a prova SEFAZ-RJ (ABCDE)
# resultado = extrair_inteligente('49368.pdf', '49368 (1).pdf', 'SEFAZ-RJ')

# Para a prova ICMBio (Certo/Errado)
# resultado = extrair_inteligente('49337.pdf', '49337 (1).pdf', 'ICMBio')

# Salva o arquivo
# with open('src/data/questoes.json', 'w', encoding='utf-8') as f:
#     json.dump(resultado, f, indent=2, ensure_ascii=False)