import pdfplumber
import json
import re
import os

def extrair_gabarito_cebraspe(caminho_gab):
    respostas = {}
    if not os.path.exists(caminho_gab): return respostas
    try:
        with pdfplumber.open(caminho_gab) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() + " "
            
            # Busca padrões como "1 C", "2 E", "120 X"
            padrao = re.compile(r'(\d{1,3})\s+([CEX])')
            matches = padrao.findall(texto)
            for num, resp in matches:
                respostas[num] = resp
    except Exception as e:
        print(f"Erro no gabarito: {e}")
    return respostas

def processar_pasta_pdfs():
    banco_final = []
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    pasta_pdfs = os.path.join(caminho_script, 'pdfs')
    
    # Lista arquivos que são PROVAS (ignora os que têm "gabarito" no nome)
    provas = [f for f in os.listdir(pasta_pdfs) if f.endswith('.pdf') and 'gabarito' not in f.lower()]

    for nome_prova in provas:
        print(f"Processando prova: {nome_prova}")
        caminho_prova = os.path.join(pasta_pdfs, nome_prova)
        # Tenta achar o gabarito correspondente (mesmo nome + gabarito)
        caminho_gab = caminho_prova.replace('.pdf', '') + ' (1).pdf' 
        # Ou ajuste para procurar qualquer arquivo que contenha "gabarito"
        
        gabarito = extrair_gabarito_cebraspe(caminho_gab)
        if not gabarito:
            print(f"⚠️ Gabarito não encontrado para {nome_prova}")
            continue

        with pdfplumber.open(caminho_prova) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                if not texto: continue

                # Divide o texto por números seguidos de espaço (padrão Cebraspe)
                itens = re.split(r'\n(?=\d{1,3}\b)', texto)
                
                for item in itens:
                    match_num = re.match(r'^(\d{1,3})\b', item.strip())
                    if match_num:
                        num = match_num.group(1)
                        if num in gabarito and gabarito[num] != 'X': # 'X' é anulada
                            pergunta = item.strip().replace('\n', ' ')
                            banco_final.append({
                                "id": f"{nome_prova}_{num}",
                                "concurso": nome_prova.split('-')[0].upper(), # Ex: PF ou PRF
                                "materia": "Conhecimentos Específicos",
                                "pergunta": pergunta,
                                "opcoes": ["Certo", "Errado"],
                                "correta": 0 if gabarito[num] == 'C' else 1,
                                "ano": "2021"
                            })

    # Salva na pasta data do seu projeto Vue
    caminho_json = os.path.join(caminho_script, '..', 'src', 'data', 'questoes.json')
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(banco_final, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sucesso! {len(banco_final)} questões geradas em {caminho_json}")

if __name__ == "__main__":
    processar_pasta_pdfs()