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
    except Exception:
        pass
    return respostas

def processar_prova_profissional(caminho_pdf, caminho_gab):
    try:
        gabarito = extrair_gabarito_sequencial(caminho_gab)
        if not gabarito: 
            print(f"   [Aviso] Gabarito nao encontrado ou vazio para: {caminho_pdf}")
            return []
        
        # Extrai os primeiros 5 digitos do nome do arquivo para o ID
        nome_arquivo = os.path.basename(caminho_pdf)
        codigo_prova = re.sub(r'\D', '', nome_arquivo)[:5]
        questoes = []
        
        with pdfplumber.open(caminho_pdf) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    meio = page.width / 2
                    # Define as colunas (esquerda e direita)
                    colunas = [
                        page.within_bbox((0, 40, meio, page.height - 40)),
                        page.within_bbox((meio, 40, page.width, page.height - 40))
                    ]
                    
                    for col in colunas:
                        texto = col.extract_text()
                        if not texto: continue
                        
                        # Split por Questão ou número isolado no início da linha
                        blocos = re.split(r'\n(?=Questão\s+\d+|\d+\s+[A-Z]|\b\d{1,3}\b\s)', texto)

                        for bloco in blocos:
                            match_num = re.search(r'\b(\d{1,3})\b', bloco)
                            if not match_num: continue
                            
                            num_q = match_num.group(1)
                            if num_q in gabarito:
                                letra_gab = gabarito[num_q]
                                
                                # Limpeza do enunciado
                                pergunta_bruta = re.sub(rf'^(Questão\s+)?{num_q}\s*', '', bloco, flags=re.IGNORECASE).strip()
                                pergunta_limpa = re.sub(r'(?i)Espaço\s+livre.*|Rascunho.*', '', pergunta_bruta).replace('\n', ' ')

                                # Diferencia Multipla Escolha de Certo/Errado
                                if re.search(r'\s([A-E])[\)\s]', pergunta_limpa):
                                    partes = re.split(r'\s[A-E][\)\s]', pergunta_limpa)
                                    enunciado = partes[0].strip()
                                    opcoes = [p.strip() for p in partes[1:] if p.strip()]
                                    correta_idx = ord(letra_gab) - 65
                                else:
                                    enunciado = pergunta_limpa
                                    opcoes = ["Certo", "Errado"]
                                    correta_idx = 0 if letra_gab == 'C' else 1

                                questoes.append({
                                    "id": int(num_q) + (int(codigo_prova) * 100),
                                    "concurso": "Simulado Geral",
                                    "materia": "Conhecimentos Gerais",
                                    "pergunta": enunciado,
                                    "opcoes": opcoes[:5],
                                    "correta": correta_idx,
                                    "fonte": f"Prova {codigo_prova} - Questão {num_q}",
                                    "explicacao": "" 
                                })
                except Exception as e_page:
                    print(f"   [Aviso] Pulei a pagina {i+1} de {nome_arquivo} devido a erro de leitura.")
                    continue

        return questoes

    except Exception as e_file:
        print(f"   [Erro Critico] Falha ao processar o arquivo {caminho_pdf}: {e_file}")
        return []

if __name__ == "__main__":
    banco_final = []
    dir_scripts = os.path.dirname(os.path.abspath(__file__))
    
    # Filtra arquivos: apenas os que nao possuem "(1)" (as provas)
    arquivos_prova = [f for f in os.listdir(dir_scripts) if f.endswith('.pdf') and '(1)' not in f]
    
    print(f"--- Iniciando Extracao de {len(arquivos_prova)} Provas ---")

    for prova in arquivos_prova:
        gabarito = prova.replace('.pdf', ' (1).pdf')
        caminho_prova = os.path.join(dir_scripts, prova)
        caminho_gab = os.path.join(dir_scripts, gabarito)
        
        print(f"Processando: {prova}...")
        novas_questoes = processar_prova_profissional(caminho_prova, caminho_gab)
        
        if novas_questoes:
            banco_final.extend(novas_questoes)
            print(f"   -> Sucesso: {len(novas_questoes)} questoes.")
        else:
            print(f"   -> Falha: Nenhuma questao extraida.")

    # Salvamento final
    caminho_final = os.path.join(dir_scripts, '..', 'data', 'questoes.json')
    os.makedirs(os.path.dirname(caminho_final), exist_ok=True)
    
    with open(caminho_final, 'w', encoding='utf-8') as f:
        json.dump(banco_final, f, indent=2, ensure_ascii=False)
        
    print(f"\n==========================================")
    print(f"CONCLUIDO: {len(banco_final)} questoes salvas.")
    print(f"Arquivo: {os.path.abspath(caminho_final)}")
    print(f"==========================================")