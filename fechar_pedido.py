from decimal import Decimal, ROUND_HALF_UP  # biblioteca padrão do Python (não é externa)


def fechar_pedido(itens, distancia_km, cupom):
    # Regras 1 e 2: soma o subtotal e recusa o pedido se algum item for inválido
    subtotal = Decimal("0")
    for preco, quantidade in itens:
        if quantidade <= 0 or preco < 0:  # preço 0 é permitido, por isso "< 0"
            return "ERRO: item inválido"
        subtotal = subtotal + Decimal(str(preco)) * quantidade  # Decimal: dinheiro exato

    # Regra 3: pedido mínimo (exatamente 20,00 é válido)
    if subtotal < 20:
        return "ERRO: pedido mínimo de R$ 20,00"

    # Regra 4: frete por distância (3 e 8 km entram na faixa mais barata)
    if distancia_km <= 3:
        frete = Decimal("5.00")
    elif distancia_km <= 8:
        frete = Decimal("9.00")
    else:
        return "ERRO: fora da área de entrega"

    # Regra 5: frete grátis olha o subtotal ANTES do desconto (regra 8)
    if subtotal >= 100:
        frete = Decimal("0.00")

    # Regras 6 e 7: cupom sem espaços nas pontas e sem diferença de maiúscula
    cupom = cupom.strip().upper()
    desconto = Decimal("0.00")
    if cupom == "LINCE10":
        desconto = min(subtotal * Decimal("0.10"), Decimal("15.00"))  # 10%, limite R$ 15
    elif cupom == "FRETEGRATIS":
        frete = Decimal("0.00")
    # qualquer outro cupom cai fora dos dois "if": é ignorado, sem erro

    # Regra 10: total com 2 casas (meio centavo sobe), vírgula decimal e "R$ " na frente
    total = (subtotal - desconto + frete).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "R$ " + str(total).replace(".", ",")


# ---------------------------------------------------------------------------
# TESTES
# ---------------------------------------------------------------------------
CASOS_PUBLICOS = [
    # (caso, itens, km, cupom, esperado)
    (1, [(25.00, 2)], 2, "", "R$ 55,00"),
    (2, [(12.50, 1), (8.00, 2)], 5, "", "R$ 37,50"),
    (3, [(15.00, 1)], 1, "", "ERRO: pedido mínimo de R$ 20,00"),
    (4, [(40.00, 3)], 6, "", "R$ 120,00"),
    (5, [(30.00, 2)], 2, "LINCE10", "R$ 59,00"),
    (6, [(90.00, 2)], 4, "LINCE10", "R$ 165,00"),
    (7, [(22.00, 1)], 9, "", "ERRO: fora da área de entrega"),
    (8, [(22.00, 1)], 3, "  fretegratis ", "R$ 22,00"),
    (9, [(10.00, 0)], 2, "", "ERRO: item inválido"),
    (10, [(25.00, 1)], 8, "CUPOMFAKE", "R$ 34,00"),
]

CASOS_EXTRAS = [
    # --- subtotal (fronteiras do pedido mínimo e do frete grátis) ---
    ("E1 subtotal = 20,00", [(20.00, 1)], 1, "", "R$ 25,00"),
    ("E2 subtotal = 19,99", [(19.99, 1)], 1, "", "ERRO: pedido mínimo de R$ 20,00"),
    ("E3 subtotal = 100,00", [(100.00, 1)], 2, "", "R$ 100,00"),
    ("E4 subtotal = 99,99", [(99.99, 1)], 2, "", "R$ 104,99"),
    ("E5 ruído de float (12,10 + 7,90 = 20)", [(12.10, 1), (7.90, 1)], 1, "", "R$ 25,00"),
    # --- distância (fronteiras do frete) ---
    ("E6 km = 3", [(25.00, 1)], 3, "", "R$ 30,00"),
    ("E7 km = 3,01", [(25.00, 1)], 3.01, "", "R$ 34,00"),
    ("E8 km = 8", [(25.00, 1)], 8, "", "R$ 34,00"),
    ("E9 km = 8,01", [(25.00, 1)], 8.01, "", "ERRO: fora da área de entrega"),
    # --- itens ---
    ("E10 preço 0 + outro item", [(0.00, 5), (25.00, 1)], 2, "", "R$ 30,00"),
    ("E11 só preço 0 (subtotal 0 -> mínimo)", [(0.00, 1)], 2, "", "ERRO: pedido mínimo de R$ 20,00"),
    ("E12 quantidade = 0", [(25.00, 0)], 2, "", "ERRO: item inválido"),
    ("E13 quantidade negativa", [(25.00, -1)], 2, "", "ERRO: item inválido"),
    ("E14 preço negativo", [(-1.00, 1), (25.00, 1)], 2, "", "ERRO: item inválido"),
    # --- LINCE10 ---
    ("E15 LINCE10 desconto < 15", [(50.00, 1)], 2, "LINCE10", "R$ 50,00"),
    ("E16 LINCE10 desconto = 15 (subtotal 150)", [(150.00, 1)], 2, "LINCE10", "R$ 135,00"),
    ("E17 LINCE10 desconto > 15 (limite)", [(200.00, 1)], 2, "LINCE10", "R$ 185,00"),
    ("E18 LINCE10 em subtotal 100 (frete grátis pelo subtotal antes do desconto)", [(100.00, 1)], 2, "LINCE10", "R$ 90,00"),
    ("E19 mínimo olha subtotal antes do desconto (21 - 2,10 < 20)", [(21.00, 1)], 2, "LINCE10", "R$ 23,90"),
    ("E20 lince10 minúsculo", [(30.00, 2)], 2, "lince10", "R$ 59,00"),
    ("E21 ' LINCE10 ' com espaços", [(30.00, 2)], 2, " LINCE10 ", "R$ 59,00"),
    # --- FRETEGRATIS e outros cupons ---
    ("E22 ' fretegratis ' km 8", [(25.00, 1)], 8, " fretegratis ", "R$ 25,00"),
    ("E23 FRETEGRATIS não dá desconto no subtotal", [(30.00, 1)], 2, "FRETEGRATIS", "R$ 30,00"),
    ("E24 cupom inexistente", [(25.00, 1)], 2, "DESCONTO50", "R$ 30,00"),
    ("E25 dois cupons juntos são ignorados", [(30.00, 1)], 2, "LINCE10 FRETEGRATIS", "R$ 35,00"),
    ("E26 cupom só com espaços", [(25.00, 1)], 2, "   ", "R$ 30,00"),
    # --- prioridade dos erros ---
    ("E27 item inválido + mínimo + fora da área", [(-5.00, 1)], 20, "", "ERRO: item inválido"),
    ("E28 mínimo + fora da área", [(10.00, 1)], 20, "", "ERRO: pedido mínimo de R$ 20,00"),
    ("E29 item inválido depois de itens bons", [(25.00, 1), (10.00, 0)], 20, "", "ERRO: item inválido"),
    ("E30 fora da área mesmo com subtotal alto e FRETEGRATIS", [(200.00, 1)], 9, "FRETEGRATIS", "ERRO: fora da área de entrega"),
]


def rodar_publicos():
    print("| Caso | Chamada | Esperado | Obtido | Passou? |")
    print("|---|---|---|---|---|")
    falhas = 0
    for caso, itens, km, cupom, esperado in CASOS_PUBLICOS:
        obtido = fechar_pedido(itens, km, cupom)
        passou = obtido == esperado
        falhas += not passou
        chamada = f"fechar_pedido({itens}, {km}, {cupom!r})"
        print(f"| {caso} | `{chamada}` | {esperado} | {obtido} | {'Sim' if passou else 'NÃO'} |")
    return falhas


def rodar_extras():
    falhas = 0
    for nome, itens, km, cupom, esperado in CASOS_EXTRAS:
        obtido = fechar_pedido(itens, km, cupom)
        passou = obtido == esperado
        falhas += not passou
        print(f"{'OK  ' if passou else 'FALHA'} {nome}: esperado={esperado!r} obtido={obtido!r}")
    return falhas


if __name__ == "__main__":
    f1 = rodar_publicos()
    print()
    f2 = rodar_extras()
    print()
    print(f"Públicos: {10 - f1}/10 | Extras: {len(CASOS_EXTRAS) - f2}/{len(CASOS_EXTRAS)}")
