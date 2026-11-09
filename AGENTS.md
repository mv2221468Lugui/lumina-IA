# Lumina AI - orientações de revisão

- Preservar o banco real `lumina.db` e os arquivos de dados do usuário.
- Testes devem usar SQLite temporário, nunca dados reais.
- Regra de despesas: exclusão por ID não pode apagar outro registro.
- Executar `python run_tests.py` antes de propor integração.
- Registrar regra, diff, teste, resultado e commit; não afirmar execução não observada.
- Não inserir chaves de API no repositório ou em logs.
