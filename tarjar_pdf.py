"""Tarjação de verdade de PDF - remove o texto sensível de dentro do documento (não só cobre com
uma caixa preta por cima). Usa PyMuPDF.

Como usar:
    - Modo Gráfico (GUI): execute este arquivo diretamente (duplo-clique ou 'python tarjar_pdf.py')
    - Modo Linha de Comando (CLI): python tarjar_pdf.py arquivo1.pdf [arquivo2.pdf ...]

Os termos sensíveis NÃO ficam no código-fonte. Ficam armazenados exclusivamente no arquivo
de configuração 'termos_sensiveis.json'.
"""

from __future__ import annotations

import os
import sys
import json
import queue
import threading
import pymupdf
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

VERSAO_APP = "1.2.0"

# Não há dados pessoais fixados no código-fonte; tudo é lido e salvo no arquivo JSON.
TERMOS_SENSIVEIS_PADRAO: list[str] = []


def _safe_print(msg: str):
    """Imprime com segurança em qualquer console Windows (evita UnicodeEncodeError)."""
    enc = sys.stdout.encoding or "utf-8"
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode(enc, errors="replace").decode(enc))


def obter_caminho_config() -> str:
    """Retorna o caminho onde a lista de termos é salva de forma persistente."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    caminho_local = os.path.join(base_dir, "termos_sensiveis.json")
    teste_escrita = os.path.join(base_dir, ".test_write.tmp")
    try:
        with open(teste_escrita, "w", encoding="utf-8") as f:
            f.write("ok")
        if os.path.exists(teste_escrita):
            os.remove(teste_escrita)
        return caminho_local
    except (PermissionError, OSError):
        appdata = os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))
        pasta_app = os.path.join(appdata, "TarjadorPDF")
        os.makedirs(pasta_app, exist_ok=True)
        return os.path.join(pasta_app, "termos_sensiveis.json")


def carregar_termos_config() -> list[str]:
    """Carrega os termos do arquivo JSON. Caso não exista, cria o arquivo automaticamente."""
    caminho = obter_caminho_config()
    if not os.path.exists(caminho):
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            _safe_print(f"Arquivo de configuração criado: {caminho}")
        except Exception as e:
            _safe_print(f"Aviso ao criar {caminho}: {e}")
        return []

    if os.path.isfile(caminho) and os.path.getsize(caminho) > 0:
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                if isinstance(dados, list):
                    return [str(t).strip() for t in dados if str(t).strip()]
        except Exception as e:
            _safe_print(f"Aviso ao ler {caminho}: {e}")
    return []


def salvar_termos_config(termos: list[str]) -> bool:
    """Salva a lista de termos sensíveis no arquivo de configuração JSON."""
    caminho = obter_caminho_config()
    try:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(termos, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        _safe_print(f"Erro ao salvar {caminho}: {e}")
        return False


def tarjar(caminho_entrada: str, termos: list[str], callback_log=None) -> str:
    """Tarja os termos sensíveis no arquivo PDF informado e salva com sufixo '_tarjado.pdf'."""
    def log(msg: str):
        if callback_log:
            callback_log(msg)
        else:
            _safe_print(msg)

    if not os.path.isfile(caminho_entrada):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_entrada}")

    nome_arquivo = os.path.basename(caminho_entrada)
    caminho_saida = caminho_entrada.rsplit(".", 1)[0] + "_tarjado.pdf"

    log(f"--- Iniciando: {nome_arquivo} ---")
    doc = pymupdf.open(caminho_entrada)
    contagem = {termo: 0 for termo in termos}

    total_paginas = len(doc)
    for num_pag, pagina in enumerate(doc, 1):
        for termo in termos:
            areas = pagina.search_for(termo)
            for area in areas:
                pagina.add_redact_annot(area, fill=(0, 0, 0))  # preenche de preto sólido
                contagem[termo] += 1
        pagina.apply_redactions()  # remove o texto/objeto do PDF permanentemente

    doc.save(caminho_saida)
    doc.close()

    log(f"[OK] Salvo como: {os.path.basename(caminho_saida)} ({total_paginas} página(s))")
    total_encontrados = sum(contagem.values())
    log(f"Ocorrências tarjadas (Total: {total_encontrados}):")
    for termo, n in contagem.items():
        if n > 0:
            log(f"  [OK] {n:>2}x: {termo}")
        else:
            log(f"  [--]  0x: {termo} (não encontrado)")
    log("")

    return caminho_saida


# Alias de compatibilidade
redigir = tarjar


class TarjadorPDFApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Tarjador de PDFs v{VERSAO_APP} - Remoção de Dados Sensíveis")
        self.geometry("860x730")
        self.minsize(720, 580)

        # Configuração de estilo ttk
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.arquivos_selecionados: list[str] = []
        self.is_processando = False
        self.caminho_config = obter_caminho_config()
        self.ultima_pasta_usada = os.path.dirname(os.path.abspath(__file__))
        self.fila_mensagens: queue.Queue = queue.Queue()

        self._construir_interface()
        self._agendar_leitura_fila()
        self._carregar_termos_iniciais()

        # Salva termos automaticamente ao fechar o programa
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _construir_interface(self):
        container = ttk.Frame(self, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho com Título, Versão e Botão Sobre
        frame_header = ttk.Frame(container)
        frame_header.pack(fill=tk.X, pady=(0, 10))

        frame_header_esq = ttk.Frame(frame_header)
        frame_header_esq.pack(side=tk.LEFT, fill=tk.X, expand=True)

        frame_titulo_linha = ttk.Frame(frame_header_esq)
        frame_titulo_linha.pack(anchor=tk.W)

        lbl_titulo = ttk.Label(
            frame_titulo_linha,
            text="Tarjador de PDFs Confidenciais",
            font=("Segoe UI", 15, "bold")
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_versao = ttk.Label(
            frame_titulo_linha,
            text=f"v{VERSAO_APP}",
            font=("Segoe UI", 9, "bold"),
            foreground="#2563eb"
        )
        lbl_versao.pack(side=tk.LEFT, padx=(8, 0), pady=(4, 0))

        lbl_subtitulo = ttk.Label(
            frame_header_esq,
            text="Selecione um ou mais arquivos PDF para tarjar e remover definitivamente textos sensíveis.",
            font=("Segoe UI", 9)
        )
        lbl_subtitulo.pack(anchor=tk.W, pady=(2, 0))

        btn_sobre = ttk.Button(
            frame_header,
            text="ℹ Sobre / Ajuda",
            command=self._abrir_sobre
        )
        btn_sobre.pack(side=tk.RIGHT, padx=(10, 0))

        # Seção 1: Seleção de Arquivos
        frame_arquivos = ttk.LabelFrame(container, text=" 1. Arquivos PDF Selecionados ", padding=10)
        frame_arquivos.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        frame_botoes_arq = ttk.Frame(frame_arquivos)
        frame_botoes_arq.pack(fill=tk.X, pady=(0, 6))

        btn_add_arquivos = ttk.Button(
            frame_botoes_arq,
            text="Selecionar Arquivo(s)...",
            command=self._adicionar_arquivos
        )
        btn_add_arquivos.pack(side=tk.LEFT, padx=(0, 6))

        btn_add_pasta = ttk.Button(
            frame_botoes_arq,
            text="Adicionar Pasta...",
            command=self._adicionar_pasta
        )
        btn_add_pasta.pack(side=tk.LEFT, padx=(0, 6))

        btn_remover = ttk.Button(
            frame_botoes_arq,
            text="Remover Selecionado(s)",
            command=self._remover_selecionados
        )
        btn_remover.pack(side=tk.LEFT, padx=(0, 6))

        btn_limpar = ttk.Button(
            frame_botoes_arq,
            text="Limpar Lista",
            command=self._limpar_arquivos
        )
        btn_limpar.pack(side=tk.LEFT)

        # Listbox com Scrollbar
        frame_lista = ttk.Frame(frame_arquivos)
        frame_lista.pack(fill=tk.BOTH, expand=True)

        scrollbar_y = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        self.listbox_arquivos = tk.Listbox(
            frame_lista,
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar_y.set,
            font=("Consolas", 9),
            height=6
        )
        scrollbar_y.config(command=self.listbox_arquivos.yview)

        self.listbox_arquivos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.lbl_contagem_arqs = ttk.Label(
            frame_arquivos,
            text="0 arquivo(s) selecionado(s)",
            font=("Segoe UI", 9, "italic")
        )
        self.lbl_contagem_arqs.pack(anchor=tk.W, pady=(4, 0))

        # Seção 2: Termos Sensíveis
        nome_config = os.path.basename(self.caminho_config)
        frame_termos = ttk.LabelFrame(
            container,
            text=f" 2. Termos Sensíveis a Tarjar (armazenados em {nome_config}) ",
            padding=10
        )
        frame_termos.pack(fill=tk.BOTH, expand=False, pady=(0, 8))

        frame_termos_topo = ttk.Frame(frame_termos)
        frame_termos_topo.pack(fill=tk.X, pady=(0, 4))

        lbl_dica_termos = ttk.Label(
            frame_termos_topo,
            text="Digite ou edite os termos abaixo (um por linha):",
            font=("Segoe UI", 8)
        )
        lbl_dica_termos.pack(side=tk.LEFT)

        btn_salvar_termos = ttk.Button(
            frame_termos_topo,
            text="💾 Salvar no JSON",
            command=self._salvar_termos_manual
        )
        btn_salvar_termos.pack(side=tk.RIGHT, padx=(4, 0))

        btn_recarregar_termos = ttk.Button(
            frame_termos_topo,
            text="🔄 Recarregar do JSON",
            command=self._carregar_termos_iniciais
        )
        btn_recarregar_termos.pack(side=tk.RIGHT, padx=(4, 0))

        btn_limpar_termos = ttk.Button(
            frame_termos_topo,
            text="🗑 Limpar Termos",
            command=self._limpar_termos_tela
        )
        btn_limpar_termos.pack(side=tk.RIGHT)

        self.txt_termos = ScrolledText(
            frame_termos,
            height=6,
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.txt_termos.pack(fill=tk.BOTH, expand=True)

        # Seção 3: Ação e Progresso
        frame_acao = ttk.Frame(container)
        frame_acao.pack(fill=tk.X, pady=(0, 8))

        self.btn_executar = tk.Button(
            frame_acao,
            text="Iniciar Tarjação dos PDFs",
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            activeforeground="white",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._iniciar_processamento
        )
        self.btn_executar.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_abrir_pasta = ttk.Button(
            frame_acao,
            text="Abrir Pasta dos Arquivos",
            command=self._abrir_pasta_arquivos,
            state=tk.DISABLED
        )
        self.btn_abrir_pasta.pack(side=tk.LEFT, padx=(0, 10))

        self.barra_progresso = ttk.Progressbar(frame_acao, orient=tk.HORIZONTAL, mode="determinate")
        self.barra_progresso.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.lbl_status = ttk.Label(frame_acao, text="Pronto para iniciar", font=("Segoe UI", 9))
        self.lbl_status.pack(side=tk.RIGHT)

        # Seção 4: Log de Execução
        frame_log = ttk.LabelFrame(container, text=" 3. Registro de Execução (Log) ", padding=10)
        frame_log.pack(fill=tk.BOTH, expand=True)

        self.txt_log = ScrolledText(
            frame_log,
            height=8,
            font=("Consolas", 9),
            state=tk.NORMAL,
            bg="#f8fafc",
            fg="#0f172a"
        )
        self.txt_log.pack(fill=tk.BOTH, expand=True)

    def _abrir_sobre(self):
        """Abre a janela com a seção Sobre, descrição e instruções detalhadas."""
        janela = tk.Toplevel(self)
        janela.title("Sobre o Tarjador de PDFs")
        janela.geometry("640x540")
        janela.minsize(580, 480)
        janela.transient(self)
        janela.grab_set()

        # Centraliza a janela sobre a principal
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (640 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (540 // 2)
        janela.geometry(f"+{max(10, x)}+{max(10, y)}")

        pad = ttk.Frame(janela, padding=16)
        pad.pack(fill=tk.BOTH, expand=True)

        # Topo
        lbl_topo = ttk.Label(
            pad,
            text="Tarjador de PDFs Confidenciais",
            font=("Segoe UI", 14, "bold")
        )
        lbl_topo.pack(anchor=tk.W)

        lbl_ver = ttk.Label(
            pad,
            text=f"Versão {VERSAO_APP} • Aplicação 100% Local e Segura",
            font=("Segoe UI", 9, "italic"),
            foreground="#475569"
        )
        lbl_ver.pack(anchor=tk.W, pady=(0, 10))

        # Texto informativo com scroll
        txt_info = ScrolledText(pad, wrap=tk.WORD, font=("Segoe UI", 9), height=18)
        txt_info.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        texto_sobre = f"""O QUE É ESTE PROGRAMA?
O Tarjador de PDFs realiza a remoção permanente e irreversível de termos sensíveis (nomes, CPFs, endereços, etc.) em documentos PDF.

DIFERENÇA PARA FERRAMENTAS VISUAIS COMUNS:
Muitos editores apenas desenham retângulos pretos sobre o texto. Nesses casos, qualquer pessoa pode selecionar, copiar ou usar ferramentas de OCR para ler o que estava por baixo.
Este programa utiliza PyMuPDF para expurgar de verdade os caracteres do código interno do documento, tornando impossível recuperar a informação censurada.

--------------------------------------------------
GUIA RÁPIDO PARA NOVOS UTILIZADORES:

1. DEFINIR TERMOS SENSÍVEIS (Quadro 2)
   - Digite ou cole os dados que deseja ocultar (um por linha).
   - Clique em 'Salvar no JSON'. Os termos ficam salvos no arquivo 'termos_sensiveis.json' ao lado do programa e nunca são perdidos.

2. SELECIONAR OS DOCUMENTOS (Quadro 1)
   - Clique em 'Selecionar Arquivo(s)...' para escolher um ou mais PDFs de qualquer pasta.
   - Ou clique em 'Adicionar Pasta...' para carregar todos os PDFs de um diretório de uma só vez.

3. INICIAR A TARJAÇÃO
   - Clique no botão verde 'Iniciar Tarjação dos PDFs'.
   - O processamento roda em segundo plano e a barra indicará o progresso.
   - O registro (Log) detalhará quantas vezes cada termo foi encontrado e removido.

4. ACESSAR OS RESULTADOS
   - Para sua total segurança, os arquivos originais NUNCA são sobrescritos.
   - Cada arquivo gera uma nova cópia com o sufixo '_tarjado.pdf' (ex.: fatura_tarjado.pdf) na mesma pasta original.
   - Ao concluir, clique em 'Abrir Pasta dos Arquivos' para visualizá-los diretamente no Windows Explorer.

--------------------------------------------------
PRIVACIDADE & PORTABILIDADE:
• Totalmente Offline: nenhum documento ou dado sai do seu computador.
• Portabilidade: você pode levar este executável para qualquer outro computador Windows. Se levar o arquivo 'termos_sensiveis.json' junto, seus termos cadastrados serão carregados automaticamente.
"""
        txt_info.insert(tk.END, texto_sobre)
        txt_info.config(state=tk.DISABLED)

        btn_fechar = ttk.Button(pad, text="Fechar", command=janela.destroy)
        btn_fechar.pack(anchor=tk.E)

    def _agendar_leitura_fila(self):
        self._processar_fila()
        self.after(50, self._agendar_leitura_fila)

    def _processar_fila(self):
        while not self.fila_mensagens.empty():
            try:
                tipo, dados = self.fila_mensagens.get_nowait()
                if tipo == "LOG":
                    self._log_msg(dados)
                elif tipo == "PROGRESSO":
                    progresso, total = dados
                    self.barra_progresso.config(value=progresso, maximum=total)
                    self.lbl_status.config(text=f"{progresso}/{total} processado(s)")
                elif tipo == "FIM":
                    sucessos, erros = dados
                    self._finalizar_ui(sucessos, erros)
            except queue.Empty:
                break

    def _adicionar_arquivos(self):
        diretorio_inicial = self.ultima_pasta_usada if os.path.exists(self.ultima_pasta_usada) else os.path.dirname(os.path.abspath(__file__))
        caminhos = filedialog.askopenfilenames(
            title="Selecione os arquivos PDF",
            initialdir=diretorio_inicial,
            filetypes=[("Arquivos PDF (*.pdf)", "*.pdf"), ("Todos os Arquivos (*.*)", "*.*")]
        )
        if caminhos:
            self.ultima_pasta_usada = os.path.dirname(caminhos[0])
            for c in caminhos:
                c_norm = os.path.abspath(c)
                if c_norm not in self.arquivos_selecionados:
                    self.arquivos_selecionados.append(c_norm)
            self._atualizar_lista_arquivos()

    def _adicionar_pasta(self):
        diretorio_inicial = self.ultima_pasta_usada if os.path.exists(self.ultima_pasta_usada) else os.path.dirname(os.path.abspath(__file__))
        pasta = filedialog.askdirectory(
            title="Selecione a pasta com os PDFs",
            initialdir=diretorio_inicial
        )
        if pasta:
            self.ultima_pasta_usada = pasta
            encontrados = 0
            for item in os.listdir(pasta):
                if item.lower().endswith(".pdf") and not item.endswith("_tarjado.pdf") and not item.endswith("_redigido.pdf"):
                    c_norm = os.path.abspath(os.path.join(pasta, item))
                    if c_norm not in self.arquivos_selecionados:
                        self.arquivos_selecionados.append(c_norm)
                        encontrados += 1
            self._atualizar_lista_arquivos()
            self._log_msg(f"Pasta adicionada: {pasta} ({encontrados} novo(s) PDF(s) encontrado(s))")

    def _remover_selecionados(self):
        selecionados = list(self.listbox_arquivos.curselection())
        for idx in reversed(selecionados):
            del self.arquivos_selecionados[idx]
        self._atualizar_lista_arquivos()

    def _limpar_arquivos(self):
        self.arquivos_selecionados.clear()
        self._atualizar_lista_arquivos()

    def _atualizar_lista_arquivos(self):
        self.listbox_arquivos.delete(0, tk.END)
        for c in self.arquivos_selecionados:
            nome = os.path.basename(c)
            pasta = os.path.dirname(c)
            self.listbox_arquivos.insert(tk.END, f"{nome}  -  ({pasta})")
        qtd = len(self.arquivos_selecionados)
        self.lbl_contagem_arqs.config(text=f"{qtd} arquivo(s) selecionado(s)")

    def _carregar_termos_iniciais(self):
        termos = carregar_termos_config()
        self.txt_termos.delete("1.0", tk.END)
        if termos:
            self.txt_termos.insert(tk.END, "\n".join(termos))
        self.lbl_status.config(text=f"{len(termos)} termo(s) carregados do JSON")

    def _limpar_termos_tela(self):
        if messagebox.askyesno("Limpar Termos", "Deseja limpar todos os termos da caixa de texto?"):
            self.txt_termos.delete("1.0", tk.END)
            self.lbl_status.config(text="Caixa de termos limpa.")

    def _obter_termos(self) -> list[str]:
        conteudo = self.txt_termos.get("1.0", tk.END)
        linhas = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]
        termos = []
        for l in linhas:
            if l.startswith("#"):
                continue
            termo = l.split("  #")[0].strip()
            if termo:
                termos.append(termo)
        return termos

    def _salvar_termos_manual(self):
        termos = self._obter_termos()
        if salvar_termos_config(termos):
            messagebox.showinfo("Salvo", f"{len(termos)} termo(s) sensíveis foram salvos com sucesso no JSON!")
            self.lbl_status.config(text="Termos salvos no JSON com sucesso!")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar os termos no arquivo de configuração.")

    def _ao_fechar(self):
        try:
            termos = self._obter_termos()
            if termos:
                salvar_termos_config(termos)
        except Exception:
            pass
        self.destroy()

    def _log_msg(self, msg: str):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)

    def _abrir_pasta_arquivos(self):
        pasta = self.ultima_pasta_usada
        if self.arquivos_selecionados:
            pasta = os.path.dirname(self.arquivos_selecionados[0])
        if os.path.exists(pasta):
            os.startfile(pasta)
        else:
            messagebox.showinfo("Aviso", f"A pasta não existe mais: {pasta}")

    def _iniciar_processamento(self):
        if self.is_processando:
            return

        if not self.arquivos_selecionados:
            messagebox.showwarning("Nenhum arquivo", "Por favor, selecione ao menos um arquivo PDF para tarjar.")
            return

        termos = self._obter_termos()
        if not termos:
            messagebox.showwarning(
                "Nenhum termo",
                "Por favor, informe ao menos um termo sensível a tarjar na caixa de texto."
            )
            return

        # Salva os termos automaticamente ao iniciar para nunca perder edições
        salvar_termos_config(termos)

        self.is_processando = True
        self.btn_executar.config(state=tk.DISABLED, bg="#94a3b8")
        self.btn_abrir_pasta.config(state=tk.DISABLED)
        self.barra_progresso.config(value=0, maximum=len(self.arquivos_selecionados))
        self.lbl_status.config(text="Processando...")
        self.txt_log.delete("1.0", tk.END)

        thread = threading.Thread(
            target=self._executar_em_background,
            args=(list(self.arquivos_selecionados), termos),
            daemon=True
        )
        thread.start()

    def _executar_em_background(self, arquivos: list[str], termos: list[str]):
        sucessos = 0
        erros = 0
        self.fila_mensagens.put(("LOG", f"=== Iniciando tarjação de {len(arquivos)} arquivo(s) ===\n"))

        for i, caminho in enumerate(arquivos, 1):
            try:
                def cb(msg):
                    self.fila_mensagens.put(("LOG", msg))

                caminho_saida = tarjar(caminho, termos, callback_log=cb)
                sucessos += 1
            except Exception as e:
                erros += 1
                erro_msg = f"[ERRO] Falha ao processar {os.path.basename(caminho)}: {e}"
                self.fila_mensagens.put(("LOG", erro_msg))

            self.fila_mensagens.put(("PROGRESSO", (i, len(arquivos))))

        self.fila_mensagens.put(("FIM", (sucessos, erros)))

    def _finalizar_ui(self, sucessos: int, erros: int):
        self.is_processando = False
        self.btn_executar.config(state=tk.NORMAL, bg="#16a34a")
        self.btn_abrir_pasta.config(state=tk.NORMAL)
        self.lbl_status.config(text="Concluído!")
        self._log_msg(f"=== Finalizado: {sucessos} com sucesso, {erros} erro(s) ===\n")

        if erros == 0:
            messagebox.showinfo(
                "Tarjação Concluída",
                f"{sucessos} arquivo(s) foram tarjados com sucesso!\nOs novos arquivos possuem o sufixo '_tarjado.pdf'."
            )
        else:
            messagebox.showwarning(
                "Processamento com Avisos",
                f"{sucessos} arquivo(s) tarjados com sucesso.\n{erros} arquivo(s) apresentaram erros (verifique o log)."
            )


# Alias de compatibilidade
RedatorPDFApp = TarjadorPDFApp


def main():
    # Se receber arquivos via argumentos na linha de comando, executa em modo CLI
    if len(sys.argv) > 1:
        arquivos = [arg for arg in sys.argv[1:] if arg.lower().endswith(".pdf")]
        if not arquivos:
            print(f"Tarjador de PDFs v{VERSAO_APP}")
            print("Uso: python tarjar_pdf.py <arquivo1.pdf> [arquivo2.pdf ...]")
            sys.exit(1)
        termos = carregar_termos_config()
        if not termos:
            print("Erro: Nenhum termo configurado em 'termos_sensiveis.json'.")
            sys.exit(1)
        print(f"Tarjador de PDFs v{VERSAO_APP}")
        print(f"Processando {len(arquivos)} arquivo(s) em modo texto com {len(termos)} termo(s)...")
        for arq in arquivos:
            try:
                tarjar(arq, termos)
            except Exception as ex:
                print(f"Erro em {arq}: {ex}")
        return

    # Modo padrão: Abre a interface gráfica (GUI)
    app = TarjadorPDFApp()
    app.mainloop()


if __name__ == "__main__":
    main()
