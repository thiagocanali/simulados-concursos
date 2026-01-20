import pdfplumber
import json
import re
import os

def extrair_gabarito_sequencial(caminho_gab):
    respostas = {}
    if not os.path.exists(caminho_gab): return respostas
    try:
        with pdfplumber.open(caminho_gab) as pdf:
            texto = " ".join([p.extract_text() or "" for p in pdf.pages])
            texto = re.sub(r'[",\r\n\t]', ' ', texto)
            tokens = texto.split()
            nums, letras = [], []
            for t in tokens:
                t = t.strip().upper()
                if t.isdigit() and 1 <= int(t) <= 150: nums.append(t)
                elif t in ['A', 'B', 'C', 'D', 'E']: letras.append(t)
            for i in range(min(len(nums), len(letras))):
                respostas[nums[i]] = letras[i]
    except: pass
    return respostas

def processar_prova_profissional(caminho_pdf, caminho_gab):
    try:
        gabarito = extrair_gabarito_sequencial(caminho_gab)
        if not gabarito: return []
        nome_arquivo = os.path.basename(caminho_pdf)
        id_concurso = nome_arquivo.replace('.pdf', '') 
        questoes = []
        with pdfplumber.open(caminho_pdf) as pdf:
            for page in pdf.pages:
                try:
                    meio = page.width / 2
                    colunas = [page.within_bbox((0, 40, meio, page.height - 40)),
                               page.within_bbox((meio, 40, page.width, page.height - 40))]
                    for col in colunas:
                        texto = col.extract_text()
                        if not texto: continue
                        blocos = re.split(r'\n(?=Questão\s+\d+|\d+\s+[A-Z]|\b\d{1,3}\b\s)', texto)
                        for bloco in blocos:
                            match_num = re.search(r'\b(\d{1,3})\b', bloco)
                            if not match_num: continue
                            num_q = match_num.group(1)
                            if num_q in gabarito:
                                letra_gab = gabarito[num_q]
                                p_limpa = re.sub(rf'^(Questão\s+)?{num_q}\s*', '', bloco, flags=re.IGNORECASE).strip()
                                p_limpa = re.sub(r'(?i)Espaço\s+livre.*|Rascunho.*', '', p_limpa).replace('\n', ' ')
                                if re.search(r'\s([A-E])[\)\s]', p_limpa):
                                    partes = re.split(r'\s[A-E][\)\s]', p_limpa)
                                    enunciado, opcoes = partes[0].strip(), [p.strip() for p in partes[1:] if p.strip()]
                                    correta_idx = ord(letra_gab) - 65
                                else:
                                    enunciado, opcoes = p_limpa, ["Certo", "Errado"]
                                    correta_idx = 0 if letra_gab == 'C' else 1
                                questoes.append({
                                    "id": int(num_q) + (int(re.sub(r'\D', '', id_concurso)[:5]) * 100),
                                    "concurso": id_concurso,
                                    "materia": "Conhecimentos Gerais",
                                    "pergunta": enunciado,
                                    "opcoes": opcoes[:5],
                                    "correta": correta_idx,
                                    "fonte": f"Prova {id_concurso} - Q{num_q}",
                                    "explicacao": "" 
                                })
                except: continue
        return questoes
    except: return []

if __name__ == "__main__":
    banco_final = []
    dir_s = os.path.dirname(os.path.abspath(__file__))
    arquivos = [f for f in os.listdir(dir_s) if f.endswith('.pdf') and '(1)' not in f]
    for prova in arquivos:
        print(f"Processando: {prova}...")
        banco_final.extend(processar_prova_profissional(os.path.join(dir_s, prova), os.path.join(dir_s, prova.replace('.pdf', ' (1).pdf'))))
    with open(os.path.join(dir_s, '..', 'data', 'questoes.json'), 'w', encoding='utf-8') as f:
        json.dump(banco_final, f, indent=2, ensure_ascii=False)
    print(f"Sucesso: {len(banco_final)} questoes salvas.")