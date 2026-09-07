# Tarjador de PDFs Confidenciais 📄🔒

Aplicativo em Python com interface gráfica (Tkinter) para **tarjação profunda e irreversível** de dados sensíveis (nomes, CPFs, endereços, etc.) em documentos PDF.

Diferente de editores que apenas sobrepõem caixas pretas visuais sobre o texto (permitindo que os dados ainda sejam selecionados ou lidos via OCR/extração), o **Tarjador de PDFs** utiliza o [PyMuPDF](https://pymupdf.readthedocs.io/) para expurgar permanentemente os caracteres e objetos do código interno do PDF.

---

## ✨ Funcionalidades

- **Remoção Definitiva**: Os dados confidenciais são destruídos do PDF, impossibilitando cópia ou extração.
- **Interface Gráfica Simples**: Janela moderna para seleção de arquivos, edição de termos e visualização de progresso.
- **Seleção Flexível**:
  - Seleção de múltiplos arquivos avulsos (`Ctrl` ou `Shift`).
  - Adição de pastas inteiras (processa todos os PDFs de um diretório).
- **Sem Dados Hardcoded**: Todos os termos a serem tarjados ficam armazenados em `termos_sensiveis.json`.
- **Criação Automática**: Caso `termos_sensiveis.json` não exista, o aplicativo cria o arquivo automaticamente na primeira execução.
- **Preservação dos Originais**: Os arquivos de entrada nunca são alterados; novos arquivos são gerados com o sufixo `_tarjado.pdf`.
- **100% Offline e Privado**: Nenhum arquivo ou dado sensível é enviado para a internet.

---

## 🚀 Como Usar

### Opção 1: Executável Standalone (Sem instalar Python)
Basta executar o arquivo `TarjadorPDF.exe`.

### Opção 2: Executar via Código-Fonte (Python)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/tarjador-pdf.git
   cd tarjador-pdf
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o programa:**
   ```bash
   python tarjar_pdf.py
   ```

---

## 🛠 Como Compilar o Executável (.exe)

Para gerar um novo executável autônomo com o PyInstaller:

```bash
pyinstaller --noconsole --onefile --name "TarjadorPDF" --clean tarjar_pdf.py
```

O arquivo final estará na pasta `dist/TarjadorPDF.exe`.

---

## 🔒 Segurança e Privacidade ao Publicar

O repositório já inclui um arquivo `.gitignore` configurado para **nunca subir**:
- Arquivos `.pdf` (faturas ou documentos pessoais).
- `termos_sensiveis.json` (arquivo onde ficam salvos os dados sensíveis reais).
- Arquivos compilados (`.exe`, pasta `build/` e `dist/`).

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.
