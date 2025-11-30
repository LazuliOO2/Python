# 🧠 Extrator de Pedidos com LLM e Pydantic

## 📦 Descrição

Este projeto tem como objetivo **extrair automaticamente pedidos em formato estruturado (JSON)** a partir de **mensagens de texto não estruturadas** enviadas por clientes.  
Ele utiliza **modelos de linguagem (LLM)** como o [Ollama](https://ollama.com) com o modelo **Gemma 3:1B**, combinados com **validação de dados via Pydantic**, para garantir que as informações extraídas estejam corretas e no formato esperado.

O sistema realiza as seguintes etapas:
- 🧠 Interpretação da mensagem original do cliente.  
- 🔎 Extração dos campos relevantes (cliente, endereço, itens, pagamento etc.).  
- 🧹 Normalização e validação dos dados com base em um esquema definido.  
- 💾 Salvamento dos pedidos em arquivos JSON e JSONL.  

---

## 📁 Estrutura do Projeto

```
📂 CONSULTORIADESAFIO
├── 📁 env/                  → Ambiente virtual (opcional)
├── 📁 out/                  → Saída dos pedidos extraídos (JSON e JSONL)
├── 📄 app.py               → Script principal para extração, validação e salvamento (com LLM)
├── 📄 pedido_extractor_no_llm.py → Versão B sem LLM (regex + heurísticas)
└── 📄 requirements.txt     → Dependências do projeto
```

---

## 🛠️ Tecnologias Utilizadas

- **Python**: Linguagem principal do projeto.  
- **Pydantic**: Para definição de esquemas e validação dos dados extraídos.  
- **Requests**: Para realizar requisições ao servidor do modelo LLM.  
- **Ollama**: Backend de inferência LLM local.  
- **JSON**: Formato estruturado de saída dos pedidos.  
- **Regex (re)**: Para limpeza e sanitização de respostas do modelo.

---

## ⚙️ Instalação

1. **Clonar o repositório:**

```sh
git clone <URL_DO_REPOSITORIO>
cd CONSULTORIADESAFIO
```

2. **Criar e ativar o ambiente virtual (opcional):**

```sh
python -m venv env
source env/bin/activate     # ou env\Scripts\activate no Windows
```

3. **Instalar as dependências:**

```sh
pip install -r requirements.txt
```

4. **Instalar e rodar o Ollama (caso ainda não tenha):**

- Acesse [https://ollama.com/download](https://ollama.com/download)  
- Instale o Ollama no seu sistema e baixe o modelo utilizado:

```sh
ollama pull gemma3:1b
```

---

## 🚀 Execução

Para rodar o projeto com LLM, basta executar o arquivo `app.py`:

```sh
python app.py
```

✅ Exemplo de mensagem processada:

```
"Oi! Aqui é o João. Quero 2 pizzas grandes de calabresa (sem cebola) e uma coca 2L. 
Entregar na Rua das Flores, 55. Pago em dinheiro. Por favor, deixar na portaria."
```

✅ Saída esperada (JSON estruturado):

```json
{
  "cliente": "João",
  "telefone": null,
  "endereco": "Rua das Flores, 55",
  "pagamento": "dinheiro",
  "itens": [
    {
      "produto": "pizza de calabresa",
      "tamanho": "grande",
      "quantidade": 2,
      "observacoes": ["sem cebola"]
    },
    {
      "produto": "coca-cola",
      "tamanho": "2L",
      "quantidade": 1,
      "observacoes": null
    }
  ],
  "observacoes_gerais": ["deixar na portaria"],
  "mensagem_original": "Oi! Aqui é o João..."
}
```

Após a execução, os resultados são automaticamente salvos em:

- 📄 `out/pedido-YYYY-MM-DDTHH-MM-SS.json` – Pedido individual.
- 📄 `out/pedidos.jsonl` – Histórico com múltiplos pedidos (um por linha).

---

## 📚 Funcionalidades Principais

- ✅ **Extração robusta:** Interpreta pedidos em linguagem natural com precisão.  
- ✅ **Sanitização automática:** Remove ruídos e corrige respostas imperfeitas do LLM.  
- ✅ **Validação com Pydantic:** Garante integridade dos dados e tipos corretos.  
- ✅ **Fallback inteligente:** Se o modelo esquecer campos obrigatórios, o sistema preenche automaticamente.  
- ✅ **Exportação versátil:** Permite salvar cada pedido individualmente ou em lote (JSONL).

---

## 🧪 Sem Ollama? Use a Versão B!

Caso você **não queira ou não possa instalar o Ollama**, existe uma **Versão B** deste projeto (`pedido_extractor_no_llm.py`) que funciona **100% localmente**, sem depender de modelos de linguagem.  

Essa versão utiliza **regex, heurísticas e Pydantic** para identificar os mesmos campos (cliente, endereço, itens, pagamento, observações etc.) diretamente a partir do texto, com alta precisão em cenários comuns.

### 🧰 Como usar a versão B

1. Certifique-se de ter o Python instalado.  
2. Instale a dependência mínima:
   ```bash
   pip install pydantic
   ```
3. Execute o script diretamente:
   ```bash
   python pedido_extractor_no_llm.py
   ```

✅ Ele fará a extração dos pedidos da mesma forma e também salvará os resultados em:

- 📄 `out/pedido-YYYY-MM-DDTHH-MM-SS.json` – pedido individual.  
- 📄 `out/pedidos.jsonl` – histórico em formato JSONL.

---

### 🧠 Gemma 1B – Requisitos de Hardware (estimados)

| Ambiente | Mínimo recomendável | Ideal para rodar bem |
|----------|---------------------|----------------------|
| 💻 **CPU (sem GPU)** | 8 GB RAM total / ~4 GB RAM livre <br> CPU 4 núcleos (x86_64) | 16 GB RAM total / 8 GB livre <br> CPU 6+ núcleos |
| ⚙️ **GPU (recomendado)** | GPU com **2 GB VRAM** (quantizado em 4-bit) | GPU com **4 GB+ VRAM** para rodar fluido e mais rápido |
| 💾 **Armazenamento** | ~1,2 GB (modelo em 4-bit quantizado) | ~3 GB se usar versões em 8-bit / FP16 |
| 📦 **Rede / Download** | ~1 GB de download do modelo (gemma:1b) | — |

---

### 📊 Dica prática (testada com Ollama)

| Configuração | Tempo médio de resposta |
|--------------|--------------------------|
| 💻 i7 + 16 GB RAM (sem GPU) | ~2.5s – 6s por resposta curta |
| ⚙️ Ryzen 5 + 32 GB RAM + GTX 1650 (4 GB) | ~0.4s – 1.2s por resposta |
| 🍏 Apple M1 (16 GB) | ~1s – 2s por resposta |
| ☁️ VPS com 2 vCPU e 4 GB RAM | ❌ Pode travar / muito lento |

💡 **Dica:** use a versão com LLM quando precisar lidar com **mensagens complexas ou pouco estruturadas**.  
Se o objetivo for apenas extrair pedidos simples e comuns (pizzas, lanches, bebidas etc.), a **Versão B** já será mais que suficiente.

---

### 🔍 Diferenças principais

| Recurso | Versão com LLM (`app.py`) | Versão B (`pedido_extractor_no_llm.py`) |
|--------|----------------------------|----------------------------------------|
| Extração semântica (interpretação complexa) | ✅ Alta (via modelo LLM) | ⚠️ Limitada a padrões comuns |
| Instalação de modelo | ✅ Necessária (Ollama + modelo) | ❌ Não necessária |
| Precisão em frases ambíguas | ✅ Melhor | ⚠️ Depende do texto |
| Execução local e offline | ✅ Sim | ✅ Sim |
| Dependências | Python + Pydantic + Requests + Ollama | Apenas Python + Pydantic |

---

## 🤝 Contribuição

Contribuições são bem-vindas! Caso queira melhorar a extração, adicionar novos campos ou integrar outros modelos, sinta-se à vontade para abrir uma **Pull Request**.

---

## 📜 Licença

Este projeto está sob a licença **MIT** – veja o arquivo LICENSE para mais detalhes.
