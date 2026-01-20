import os
import json
import time
import requests
import sys
from dotenv import load_dotenv

# 1. Configuração de Encoding para Windows (Evita erro de caracteres)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# 2. Carregar variáveis de ambiente
caminho_env = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(caminho_env)
API_KEY = os.getenv('GEMINI_API_KEY')
JSON_PATH = os.path.join(os.path.dirname(__file__), '../data/questoes.json')

if not API_KEY:
    print("ERRO: Chave GEMINI_API_KEY nao encontrada no .env")
    exit()

# URL ajustada para a versao v1beta com o modelo flash-latest (mais resiliente)
URL_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def chamar_ia(prompt_texto):
    """Faz a requisicao direta via HTTP para evitar problemas com bibliotecas locais."""
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt_texto}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.7
        }
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(URL_API, json=payload, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        try:
            return dados['candidates'][0]['content']['parts'][0]['text'].strip()
        except (KeyError, IndexError):
            return "Erro ao processar resposta da IA."
    else:
        # Se der erro, ele retorna o status para o log
        return f"ERRO_API_{response.status_code}"

def processar():
    if not os.path.exists(JSON_PATH):
        print(f"Arquivo nao encontrado: {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        questoes = json.load(f)

    print(f"Iniciando: {len(questoes)} questoes encontradas.")

    for i, q in enumerate(questoes):
        explicacao_atual = q.get('explicacao', '')
        
        # Só processa se for placeholder ou estiver vazio
        if "oficial" in explicacao_atual or "Aguardando" in explicacao_atual or not explicacao_atual:
            print(f"Processando {i+1}/{len(questoes)} (ID: {q['id']})...", end=" ", flush=True)
            
            prompt = (
                f"Voce e um professor de concursos. Explique em no maximo 3 linhas "
                f"por que a alternativa de indice {q['correta']} e a correta para a questao: "
                f"{q['pergunta']}. Opcoes: {q['opcoes']}"
            )
            
            resultado = chamar_ia(prompt)
            
            if "ERRO_API" in resultado:
                print(f"Falhou ({resultado})")
                # Se for 404 de novo, vamos tentar um fallback no nome do modelo
                continue
            
            q['explicacao'] = resultado
            
            # Salva o progresso imediatamente no arquivo
            with open(JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(questoes, f, indent=2, ensure_ascii=False)
            
            print("OK!")
            
            # Pausa obrigatoria para evitar bloqueio na conta gratuita
            time.sleep(3)

    print("\n--- PROCESSO CONCLUIDO ---")

if __name__ == "__main__":
    processar()