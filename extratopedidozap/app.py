from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError
import json, requests, time
import re
import traceback
from pathlib import Path
from datetime import datetime
# ============================================================
# * 1) Esquemas (Pydantic)
# ============================================================

# * Define a estrutura para os tipo de dados (schema)
# ? Optional[T] = "o valor pode ser do tipo T ou None"
class Item(BaseModel):
    produto: str
    tamanho: Optional[str] = None
    quantidade: Optional[int] = None
    observacoes: Optional[List[str]] = None

# ? Field permite metadados e valores padrão avançados.
class PedidoSchema(BaseModel):
    cliente: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    pagamento: Optional[str] = None  # validaremos valor depois
    itens: List[Item] = Field(default_factory=list)
    observacoes_gerais: Optional[List[str]] = None
    mensagem_original: str  # <- obrigatório (mas garantimos fallback no código)

# ============================================================
# * 2) Config do LLM
# ============================================================

ENGINE = "ollama"  # "ollama" | "transformers"
MODEL  = "gemma3:1b"

# ============================================================
# * 3) Prompt (otimizado p/ modelos pequenos)
# ============================================================

PROMPT_TEMPLATE = """Você é um extrator de dados estritamente JSON.

TAREFA: extraia o pedido da MENSAGEM e responda APENAS com um JSON VÁLIDO (sem comentários, sem texto extra).

Esquema:
{{
  "cliente": string|null,
  "telefone": string|null,
  "endereco": string|null,
  "pagamento": "pix"|"dinheiro"|"cartão crédito"|"cartão débito"|null,
  "itens": [
    {{"produto": string, "tamanho": string|null, "quantidade": int|null, "observacoes": [string]|null}}
  ],
  "observacoes_gerais": [string]|null,
  "mensagem_original": string
}}

Regras:
- Converta números por extenso para inteiros quando fizer sentido ("duas" → 2; "uma" → 1).
- Se não tiver certeza, use null.
- NÃO inclua nada fora do JSON.
- O campo "mensagem_original" deve repetir a mensagem recebida, integralmente.

Regras adicionais:
- Para pizzas e lanches: mantenha o SABOR em "produto" (ex.: "pizza de frango com catupiry") e use "tamanho" apenas para o porte ("pequena", "média", "grande"). Não divida um item em vários (não separar "pizza" e "frango").
- "observacoes_gerais" deve conter APENAS observações não vinculadas a um item: "sem guardanapo", "entregar no portão", "com talheres". NÃO copie a mensagem inteira. NÃO repita endereço, pagamento, telefone, sabores ou tamanhos.
- Se a quantidade não for mencionada explicitamente, assuma 1.
- Use "tamanho" para porte do item (pizza) ou medida/volume (ex.: "2L", "350ml"), quando for característica do produto e não quantidade de unidades.

Exemplos:
Entrada: "pizza média de frango c/ catupiry (sem azeitona) e coca 2L"
Saída:
{{
  "itens": [
    {{"produto": "pizza de frango com catupiry", "tamanho": "média", "quantidade": 1, "observacoes": ["sem azeitona"]}},
    {{"produto": "coca-cola", "tamanho": "2L", "quantidade": 1, "observacoes": null}}
  ],
  "observacoes_gerais": null
}}

MENSAGEM:
\"\"\"{mensagem}\"\"\"\n"""


# ============================================================
# * 4) Implementações de call_llm (Ollama)
# ============================================================

def _ollama_generate(prompt: str, model: str, temperature: float = 0.1, max_tokens: int = 768) -> str:
    """
    Chama o endpoint /api/generate do Ollama.
    Dica: "raw": True ajuda modelos pequenos a respeitar melhor format="json".
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "format": "json",  # solicita JSON
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "raw": True,  # <- melhora o cumprimento de JSON estrito em alguns modelos
        },
        "stream": False,
    }
    r = requests.post(url, json=payload, timeout=120)
    r.raise_for_status()
    out = r.json().get("response", "")
    return out.strip()

def call_llm(prompt: str) -> str:
    # wrapper simples (facilita trocar motor no futuro)
    return _ollama_generate(prompt, MODEL)

# ============================================================
# * 5) Utilidades de parsing/sanitização
# ============================================================

def _has_explicit_qty(text: str) -> bool:
    """
    Heurística: detecta menções explícitas de quantidade (números e palavras comuns).
    """
    text = (text or "").lower()
    return bool(re.search(r"\b(\d+|uma|um|duas|dois|tr[eê]s|quatro|cinco|meia|metade)\b", text))

def _clean_noise(txt: str) -> str:
    """
    Remove ruídos comuns: BOM, aspas “curly”, comentários, cercas de código.
    """
    if not isinstance(txt, str):
        return txt

    s = txt

    # Remove BOM
    s = s.lstrip("\ufeff")

    # Normaliza aspas “curly”
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    # Remove cercas ``` (com ou sem "json")
    s = s.strip()
    if s.startswith("```"):
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl+1:]
        if s.endswith("```"):
            s = s[:-3].rstrip()

    # Remove comentários de linha //... e de bloco /* ... */
    s = re.sub(r"//[^\n\r]*", "", s)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)

    return s.strip()

def _force_json_load(s: str) -> dict:
    """
    Carrega JSON tolerante a 'lixo' comum de LLMs:
    - remove BOM, aspas curly, comentários, cercas de código
    - se vier só os pares chave:valor sem { }, embrulha com { ... }
    - recorta do primeiro '{' ao último '}'
    - remove vírgulas à esquerda de '}' e ']'
    - remove vírgula inicial/final solta
    - balanceia chaves se faltar
    Em caso de erro, lança ValueError com um trecho útil (RAW e CANDIDATE).
    """
    if not s or not isinstance(s, str):
        raise ValueError("Resposta vazia do LLM")

    # ---------- limpeza básica ----------
    txt = s

    # BOM
    txt = txt.lstrip("\ufeff")

    # aspas “curly”
    txt = txt.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")

    # cercas ``` (com ou sem 'json')
    t = txt.strip()
    if t.startswith("```"):
        first_nl = t.find("\n")
        if first_nl != -1:
            t = t[first_nl+1:]
        if t.endswith("```"):
            t = t[:-3].rstrip()
        txt = t

    # comentários //... e /* ... */
    txt = re.sub(r"//[^\n\r]*", "", txt)
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.DOTALL)

    raw_clean = txt.strip()

    # ---------- CASO RAIZ DO SEU ERRO ----------
    # Se não tem '{' mas já começa com uma chave conhecida tipo "cliente":
    # ou o texto começa com aspas de chave na 1ª linha
    starts_with_key = bool(re.match(
        r'^\s*"\s*(cliente|telefone|endereco|pagamento|itens|observacoes_gerais|mensagem_original)\s*"\s*:',
        raw_clean
    ))
    if ("{" not in raw_clean and "}" not in raw_clean and starts_with_key):
        raw_clean = "{\n" + raw_clean.strip().strip(",") + "\n}"

    # ---------- recorte { ... } se existir ----------
    if "{" in raw_clean and "}" in raw_clean and raw_clean.find("{") < raw_clean.rfind("}"):
        candidate = raw_clean[raw_clean.find("{"): raw_clean.rfind("}") + 1]
    else:
        candidate = raw_clean  # pode ser array (não é o esperado, mas tentamos)

    # vírgulas finais antes de '}' e ']'
    candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
    # vírgula solta no começo/fim
    candidate = candidate.strip().lstrip(",").rstrip(",")

    # ---------- tentativa de parse ----------
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as e:
        # balancear chaves se faltar
        open_count  = candidate.count("{")
        close_count = candidate.count("}")
        if close_count < open_count:
            candidate2 = candidate + ("}" * (open_count - close_count))
            candidate2 = re.sub(r",\s*([}\]])", r"\1", candidate2)
            candidate2 = candidate2.strip().lstrip(",").rstrip(",")
            try:
                return json.loads(candidate2)
            except json.JSONDecodeError as e2:
                raw_snip = raw_clean[:400].replace("\n", "\\n")
                cand_snip = candidate2[:400].replace("\n", "\\n")
                raise ValueError(
                    f"Falha ao parsear JSON (após balancear). RAW: {raw_snip} || CAND: {cand_snip} || err: {e2}"
                ) from e2
        else:
            raw_snip = raw_clean[:400].replace("\n", "\\n")
            cand_snip = candidate[:400].replace("\n", "\\n")
            raise ValueError(
                f"Falha ao parsear JSON. RAW: {raw_snip} || CAND: {cand_snip} || err: {e}"
            ) from e

# ============================================================
# * 6) Extração + validação
# ============================================================

def extrair_com_llm(mensagem: str) -> dict:
    """
    Envia a mensagem ao LLM, tenta decodificar JSON de forma robusta,
    normaliza campos e valida contra o schema Pydantic.
    """
    prompt = PROMPT_TEMPLATE.format(mensagem=mensagem)

    # Primeira chamada ao LLM
    raw = call_llm(prompt).strip()
    print("RAW 1ª chamada (primeiros 400):", raw[:400].replace("\n", "\\n"))

    # 1ª tentativa de parse
    try:
        data = _force_json_load(raw)
    except Exception as e:
        print("DEBUG (1ª tentativa) - bruto:", raw[:800])
        # 2ª tentativa: reforça a instrução e pede JSON estrito
        retry_prompt = prompt + "\n\nResponda NOVAMENTE e APENAS com JSON válido (sem texto fora do JSON). Comece com '{' e termine com '}'."
        time.sleep(0.1)
        raw = call_llm(retry_prompt).strip()
        print("RAW 2ª chamada (primeiros 400):", raw[:400].replace("\n", "\\n"))
        try:
            data = _force_json_load(raw)
        except Exception as e2:
            print("DEBUG (2ª tentativa) - bruto:", raw[:800])
            raise RuntimeError(f"Falha ao decodificar JSON do LLM: {e2}") from e2

    if not isinstance(data, dict):
        # Se vier array/valor, falha clara
        raise RuntimeError("LLM não retornou um objeto JSON na raiz.")

    # Fallback: se o modelo esquecer, preserva a mensagem original
    data.setdefault("mensagem_original", mensagem)

    # ------- Normalizações -------
    # pagamento normalizado
    if isinstance(data.get("pagamento"), str):
        mapa = {
            "pix": "pix",
            "dinheiro": "dinheiro",
            "cartao credito": "cartão crédito",
            "cartão credito": "cartão crédito",
            "cartao debito": "cartão débito",
            "cartão debito": "cartão débito",
            "cartão crédito": "cartão crédito",
            "cartão débito": "cartão débito",
        }
        raw_val = data["pagamento"].strip().lower()
        table = str.maketrans("ãáâàéêíóôúç", "aaaaeeioouc")
        norm = raw_val.translate(table).replace("  ", " ")
        data["pagamento"] = mapa.get(norm, data["pagamento"])

    # itens
    itens = data.get("itens", [])
    if isinstance(itens, list):
        for it in itens:
            if not isinstance(it, dict):
                continue
            # observacoes: string -> [string]
            if isinstance(it.get("observacoes"), str):
                it["observacoes"] = [it["observacoes"]]
            # quantidade: "3" -> 3
            if isinstance(it.get("quantidade"), str) and it["quantidade"].strip().isdigit():
                it["quantidade"] = int(it["quantidade"].strip())
            # default = 1 se não houver quantidade explícita na mensagem
            if it.get("quantidade") in (None, "") and it.get("produto"):
                if not _has_explicit_qty(data.get("mensagem_original", "")):
                    it["quantidade"] = 1
            # padronização de alguns nomes
            p = (it.get("produto") or "").strip().lower()
            if p in ("coca", "coca cola", "coca-cola", "refrigerante coca"):
                it["produto"] = "coca-cola"

    # observacoes_gerais: string -> [string] e filtro de lixo
    if isinstance(data.get("observacoes_gerais"), str):
        data["observacoes_gerais"] = [data["observacoes_gerais"]]
    if isinstance(data.get("observacoes_gerais"), list):
        ban = ["pizza", "coca", "catupiry", "calabresa", "endereço", "endereco", "pago", "pagamento", "telefone"]
        data["observacoes_gerais"] = [
            o for o in data["observacoes_gerais"]
            if isinstance(o, str) and 2 <= len(o) <= 80 and not any(k in o.lower() for k in ban)
        ] or None

    # Validação (Pydantic v2)
    pedido = PedidoSchema(**data)
    return pedido.model_dump()

# ============================================================
# * 6.5) Funções para salvar pedidos em arquivos JSON
# ============================================================

from pathlib import Path
from datetime import datetime

def _safe_write_text(path: Path, content: str) -> None:
    """
    Grava conteúdo em arquivo de forma simples.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def save_pedido_json_unico(pedido: dict, out_dir: str = "out") -> Path:
    """
    Salva um arquivo JSON único para o pedido (nome com timestamp).
    Retorna o Path do arquivo salvo.
    """
    ts = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    path = Path(out_dir) / f"pedido-{ts}.json"
    _safe_write_text(path, json.dumps(pedido, ensure_ascii=False, indent=2))
    return path

def append_pedido_jsonl(pedido: dict, out_dir: str = "out", filename: str = "pedidos.jsonl") -> Path:
    """
    Acrescenta o pedido em um arquivo JSON Lines (uma linha por pedido).
    Cria o arquivo se não existir.
    Retorna o Path do arquivo.
    """
    path = Path(out_dir) / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(pedido, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return path

# ============================================================
# * 7) Uso 
# ============================================================

if __name__ == "__main__":
    msg = (
        "Oi! Aqui é o João. Quero 2 pizzas grandes de calabresa (sem cebola) e uma coca 2L. "
        "Entregar na Rua das Flores, 55. Pago em dinheiro. Por favor, deixar na portaria"
    )
    try:
        resultado = extrair_com_llm(msg)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))

        # 👇 Aqui salva o pedido automaticamente
        json_unico = save_pedido_json_unico(resultado, out_dir="out")
        jsonl_log  = append_pedido_jsonl(resultado, out_dir="out", filename="pedidos.jsonl")
        print(f"\nArquivos salvos:\n- {json_unico}\n- {jsonl_log}")

    except ValidationError as e:
        print("Falha de validação:", e)
    except Exception as e:
        print("Erro geral:", e)
        print("--- TRACEBACK ---")
        print(traceback.format_exc())


