<script setup>
import { ref, computed } from 'vue'
import questoesRaw from './data/questoes.json'

// Estados
const concursoSelecionado = ref(null)
const questaoAtualIndex = ref(0)
const questaoRespondida = ref(false)
const opcaoEscolhida = ref(null)
const acertos = ref(0)
const simuladoIniciado = ref(false)
const simuladoFinalizado = ref(false)
const listaDeQuestoes = ref([])

const categorias = {
  "🔥 Mais Visados": ["CNU", "Correios", "Banco do Brasil", "Caixa", "INSS", "PF", "PRF", "Receita Federal"],
  "⚖️ Tribunais": ["TJ", "TRT", "TRF", "TSE/TRE"],
  "🏛️ Outros": ["IBGE", "Prefeituras", "Militares"]
}

const iniciarSimulado = (concurso) => {
  const filtradas = questoesRaw.filter(q => q.concurso === concurso)
  
  if (filtradas.length === 0) {
    alert("Em breve teremos questões para " + concurso);
    return;
  }

  // Embaralha as questões do concurso escolhido
  listaDeQuestoes.value = [...filtradas].sort(() => Math.random() - 0.5).slice(0, 10)
  
  concursoSelecionado.value = concurso
  simuladoIniciado.value = true
  simuladoFinalizado.value = false
  questaoAtualIndex.value = 0
  acertos.value = 0
  questaoRespondida.value = false
}

const questaoAtual = computed(() => listaDeQuestoes.value[questaoAtualIndex.value])

const responder = (index) => {
  if (questaoRespondida.value) return
  opcaoEscolhida.value = index
  questaoRespondida.value = true
  if (index === questaoAtual.value.correta) acertos.value++
}

const proximaQuestao = () => {
  if (questaoAtualIndex.value + 1 < listaDeQuestoes.value.length) {
    questaoAtualIndex.value++
    questaoRespondida.value = false
    opcaoEscolhida.value = null
  } else {
    simuladoFinalizado.value = true
  }
}

const reiniciar = () => {
  simuladoIniciado.value = false
  simuladoFinalizado.value = false
}
</script>

<template>
  <div class="container">
    <header class="main-header">
      <h1 @click="reiniciar" style="cursor:pointer">🚀 Simulados Brasil</h1>
      <p v-if="!simuladoIniciado">Escolha um concurso para começar a treinar</p>
    </header>

    <main v-if="!simuladoIniciado">
      <div v-for="(lista, cat) in categorias" :key="cat" class="categoria-group">
        <h3>{{ cat }}</h3>
        <div class="grid-botoes">
          <button v-for="c in lista" :key="c" @click="iniciarSimulado(c)" class="btn-concurso">
            {{ c }}
          </button>
        </div>
      </div>
    </main>

    <main v-else-if="!simuladoFinalizado && questaoAtual">
      <div class="status-bar">
        <span>Concurso: <strong>{{ concursoSelecionado }}</strong></span>
        <span>Questão {{ questaoAtualIndex + 1 }} de {{ listaDeQuestoes.length }}</span>
      </div>

      <div class="card-questao">
        <p class="pergunta">{{ questaoAtual.pergunta }}</p>

        <div class="opcoes">
          <button 
            v-for="(opcao, i) in questaoAtual.opcoes" :key="i"
            @click="responder(i)"
            :class="['btn-opcao', {
              'correta': questaoRespondida && i === questaoAtual.correta,
              'errada': questaoRespondida && opcaoEscolhida === i && i !== questaoAtual.correta,
              'desativado': questaoRespondida && opcaoEscolhida !== i
            }]"
          >
            <span class="letra">{{ String.fromCharCode(65 + i) }}</span> {{ opcao }}
          </button>
        </div>

        <transition name="fade">
          <div v-if="questaoRespondida" class="feedback">
            <div :class="['alerta', opcaoEscolhida === questaoAtual.correta ? 'sucesso' : 'erro']">
              {{ opcaoEscolhida === questaoAtual.correta ? '✅ Você acertou!' : '❌ Você errou.' }}
            </div>
            
            <div class="explicacao">
              <strong>💡 Explicação:</strong>
              <p>{{ questaoAtual.explicacao }}</p>
            </div>

            <button @click="proximaQuestao" class="btn-proxima">
              {{ questaoAtualIndex + 1 === listaDeQuestoes.length ? 'Ver Resultado' : 'Próxima Questão' }}
            </button>
          </div>
        </transition>
      </div>
    </main>

    <main v-else class="resultado">
      <h2>Simulado Concluído!</h2>
      <div class="score">
        <span class="grande">{{ acertos }}</span> / {{ listaDeQuestoes.length }}
        <p>acertos</p>
      </div>
      <button @click="reiniciar" class="btn-proxima">Voltar ao Início</button>
    </main>
  </div>
</template>

<style>
/* Estilos globais e scaneáveis */
:root { --primary: #007bff; --success: #28a745; --danger: #dc3545; --bg: #f8f9fa; }
body { background-color: var(--bg); color: #333; margin: 0; }
.container { max-width: 700px; margin: 0 auto; padding: 20px; }
.main-header { text-align: center; margin-bottom: 30px; }
.grid-botoes { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 10px; margin-bottom: 20px; }

.btn-concurso { background: white; border: 1px solid #ddd; padding: 12px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; }
.btn-concurso:hover { border-color: var(--primary); color: var(--primary); background: #f0f7ff; }

.card-questao { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.pergunta { font-size: 1.2rem; font-weight: 600; margin-bottom: 20px; line-height: 1.4; }

.opcoes { display: flex; flex-direction: column; gap: 10px; }
.btn-opcao { text-align: left; padding: 15px; border: 2px solid #eee; border-radius: 10px; background: white; cursor: pointer; display: flex; align-items: center; gap: 10px; }
.letra { background: #eee; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 0.8rem; font-weight: bold; }

.correta { border-color: var(--success); background: #e8f5e9; }
.correta .letra { background: var(--success); color: white; }
.errada { border-color: var(--danger); background: #ffebee; }
.errada .letra { background: var(--danger); color: white; }

.feedback { margin-top: 20px; border-top: 1px solid #eee; padding-top: 20px; }
.alerta { padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 10px; }
.sucesso { background: #d4edda; color: #155724; }
.erro { background: #f8d7da; color: #721c24; }
.explicacao { background: #f1f3f5; padding: 15px; border-radius: 8px; font-size: 0.95rem; line-height: 1.5; }

.btn-proxima { width: 100%; margin-top: 15px; background: var(--primary); color: white; border: none; padding: 15px; border-radius: 8px; font-weight: bold; cursor: pointer; }
.resultado { text-align: center; background: white; padding: 40px; border-radius: 12px; }
.score .grande { font-size: 4rem; font-weight: 800; color: var(--primary); }
</style>