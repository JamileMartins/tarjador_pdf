# Política de Segurança 🔒

A segurança e a privacidade das informações dos usuários são o pilar central do **Tarjador de PDFs**.

---

## 🛡️ Modelo de Privacidade

- **100% Offline**: O aplicativo não realiza requisições de rede, telemetria ou envio de estatísticas para servidores externos.
- **Processamento Puramente Local**: Todo o expurgo e tarjação de dados ocorrem estritamente na memória do seu computador.
- **Expurgo Físico e Irreversível**: Utiliza o motor do PyMuPDF (`apply_redactions()`) para remover permanentemente os glifos, textos e fluxos de dados confidenciais do código interno do PDF, impedindo seleção, cópia ou extração via OCR.

---

## 🚨 Relatando Vulnerabilidades

Se você identificar qualquer problema de segurança, falha de expurgo em layouts específicos de PDF ou risco de vazamento de dados, pedimos a gentileza de nos reportar com responsabilidade:

1. **NÃO crie uma Issue pública** contendo dados confidenciais ou detalhes exploráveis com documentos reais.
2. Abra um relatório através de **Security Advisories** no GitHub do projeto ou contate os mantenedores.
3. Forneça uma descrição do problema e, se possível, um PDF fictício de exemplo (sem dados reais) para reprodução.

Agradecemos seu auxílio em manter os dados de todos protegidos!
