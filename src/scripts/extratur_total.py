import os
import json
import pdfplumber # Certifique-se de ter instalado: pip install pdfplumber
import re

def extrair_dados_pdf(caminho_pdf):
    questoes_do_pdf = []
    # Aqui vai a lógica de extração que você já estava usando
    # Vou colocar um exemplo base que busca Pergunta e Opções
    with pdfplumber.open(caminho_pdf) as pdf:
        texto_completo = ""
        for pagina in pdf.pages:
            texto_completo += pagina.extract_text()
            
        # Exemplo de busca simples (ajuste conforme o padrão das suas provas)
        # Esta parte depende de como o texto aparece no seu PDF
        blocos = texto_completo.split('Questão') 
        
        for bloco in blocos[1:]:
            try:
                # Lógica simplificada para estruturar os dados
                questao = {
                    "id": len(questoes_do_pdf) + 5000, # ID incremental
                    "materia": "Geral",
                    "pergunta": bloco.split('\n')[0].strip(),
                    "opcoes": ["A", "B", "C", "D"], # Placeholder
                    "correta": 0,
                    "explicacao": "Explicação disponível em breve."
                }
                questoes_do_pdf.append(questao)
            except:
                continue
                
    return questoes_do_pdf

def processar_tudo():
    pasta_scripts = os.path.dirname(__file__)
    lista_final = []
    
    # Lista todos os arquivos na pasta que terminam com .pdf
    arquivos = [f for f in os.listdir(pasta_scripts) if f.endswith('.pdf')]
    
    print(f"Encontrados {len(arquivos)} arquivos PDF. Iniciando extração...")

    for arquivo in arquivos:
        caminho_completo = os.path.join(pasta_scripts, arquivo)
        print(f"Processando: {arquivo}")
        
        try:
            dados = extrair_dados_pdf(caminho_completo)
            lista_final.extend(dados)
        except Exception as e:
            print(f"Erro ao processar {arquivo}: {e}")

    # Salva o arquivo gigante
    caminho_saida = os.path.join(pasta_scripts, '../data/questoes.json')
    
    # Garante que a pasta data existe
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, indent=2, ensure_ascii=False)

    print(f"--- FIM ---")
    print(f"Total de questões extraídas: {len(lista_final)}")
    print(f"Arquivo salvo em: {caminho_saida}")

if __name__ == "__main__":
    processar_tudo()