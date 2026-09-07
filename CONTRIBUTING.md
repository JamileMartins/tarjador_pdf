# Guia de Contribuição 🤝

Agradecemos o seu interesse em contribuir com o **Tarjador de PDFs**! Este projeto é de código aberto e qualquer melhoria, correção de bugs ou novas funcionalidades são muito bem-vindas.

---

## 📋 Diretrizes Gerais

1. **Privacidade Absoluta em Primeiro Lugar**:
   - Este software tem como premissa ser **100% offline** e seguro.
   - NUNCA submeta arquivos reais (faturas, holerites, contratos) ou dados confidenciais nos testes, código, issues ou Pull Requests.
   - Sempre utilize dados fictícios/sintéticos nos testes.

2. **Padrão de Código**:
   - Código limpo, legível e em conformidade com as diretrizes do PEP 8.
   - Mantenha comentários descritivos sem expor dados particulares.

---

## 🛠️ Ambiente de Desenvolvimento Local

### 1. Clonar o Repositório e Configurar Ambiente
```bash
git clone https://github.com/JamileMartins/tarjador_pdf.git
cd tarjador_pdf

# Criar e ativar ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executando os Testes Automatizados
Antes de abrir um Pull Request, certifique-se de que todos os testes passem:
```bash
python -m unittest discover -s tests -v
```

### 3. Executando a Aplicação
```bash
python tarjar_pdf.py
```

### 4. Compilando o Executável (.exe)
```bash
pyinstaller --noconsole --onefile --name "TarjadorPDF" --icon "app_icon.ico" --collect-all tkinterdnd2 --clean tarjar_pdf.py
```

---

## 🚀 Fluxo de Trabalho para Pull Requests

1. Crie uma branch para a sua alteração:
   ```bash
   git checkout -b feature/minha-melhoria
   ```
2. Faça as alterações necessárias e adicione testes unitários para o novo comportamento em `tests/test_tarjador.py`.
3. Garanta que a suíte de testes passe integralmente (`python -m unittest discover -s tests`).
4. Faça commit com mensagens descritivas (recomendamos Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`).
5. Abra o Pull Request detalhando as mudanças realizadas.
