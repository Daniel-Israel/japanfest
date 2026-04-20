from enum import Enum as PyEnum


class OrderStatus(PyEnum):
    queue = "Fila"
    ready = "Pronto"
    delivered = "Entregue"
 
 
class PaymentMethod(PyEnum):
    credit = "Cartão de Crédito"
    debit = "Cartão de Debito"
    cash = "Dinheiro"
    pix = "Pix"
 
 
class MovimentType(PyEnum):
    sale = "Venda"
    restock = "Entrada de Estoque"
    fix = "Ajuste"