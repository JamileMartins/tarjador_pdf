# Tarjador de PDFs Confidenciais 🛡️ v1.4.0

[![CI](https://github.com/JamileMartins/tarjador_pdf/actions/workflows/ci.yml/badge.svg)](https://github.com/JamileMartins/tarjador_pdf/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Privacy: 100% Offline](https://img.shields.io/badge/Privacidade-100%25%20Offline-success.svg)](SECURITY.md)

Aplicativo desktop com interface gráfica (Tkinter) para **tarjação profunda e irreversível** de dados sensíveis (nomes, CPFs, endereços, etc.) em documentos PDF.

Diferente de editores que apenas sobrepõem caixas pretas visuais sobre o texto (permitindo que os dados ainda sejam selecionados ou lidos via OCR/extração), o **Tarjador de PDFs** utiliza o [PyMuPDF](https://pymupdf.readthedocs.io/) para expurgar permanentemente os caracteres e objetos do código interno do PDF.

---

## ✨ Funcionalidades

- **Remoção Definitiva**: Os dados confidenciais são destruídos do PDF, impossibilitando cópia ou extração.
- **Arrastar e Soltar (Drag & Drop)**:
  - Arraste arquivos `.pdf` ou pastas inteiras diretamente do Windows Explorer para dentro da janela do aplicativo.
- **Pré-visualização Visual de Páginas**:
  - Visualize as páginas de qualquer PDF da fila com paginação anterior/próxima e navegação rápida direto na interface (duplo clique em qualquer item ou clique em *Ver Prévia*).
- **Destino dos Arquivos Customizável**:
  - **Mesma pasta do original**: gera `[nome]_tarjado.pdf` ao lado do arquivo original.
  - **Subpasta 'tarjados/'**: organiza os arquivos gerados em uma subpasta limpa.
  - **Pasta personalizada**: escolha um diretório centralizado para salvar todos os documentos tarjados.
- **Busca Inteligente (Tolerante a Acentos e Caixa)**:
  - Encontra variações como `Patrícia`, `PATRICIA` e `patricia` mesmo pesquisando sem acento ou em minúsculas.
  - Tolera quebras de linha e espaçamentos múltiplos.
- **Detecção Automática por Padrões (Regex)**:
  - Auto-tarjação de qualquer **CPF** detectado (`XXX.XXX.XXX-XX` ou numérico).
  - Auto-tarjação de qualquer **E-mail** detectado.
  - Auto-tarjação de qualquer **Telefone** detectado.
- **Cor da Tarja Customizável**:
  - **Preto Sólido (Padrão)**: tarja tradicional visível.
  - **Branco (Ocultação Limpa)**: oculta o texto mantendo o fundo branco, ideal para impressões limpas.
- **Interface Gráfica Moderna**:
  - Ícone exclusivo da aplicação na barra de títulos e no executável.
  - Barra de progresso e log detalhado em tempo real (processamento em thread assíncrona).
  - Seção integrada de **Sobre / Ajuda** com manual completo para novos usuários.
- **Sem Dados Hardcoded**: Todos os termos personalizados são salvos em `termos_sensiveis.json`.
- **Criação Automática**: Caso `termos_sensiveis.json` não exista, o aplicativo cria o arquivo automaticamente na primeira inicialização.
- **Preservação dos Originais**: Os arquivos de entrada nunca são alterados.
- **100% Offline e Privado**: Nenhum arquivo ou dado sensível é enviado para a internet.

---

## 🚀 Como Usar

### Opção 1: Executável Standalone (Sem instalar Python)
Basta baixar e executar o arquivo `TarjadorPDF.exe` (compatível com Windows 10 e 11) disponível na seção de [Releases](https://github.com/JamileMartins/tarjador_pdf/releases).

### Opção 2: Executar via Código-Fonte (Python)

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/JamileMartins/tarjador_pdf.git
   cd tarjador_pdf
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

## 🧪 Como Executar os Testes Automatizados

O projeto conta com uma suíte completa de testes unitários e de integração utilizando o framework nativo `unittest`:

```bash
python -m unittest discover -s tests -v
```

Os testes utilizam PDFs sintéticos criados em tempo de execução na memória/temp para garantir que o motor de tarjação expurga 100% das informações sensíveis sem necessitar de nenhum documento confidencial real.

---

## 🛠️ Como Compilar o Executável (.exe)

Para gerar um novo executável autônomo com o PyInstaller incluindo ícone e suporte a Drag & Drop:

```bash
pyinstaller --noconsole --onefile --name "TarjadorPDF" --icon "app_icon.ico" --collect-all tkinterdnd2 --clean tarjar_pdf.py
```

O arquivo final estará na pasta `dist/TarjadorPDF.exe`.

---

## 🔒 Segurança e Privacidade ao Publicar

O repositório inclui um arquivo `.gitignore` configurado para **nunca enviar**:
- Arquivos `.pdf` (faturas ou documentos pessoais).
- `termos_sensiveis.json` (arquivo onde ficam salvos os dados sensíveis reais).
- Arquivos compilados (`.exe`, pasta `build/` e `dist/`).

Para mais informações, leia nossa [Política de Segurança](SECURITY.md).

---

## 🤝 Contribuição e Comunidade

Contribuições são muito bem-vindas! Consulte os guias abaixo:
- [Guia de Contribuição](CONTRIBUTING.md)
- [Código de Conduta](CODE_OF_CONDUCT.md)
- [Relatar um Bug](.github/ISSUE_TEMPLATE/bug_report.md)
- [Sugerir Funcionalidade](.github/ISSUE_TEMPLATE/feature_request.md)

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
