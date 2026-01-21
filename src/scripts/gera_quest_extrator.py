import pdfplumber
import json
import re
import os

def extrair_gabarito(caminho_gab):
    respostas = {}
    if not os.path.exists(caminho_gab): return respostas
    try:
        with pdfplumber.open(caminho_gab) as pdf:
            texto = " ".join([p.extract_text() or "" for p in pdf.pages])
            tokens = re.sub(r'[",\r\n\t]', ' ', texto).split()
            nums, letras = [], []
            for t in tokens:
                t = t.strip().upper()
                if t.isdigit(): nums.append(t)
                elif t in ['A', 'B', 'C', 'D', 'E']: letras.append(t)
            for i in range(min(len(nums), len(letras))):
                respostas[nums[i]] = letras[i]
    except: pass
    return respostas

def processar_prova(caminho_pdf, caminho_gab):
    gabarito = extrair_gabarito(caminho_gab)
    if not gabarito: return []
    
    questoes = []
    id_prova = os.path.basename(caminho_pdf).replace('.pdf', '')

    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()
            if not texto: continue
            # Divide por padrões de questão (ex: Questão 01 ou 1 A) )
            blocos = re.split(r'\n(?=Questão\s+\d+|\d+\s+[A-Z]|\b\d{1,3}\b\s)', texto)
            for bloco in blocos:
                num_match = re.search(r'\b(\d{1,3})\b', bloco)
                if num_match and num_match.group(1) in gabarito:
                    num = num_match.group(1)
                    # Lógica simples de matéria: se tiver "Art." ou "Trânsito", marca como Trânsito
                    materia = "Conhecimentos Gerais"
                    if any(word in bloco.lower() for word in ["art.", "ctb", "veículo", "trânsito"]): materia = "Legislação de Trânsito"
                    elif any(word in bloco.lower() for word in ["vírgula", "texto", "concordância"]): materia = "Português"

                    questoes.append({
                        "id": f"{id_prova}_{num}",
                        "prova": id_prova,
                        "materia": materia,
                        "pergunta": bloco.split('A)')[0].strip(),
                        "opcoes": re.findall(r'[A-E]\)\s*(.*?)(?=[A-E]\)|$)', bloco.replace('\n', ' ')),
                        "correta": ord(gabarito[num]) - 65
                    })
    return questoes

if __name__ == "__main__":
    banco = []
    pasta = os.path.dirname(os.path.abspath(__file__))
    arquivos = [f for f in os.listdir(pasta) if f.endswith('.pdf') and '(1)' not in f]
    for f in arquivos:
        print(f"Lendo {f}...")
        banco.extend(processar_prova(os.path.join(pasta, f), os.path.join(pasta, f.replace('.pdf', ' (1).pdf'))))
    
    with open(os.path.join(pasta, '..', 'data', 'questoes.json'), 'w', encoding='utf-8') as f:
        json.dump(banco, f, indent=2, ensure_ascii=False)
    print(f"Sucesso! {len(banco)} questões extraídas.")