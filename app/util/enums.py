from enum import Enum as PyEnum


class OrderStatus(PyEnum):
    queue = "Fila"
    ready = "Pronto"
    delivered = "Entregue"
    canceled = "Cancelado"
 
 
class PaymentMethod(PyEnum):
    credit = "Cartão de Crédito"
    debit = "Cartão de Débito"
    cash = "Dinheiro"
    pix = "Pix"
 
 
class MovementType(PyEnum):
    sale = "Venda"
    restock = "Entrada de Estoque"
    fix = "Ajuste"


class IncludeOptions(PyEnum):
    items = "items"


class SortOptions(PyEnum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    status = "status"


class SortOrderOptions(PyEnum):
    asc = "asc"
    desc = "desc"
