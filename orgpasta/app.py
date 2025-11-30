import os
import shutil
from pathlib import Path

# ---------- NOVO: UI com Tkinter ----------
def perguntar_opcao_gui(pergunta, opcoes_validas, padrao=None):
    """
    Mostra um diálogo Tkinter modal (sem usar mainloop global).
    Retorna (tecla_escolhida, aplicar_a_todos: bool) ou (None, False) se falhar.
    """
    try:
        import tkinter as tk
        from tkinter import ttk

        escolha = {"key": None, "apply_all": False}

        # root oculto para gerenciar o diálogo
        root = tk.Tk()
        root.withdraw()  # não mostra janela principal

        # cria janela modal
        top = tk.Toplevel(root)
        top.title("Conflito de arquivos")
        top.resizable(False, False)

        # centralizar
        largura, altura = 520, 220
        top.update_idletasks()
        x = (top.winfo_screenwidth() // 2) - (largura // 2)
        y = (top.winfo_screenheight() // 2) - (altura // 2)
        top.geometry(f"{largura}x{altura}+{x}+{y}")

        # manter em primeiro plano (por curto período)
        try:
            top.attributes("-topmost", True)
            top.after(250, lambda: top.attributes("-topmost", False))
        except Exception:
            pass

        frm = ttk.Frame(top, padding=16)
        frm.pack(fill="both", expand=True)

        lbl = ttk.Label(frm, text=pergunta, wraplength=480, justify="left")
        lbl.pack(anchor="w", pady=(0, 12))

        apply_var = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(frm, text="Aplicar esta decisão a todos os conflitos desta execução",
                              variable=apply_var)
        chk.pack(anchor="w", pady=(0, 12))

        btns = ttk.Frame(frm)
        btns.pack()

        def choose(key):
            escolha["key"] = key
            escolha["apply_all"] = bool(apply_var.get())
            top.destroy()

        # cria botões na ordem das chaves
        for key, label in opcoes_validas.items():
            ttk.Button(btns, text=f"{label} ({key})", command=lambda k=key: choose(k)).pack(side="left", padx=6)

        # Enter = padrão (se existir)
        def on_enter(event):
            if padrao and padrao in opcoes_validas:
                choose(padrao)

        top.bind("<Return>", on_enter)

        # ESC = fecha como padrão (ou cancela)
        def on_esc(event):
            if padrao and padrao in opcoes_validas:
                choose(padrao)
            else:
                top.destroy()

        top.bind("<Escape>", on_esc)

        # Fechar janela = padrão (se houver) ou None
        def on_close():
            if padrao and padrao in opcoes_validas:
                choose(padrao)
            else:
                top.destroy()

        top.protocol("WM_DELETE_WINDOW", on_close)

        # foco no diálogo
        top.focus_force()
        top.grab_set()          # torna modal (bloqueia interação com outras janelas do app)
        root.wait_window(top)   # espera o diálogo fechar (sem mainloop global)

        # encerra root oculto
        try:
            root.destroy()
        except Exception:
            pass

        return escolha["key"], escolha["apply_all"]

    except Exception:
        # Falhou a GUI? Fallback pro console no chamador.
        return None, False


def perguntar_opcao_console(pergunta, opcoes_validas, padrao=None):
    opcoes_str = "/".join([k for k in opcoes_validas.keys()])
    while True:
        resp = input(f"{pergunta} [{opcoes_str}]{' (Enter='+padrao+')' if padrao else ''}: ").strip().upper()
        if not resp and padrao:
            return padrao, False
        if resp in opcoes_validas:
            # No console, perguntamos também se quer aplicar a todos
            resp_all = input("Aplicar esta decisão a todos os conflitos? [S/N] (Enter=N): ").strip().upper()
            aplicar_todos = (resp_all == "S")
            return resp, aplicar_todos
        print(f"Opção inválida. Escolha uma das seguintes: {opcoes_str}.")

def perguntar_opcao(pergunta, opcoes_validas, padrao=None):
    """
    Tenta GUI; se não rolar, usa console.
    Retorna (opcao, aplicar_a_todos)
    """
    key, apply_all = perguntar_opcao_gui(pergunta, opcoes_validas, padrao)
    if key is not None:
        return key, apply_all
    # fallback console
    return perguntar_opcao_console(pergunta, opcoes_validas, padrao)

# ---------- RESTO DO SEU SCRIPT ----------
def gerar_nome_sem_colisao(destino_path: Path) -> Path:
    base = destino_path.stem
    sufixo = destino_path.suffix
    pasta = destino_path.parent
    i = 1
    novo = destino_path
    while novo.exists():
        novo = pasta / f"{base}_{i}{sufixo}"
        i += 1
    return novo

def organizar_arquivos(pasta_base):
    pasta = Path(pasta_base)
    if not pasta.exists():
        print(f"❌ Erro: A pasta '{pasta_base}' não existe!")
        return False

    categorias = {
        "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx", ".odt"],
        "Áudios": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "Vídeos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
        "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Scripts": [".py", ".js", ".html", ".css", ".php", ".java"],
        "Executáveis": [".exe", ".msi", ".deb", ".dmg"],
        "Outros": []
    }

    # guarda decisão global se usuário marcar "aplicar a todos"
    decisao_global = {"acao": None}  # "S"|"R"|"O"

    try:
        for categoria in categorias:
            (pasta / categoria).mkdir(exist_ok=True)

        for arquivo in pasta.iterdir():
            if arquivo.is_file():
                extensao = arquivo.suffix.lower()

                categoria_destino = "Outros"
                for categoria, extensoes in categorias.items():
                    if extensao in extensoes:
                        categoria_destino = categoria
                        break

                destino = pasta / categoria_destino / arquivo.name

                if destino.exists():
                    # se já temos decisão global, usamos ela
                    if decisao_global["acao"]:
                        acao = decisao_global["acao"]
                        aplicar_todos = True
                    else:
                        pergunta = (
                            f"Já existe '{destino.name}' em '{categoria_destino}'.\n"
                            f"O que deseja fazer com '{arquivo.name}'?"
                        )
                        opcoes = {"S": "Pular", "R": "Renomear", "O": "Sobrescrever"}
                        acao, aplicar_todos = perguntar_opcao(pergunta, opcoes, padrao="S")
                        if aplicar_todos:
                            decisao_global["acao"] = acao

                    if acao == "S":
                        print(f"⏭️  Pulado: {arquivo.name}")
                        continue
                    elif acao == "R":
                        novo_dest = gerar_nome_sem_colisao(destino)
                        shutil.move(str(arquivo), str(novo_dest))
                        print(f"✳️  Renomeado e movido: {arquivo.name} → {novo_dest.parent.name}/{novo_dest.name}")
                    elif acao == "O":
                        try:
                            destino.unlink()
                        except Exception:
                            pass
                        shutil.move(str(arquivo), str(destino))
                        print(f"♻️  Sobrescrito: {arquivo.name} → {categoria_destino}/{destino.name}")
                else:
                    shutil.move(str(arquivo), str(destino))
                    print(f"✅ {arquivo.name} → {categoria_destino}")

        print("\n🎉 Organização concluída com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro durante a organização: {e}")
        return False

if __name__ == "__main__":
    caminho = input("Digite o caminho da pasta a organizar (ou Enter para selecionar): ").strip()
    if not caminho:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw()
            caminho = filedialog.askdirectory(title="Selecione a pasta para organizar")
        except Exception:
            print("⚠️  tkinter não disponível. Digite o caminho manualmente.")
            caminho = input("Caminho da pasta: ").strip()

    if caminho and os.path.exists(caminho):
        organizar_arquivos(caminho)
    else:
        print("❌ Nenhuma pasta válida selecionada.")
