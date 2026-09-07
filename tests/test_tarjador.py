# -*- coding: utf-8 -*-
"""
Suíte de testes unitários e de integração para o Tarjador de PDFs.
Testa utilitários, tolerância a acentos, expressões regulares, persistência de termos e o motor de tarjação.
Todos os PDFs são criados sinteticamente em memória/temp (nenhum dado real é exposto).
"""

import os
import sys
import tempfile
import unittest
import pymupdf

# Garante acesso ao módulo raiz
DIRETORIO_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DIRETORIO_RAIZ not in sys.path:
    sys.path.insert(0, DIRETORIO_RAIZ)

import tarjar_pdf
from tarjar_pdf import (
    criar_regex_tolerante,
    obter_caminho_base,
    obter_caminho_config,
    carregar_termos_config,
    salvar_termos_config,
    tarjar,
    PADRAO_CPF,
    PADRAO_EMAIL,
    PADRAO_TELEFONE,
)


class TestUtilidadesRegex(unittest.TestCase):
    """Testes para geração de regex tolerante e identificadores."""

    def test_obter_caminho_base(self):
        base = obter_caminho_base()
        self.assertTrue(isinstance(base, str))
        self.assertTrue(os.path.exists(base))

    def test_criar_regex_tolerante_acentos(self):
        """Testa se o padrão encontra variações com e sem acento e maiúsculas/minúsculas."""
        padrao = criar_regex_tolerante("Patricia")
        self.assertIsNotNone(padrao.search("Patrícia"))
        self.assertIsNotNone(padrao.search("PATRICIA"))
        self.assertIsNotNone(padrao.search("patricia"))
        self.assertIsNotNone(padrao.search("Pátríciá"))

        padrao_joao = criar_regex_tolerante("Joao Conceicao")
        self.assertIsNotNone(padrao_joao.search("João Conceição"))
        self.assertIsNotNone(padrao_joao.search("JOAO  CONCEICAO"))

    def test_regex_cpf(self):
        cpfs_validos = [
            "123.456.789-00",
            "000.111.222-33",
            "999.888.777-66",
            "12345678900",
        ]
        for cpf in cpfs_validos:
            matches = PADRAO_CPF.findall(cpf)
            self.assertTrue(len(matches) > 0, f"Deveria ter casado com o CPF: {cpf}")

    def test_regex_email(self):
        emails_validos = [
            "usuario@dominio.com",
            "maria.fatima@empresa.com.br",
            "dev_teste+tag@sub.exemplo.org",
            "contato123@portal.net",
        ]
        for email in emails_validos:
            matches = PADRAO_EMAIL.findall(email)
            self.assertTrue(len(matches) > 0, f"Deveria ter casado com o E-mail: {email}")

        emails_invalidos = [
            "nao-eh-email",
            "@dominio.com",
            "usuario@",
            "usuario@.com",
        ]
        for inv in emails_invalidos:
            matches = PADRAO_EMAIL.findall(inv)
            self.assertEqual(len(matches), 0, f"Não deveria casar com string inválida: {inv}")

    def test_regex_telefone(self):
        fones_validos = [
            "(11) 98765-4321",
            "(21) 3456-7890",
            "11 98888-7777",
            "+55 11 99999-8888",
            "(31) 91234-5678",
        ]
        for fone in fones_validos:
            matches = PADRAO_TELEFONE.findall(fone)
            self.assertTrue(len(matches) > 0, f"Deveria ter casado com o telefone: {fone}")


class TestConfiguracaoTermos(unittest.TestCase):
    """Testes para carregamento e salvamento de termos sensíveis."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.caminho_json_temp = os.path.join(self.temp_dir.name, "termos_sensiveis.json")
        self.orig_obter_config = tarjar_pdf.obter_caminho_config
        tarjar_pdf.obter_caminho_config = lambda: self.caminho_json_temp

    def tearDown(self):
        tarjar_pdf.obter_caminho_config = self.orig_obter_config
        self.temp_dir.cleanup()

    def test_salvar_e_carregar_termos(self):
        termos_teste = ["TERMO DE TESTE 1", "123.456.789-00", "RUA EXEMPLO, 100"]
        sucesso = salvar_termos_config(termos_teste)
        self.assertTrue(sucesso)
        self.assertTrue(os.path.exists(self.caminho_json_temp))

        termos_lidos = carregar_termos_config()
        self.assertEqual(termos_lidos, termos_teste)

    def test_criacao_automatica_quando_inexistente(self):
        if os.path.exists(self.caminho_json_temp):
            os.remove(self.caminho_json_temp)

        termos = carregar_termos_config()
        self.assertTrue(isinstance(termos, list))
        self.assertTrue(os.path.exists(self.caminho_json_temp))


class TestTarjacaoPDF(unittest.TestCase):
    """Testes de integração com o motor PyMuPDF e PDFs sintéticos."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.pdf_origem = os.path.join(self.temp_dir.name, "fatura_sintetica.pdf")

        doc = pymupdf.open()
        pagina = doc.new_page()
        texto = (
            "Fatura de Teste Confidencial\n\n"
            "Cliente: Maria de Fátima Silva\n"
            "CPF: 123.456.789-00\n"
            "E-mail: maria.fatima@empresa.com.br\n"
            "Telefone: (11) 98765-4321\n\n"
            "Serviço Prestado: Manutenção Mensal\n"
            "Valor Total: R$ 350,00\n"
            "Data de Vencimento: 20/09/2026\n"
        )
        pagina.insert_text((50, 72), texto, fontsize=11)
        doc.save(self.pdf_origem)
        doc.close()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tarjacao_completa_expurgo_irreversivel(self):
        """Valida que os termos sensíveis foram destruídos do PDF e o texto público preservado."""
        # Termo procurado SEM acento propositalmente
        termos = ["Maria de Fatima Silva"]

        logs = []
        caminho_saida = tarjar(
            caminho_entrada=self.pdf_origem,
            termos=termos,
            ignorar_acentos=True,
            tarjar_cpfs=True,
            tarjar_emails=True,
            tarjar_telefones=True,
            cor_tarja="preto",
            modo_pasta_saida="mesma",
            callback_log=lambda m: logs.append(m)
        )

        self.assertTrue(os.path.exists(caminho_saida))
        self.assertTrue(caminho_saida.endswith("_tarjado.pdf"))

        # Inspeciona o código interno do PDF resultante
        doc_tarjado = pymupdf.open(caminho_saida)
        texto_tarjado = doc_tarjado[0].get_text("text")
        doc_tarjado.close()

        # Dados sensíveis NÃO PODEM mais existir no texto
        self.assertNotIn("Maria de Fátima Silva", texto_tarjado)
        self.assertNotIn("123.456.789-00", texto_tarjado)
        self.assertNotIn("maria.fatima@empresa.com.br", texto_tarjado)
        self.assertNotIn("(11) 98765-4321", texto_tarjado)

        # Dados públicos DEVEM permanecer intactos
        self.assertIn("Fatura de Teste Confidencial", texto_tarjado)
        self.assertIn("Valor Total: R$ 350,00", texto_tarjado)
        self.assertIn("Data de Vencimento: 20/09/2026", texto_tarjado)

    def test_modo_pasta_saida_subpasta(self):
        caminho_saida = tarjar(
            caminho_entrada=self.pdf_origem,
            termos=["Maria"],
            modo_pasta_saida="subpasta"
        )
        self.assertTrue(os.path.exists(caminho_saida))
        self.assertIn("tarjados", caminho_saida)

    def test_modo_pasta_saida_custom(self):
        pasta_custom = os.path.join(self.temp_dir.name, "saida_customizada")
        os.makedirs(pasta_custom, exist_ok=True)

        caminho_saida = tarjar(
            caminho_entrada=self.pdf_origem,
            termos=["Maria"],
            modo_pasta_saida="custom",
            pasta_saida_custom=pasta_custom
        )
        self.assertTrue(os.path.exists(caminho_saida))
        self.assertEqual(os.path.dirname(caminho_saida), pasta_custom)

    def test_cor_tarja_branca(self):
        caminho_saida = tarjar(
            caminho_entrada=self.pdf_origem,
            termos=["Maria"],
            cor_tarja="branco"
        )
        self.assertTrue(os.path.exists(caminho_saida))


if __name__ == "__main__":
    unittest.main()
