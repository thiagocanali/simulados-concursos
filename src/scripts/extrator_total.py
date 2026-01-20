import pdfplumber
import json
import re
import os

def extrair_gabarito_sequencial(caminho_gab):
    respostas = {}
    if not os.path.exists(caminho_gab): return respostas
    with pdfplumber.open(caminho_gab) as pdf:
        texto = " ".join([p.extract_text() for p in pdf.pages])
        texto = re.sub(r'[",\r\n\t]', ' ', texto)
        tokens = texto.split()
        nums, letras = [], []
        for t in tokens:
            t = t.strip().upper()
            if t.isdigit() and 1 <= int(t) <= 150: nums.append(t)
            elif t in ['A', 'B', 'C', 'D', 'E']: letras.append(t)
        for i in range(min(len(nums), len(letras))):
            respostas[nums[i]] = letras[i]
    return respostas

def processar_prova_profissional(caminho_pdf, caminho_gab, concurso, materia):
    gabarito = extrair_gabarito_sequencial(caminho_gab)
    if not gabarito: return []
    
    questoes = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            # Divisão por colunas para evitar mistura de texto
            meio = page.width / 2
            colunas = [
                page.within_bbox((0, 40, meio, page.height - 40)),
                page.within_bbox((meio, 40, page.width, page.height - 40))
            ]
            
            for col in colunas:
                texto = col.extract_text()
                if not texto: continue
                
                # Split por Questão
                blocos = re.split(r'\n(?=Questão\s+\d+|\d+\s+[A-Z]|\b\d{1,3}\b\s)', texto)

                for bloco in blocos:
                    match_num = re.search(r'\b(\d{1,3})\b', bloco)
                    if not match_num: continue
                    
                    num_q = match_num.group(1)
                    if num_q in gabarito:
                        letra_gab = gabarito[num_q]
                        
                        # Limpeza do texto da pergunta
                        pergunta_bruta = re.sub(rf'^(Questão\s+)?{num_q}\s*', '', bloco, flags=re.IGNORECASE).strip()
                        pergunta_limpa = re.sub(r'(?i)Espaço\s+livre.*|Rascunho.*', '', pergunta_bruta).replace('\n', ' ')

                        # Lógica de alternativas
                        if re.search(r'\s([A-E])[\)\s]', pergunta_limpa):
                            partes = re.split(r'\s[A-E][\)\s]', pergunta_limpa)
                            enunciado = partes[0].strip()
                            opcoes = [p.strip() for p in partes[1:] if p.strip()]
                            correta_idx = ord(letra_gab) - 65
                        else:
                            enunciado = pergunta_limpa
                            opcoes = ["Certo", "Errado"]
                            correta_idx = 0 if letra_gab == 'C' else 1

                        # NOVA ESTRUTURA CONFORME SEU PEDIDO
                        # ... (dentro do seu loop de questões no extrator_total.py)
                        questoes.append({
                            "id": int(num_q) + (5000 if "SEFAZ" in concurso else 6000),
                            "concurso": concurso,
                            "materia": materia,
                            "pergunta": enunciado,
                            "opcoes": opcoes[:5],
                            "correta": correta_idx,
                            "fonte": f"Questão {num_q} oficial {concurso}.", # Nome da prova
                            "explicacao": "[Aguardando explicação detalhada via IA...]" # Placeholder para o outro script preencher
                        })
    return questoes

if __name__ == "__main__":
    banco_final = []
    config = [
        ('49368.pdf', '49368 (1).pdf', 'SEFAZ-RJ', 'Administração Pública'),
        ('49337.pdf', '49337 (1).pdf', 'ICMBio', 'Conhecimentos Específicos')
    ]
    
    for prova, gab, nome, mat in config:
        if os.path.exists(prova):
            print(f"Processando {nome}...")
            banco_final.extend(processar_prova_profissional(prova, gab, nome, mat))

    dir_script = os.path.dirname(os.path.abspath(__file__))
    caminho_final = os.path.join(dir_script, '..', 'data', 'questoes.json')
    
    with open(caminho_final, 'w', encoding='utf-8') as f:
        json.dump(banco_final, f, indent=2, ensure_ascii=False)
        
    print(f"\nSucesso! {len(banco_final)} questões salvas em: {caminho_final}")