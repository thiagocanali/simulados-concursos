import json
import re

def converter_para_json(arquivo_entrada, arquivo_saida):
    questoes = []
    
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Este padrão busca: Pergunta, Opções (A, B, C, D, E) e Gabarito
    # Ajustado para capturar o formato comum de provas
    blocos = re.split(r'\n(?=\d+\.)', conteudo)

    for i, bloco in enumerate(blocos):
        if not bloco.strip(): continue
        
        try:
            # Extrai a pergunta (tudo até a letra A)
            partes = re.split(r'\n[a-eA-E]\)', bloco)
            pergunta = re.sub(r'^\d+\.\s*', '', partes[0]).strip()
            
            # Extrai as opções
            opcoes = [opt.strip() for opt in partes[1:]]
            
            # Tenta achar o gabarito (ex: GABARITO: C)
            gabarito_match = re.search(r'GABARITO:\s*([A-E])', bloco, re.IGNORECASE)
            correta_index = ord(gabarito_match.group(1).upper()) - 65 if gabarito_match else 0
            
            questoes.append({
                "id": 200 + i,
                "concurso": "Importado",
                "materia": "Geral",
                "pergunta": pergunta,
                "opcoes": opcoes[:5], # Garante no máximo 5
                "correta": correta_index,
                "explicacao": "Questão importada automaticamente via script."
            })
        except Exception as e:
            print(f"Erro ao processar questão {i}: {e}")

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(questoes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sucesso! {len(questoes)} questões geradas em {arquivo_saida}")

# Execução
if __name__ == "__main__":
    # Nome do arquivo de texto que você criou
    converter_para_json('questoes_brutas.txt', 'src/data/questoes_novas.json')