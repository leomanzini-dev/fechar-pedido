"""Tenta quebrar fechar_pedido com pedidos aleatórios.

Em vez de conferir valores fixos, confere propriedades que SEMPRE devem valer
(derivadas das 10 regras do enunciado). Rodar: python verifica_propriedades.py
"""
import random
import re
from decimal import Decimal

from fechar_pedido import fechar_pedido

FORMATO_OK = re.compile(r"^R\$ \d+,\d{2}$")
ERROS = {
    "ERRO: item inválido",
    "ERRO: pedido mínimo de R$ 20,00",
    "ERRO: fora da área de entrega",
}


def valor(saida):
    """'R$ 55,00' -> Decimal('55.00')"""
    return Decimal(saida[3:].replace(",", "."))


def pedido_aleatorio(rnd):
    itens = [(round(rnd.uniform(0, 70), 2), rnd.randint(1, 4)) for _ in range(rnd.randint(1, 4))]
    km = rnd.choice([0, 0.5, 2.99, 3, 3.01, 5, 7.99, 8, 8.01, 12])
    return itens, km


def subtotal_de(itens):
    return sum(Decimal(str(p)) * q for p, q in itens)


def main(n=100000, semente=7):
    rnd = random.Random(semente)
    falhas = []

    def checa(nome, ok, contexto):
        if not ok:
            falhas.append((nome, contexto))

    for _ in range(n):
        itens, km = pedido_aleatorio(rnd)
        cupom = rnd.choice(["", "LINCE10", "FRETEGRATIS", "XYZ"])
        sub = subtotal_de(itens)
        base = fechar_pedido(itens, km, "")
        saida = fechar_pedido(itens, km, cupom)
        ctx = (itens, km, cupom, saida)

        # P1: a saída é sempre um valor no formato certo OU uma das 3 mensagens exatas
        checa("P1 formato", FORMATO_OK.match(saida) or saida in ERROS, ctx)

        # P2: prioridade dos erros
        if sub < 20:
            checa("P2 mínimo", saida == "ERRO: pedido mínimo de R$ 20,00", ctx)
        elif km > 8:
            checa("P2 área", saida == "ERRO: fora da área de entrega", ctx)

        # P3: cupom não muda se o pedido é aceito ou recusado (regra 8)
        checa("P3 cupom não cria nem tira erro", (saida in ERROS) == (base in ERROS), ctx)

        if saida not in ERROS:
            total, total_base = valor(saida), valor(base)
            # P4: total nunca fica abaixo de 0 nem passa de subtotal + 9
            checa("P4 limites", 0 <= total <= sub + 9, ctx)
            # P5: LINCE10 tira no máximo 15 e nunca aumenta o total
            if cupom == "LINCE10":
                checa("P5 teto 15", total_base - Decimal("15.00") <= total <= total_base, ctx)
            # P6: FRETEGRATIS nunca aumenta; se havia frete, tira só o frete (5 ou 9)
            if cupom == "FRETEGRATIS":
                checa("P6 frete", total_base - total in (0, Decimal("5.00"), Decimal("9.00")), ctx)
            # P7: cupom desconhecido = sem cupom
            if cupom in ("", "XYZ"):
                checa("P7 cupom ignorado", saida == base, ctx)
            # P8: maiúsculas/minúsculas e espaços não mudam nada
            if cupom:
                variantes = ["  " + cupom.lower() + " ", cupom.title(), "\t" + cupom + "\n"]
                checa("P8 caixa e espaços", all(fechar_pedido(itens, km, v) == saida for v in variantes), ctx)

        # P9: a ordem dos itens não importa
        embaralhado = itens[:]
        rnd.shuffle(embaralhado)
        checa("P9 ordem dos itens", fechar_pedido(embaralhado, km, cupom) == saida, ctx)

        # P10: um item com quantidade 0 sempre invalida, mesmo com o resto perfeito
        checa("P10 item inválido ganha", fechar_pedido(itens + [(1.0, 0)], 20, cupom) == "ERRO: item inválido", ctx)

        # P11: longe demais nunca é mais barato que perto, enquanto ainda há entrega
        if km <= 8 and saida not in ERROS:
            perto = fechar_pedido(itens, 0, cupom)
            checa("P11 frete cresce com a distância", valor(perto) <= valor(saida), ctx)

    print(f"{n} pedidos aleatórios, {len(falhas)} violações")
    por_nome = {}
    for nome, ctx in falhas:
        por_nome.setdefault(nome, []).append(ctx)
    for nome, ctxs in por_nome.items():
        print(f"- {nome}: {len(ctxs)} casos, exemplo: {ctxs[0]}")
    return len(falhas)


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
