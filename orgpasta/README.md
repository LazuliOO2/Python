
# 🗂️ Organizador de Arquivos com Python e Tkinter

Este projeto é um **script em Python** que organiza automaticamente os arquivos de uma pasta em subpastas categorizadas por tipo (imagens, documentos, vídeos etc.). Ele oferece uma **interface gráfica simples com Tkinter** para lidar com conflitos de arquivos, além de um **modo console** como alternativa.

## 📁 Introdução

O objetivo deste projeto é facilitar a organização de diretórios bagunçados, movendo cada arquivo para a pasta correspondente com base na sua extensão. Ele é útil para:

- Organizar downloads automaticamente.
- Separar arquivos de projetos em categorias.
- Manter seu sistema de arquivos limpo e estruturado.

### 🔧 Bibliotecas utilizadas

- **os**: manipulação de diretórios e caminhos.
- **shutil**: mover e renomear arquivos.
- **pathlib**: manipulação moderna de caminhos de arquivos.
- **tkinter**: interface gráfica para decisões de conflito.

---

## ⚙️ Instalação

1. Clone o repositório para sua máquina local:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

2. Instale as dependências necessárias (Tkinter já vem com o Python na maioria dos casos):

```bash
pip install tk
```

> 💡 Obs: Em algumas distribuições Linux, pode ser necessário instalar o Tkinter separadamente:
```bash
sudo apt-get install python3-tk
```

---

## 🧠 Explicação do Código

O script é dividido em três partes principais:

### 🪟 1. Interface de Decisão de Conflitos

Quando um arquivo com o mesmo nome já existe no destino, o programa exibe uma **janela Tkinter** para que você escolha o que fazer:

- **Pular** – Ignora o arquivo atual.
- **Renomear** – Cria uma nova versão com nome diferente (`arquivo_1.txt`).
- **Sobrescrever** – Substitui o arquivo existente.

Também é possível aplicar a mesma decisão para todos os conflitos da sessão.

Se o Tkinter não estiver disponível (por exemplo, em servidores), o script entra automaticamente no **modo console**, pedindo as opções via `input()`.

---

### 📁 2. Organização de Arquivos

Os arquivos são classificados automaticamente nas seguintes categorias:

- 🖼️ **Imagens** – `.jpg`, `.png`, `.webp`, etc.
- 📄 **Documentos** – `.pdf`, `.docx`, `.txt`, `.xlsx`, etc.
- 🎧 **Áudios** – `.mp3`, `.wav`, etc.
- 🎥 **Vídeos** – `.mp4`, `.avi`, `.mkv`, etc.
- 📦 **Compactados** – `.zip`, `.rar`, `.7z`, etc.
- 💻 **Scripts** – `.py`, `.js`, `.php`, etc.
- ⚙️ **Executáveis** – `.exe`, `.msi`, `.deb`, etc.
- 📁 **Outros** – Extensões não reconhecidas.

---

### 🖥️ 3. Execução do Script

Ao rodar o programa, ele solicita o caminho da pasta a ser organizada. Você pode:

- Digitar o caminho manualmente.
- Pressionar Enter e selecionar a pasta por meio de uma janela gráfica.

Exemplo de uso no terminal:

```bash
python app.py
```

📂 Exemplo de saída:

```
✅ foto.png → Imagens
✅ relatorio.pdf → Documentos
✳️  Renomeado e movido: script.py → Scripts/script_1.py
♻️  Sobrescrito: video.mp4 → Vídeos/video.mp4

🎉 Organização concluída com sucesso!
```

---

## 🧪 Como Usar

1. Execute o script diretamente:

```bash
python app.py
```

2. Digite ou selecione a pasta que deseja organizar.

3. Escolha o que fazer em caso de conflitos de arquivos.

4. Veja os arquivos organizados automaticamente em subpastas!

---

## 📌 Observações

- Se preferir automatizar a execução, você pode transformar este script em um serviço agendado (por exemplo, com `cron` no Linux ou Agendador de Tarefas no Windows).
- O código foi estruturado para ser facilmente adaptado — você pode adicionar novas categorias e extensões conforme necessário.

---

## 🚀 Próximas Atualizações

- Interface gráfica completa para selecionar múltiplas pastas.
- Barra de progresso e logs detalhados.
- Integração com sistemas de monitoramento em tempo real usando `watchdog`.

---

### 📜 Licença

Este projeto é open-source e está disponível sob a licença MIT. Sinta-se à vontade para usar, modificar e compartilhar.
