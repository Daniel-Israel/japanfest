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
    staff = "Staff"
    loss = "Perda"
    donation = "Doação"


class ReceiptType(PyEnum):
    client = "Cliente"
    kitchen = "Cozinha"


class ReceiptStatus(PyEnum):
    pending = "Pendente"
    printed = "Impresso"
    error = "Erro"


class MovementType(PyEnum):
    sale = "Venda"
    restock = "Entrada de Estoque"
    fix = "Ajuste"
    staff = "Staff"
    loss = "Perda"
    donation = "Doação"


class IncludeOptions(PyEnum):
    items = "items"
    items_and_customizations = "items_and_customizations"


class SortOptions(PyEnum):
    id = "id"
    created_at = "created_at"
    updated_at = "updated_at"
    status = "status"


class SortOrderOptions(PyEnum):
    asc = "asc"
    desc = "desc"


class LossType(PyEnum):
    staff = "Staff"
    loss = "Perda"
    donation = "Doação"
