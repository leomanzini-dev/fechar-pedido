# fechar-pedido

Função em Python que calcula o total de um pedido de delivery (subtotal, frete, cupom e
mensagens de erro), feita para o processo seletivo simulado da Lince Software (IMMES).

## Regras
Subtotal mínimo de R$ 20,00 · frete R$ 5,00 até 3 km e R$ 9,00 até 8 km (inclusive) ·
frete grátis com subtotal a partir de R$ 100,00 · cupom `LINCE10` (10%, máximo R$ 15,00) ·
cupom `FRETEGRATIS` · qualquer outro cupom é ignorado.

## Como rodar
```bash
python fechar_pedido.py        # imprime a tabela dos 10 casos e os testes extras
pip install pytest
pytest -v                      # 41 testes
python verifica_propriedades.py   # 11 propriedades em 100 mil pedidos aleatórios
```

## Decisão importante
O cálculo usa `Decimal` e arredonda meio centavo para cima. A primeira versão usava `float` e
errava R$ 0,01 em cerca de 0,6% dos pedidos com `LINCE10`.
