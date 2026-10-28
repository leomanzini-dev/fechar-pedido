import pytest

from fechar_pedido import CASOS_EXTRAS, CASOS_PUBLICOS, fechar_pedido


@pytest.mark.parametrize("caso, itens, km, cupom, esperado", CASOS_PUBLICOS)
def test_casos_publicos(caso, itens, km, cupom, esperado):
    assert fechar_pedido(itens, km, cupom) == esperado


@pytest.mark.parametrize("nome, itens, km, cupom, esperado", CASOS_EXTRAS)
def test_casos_extras(nome, itens, km, cupom, esperado):
    assert fechar_pedido(itens, km, cupom) == esperado


def test_meio_centavo_sobe():
    # 32,65 - 3,265 + 5,00 = 34,385 -> 34,39 (com float dava 34,38)
    assert fechar_pedido([(32.65, 1)], 3, "LINCE10") == "R$ 34,39"
