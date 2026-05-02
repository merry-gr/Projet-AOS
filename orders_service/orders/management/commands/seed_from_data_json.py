import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from orders.models import Order, OrderItem


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone=timezone.utc)
    return dt


@dataclass(frozen=True)
class FixtureRow:
    model: str
    pk: object
    fields: dict


def _load_rows(path: Path) -> list[FixtureRow]:
    data = path.read_bytes()
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        text = data.decode("utf-16")
    else:
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("latin-1")
    raw = json.loads(text)
    rows: list[FixtureRow] = []
    for item in raw:
        rows.append(FixtureRow(model=item["model"], pk=item.get("pk"), fields=dict(item["fields"])))
    return rows


class Command(BaseCommand):
    help = "Seed orders_service DB from the shared Microservices/data.json (legacy fixture format)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=None,
            help="Path to data.json (defaults to ../../data.json from this service root).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        service_root = Path(__file__).resolve().parents[4]  # .../orders_service
        default_path = (service_root / ".." / "data.json").resolve()
        path = Path(options["path"]).resolve() if options["path"] else default_path

        rows = _load_rows(path)
        order_rows = [r for r in rows if r.model == "orders.order"]
        item_rows = [r for r in rows if r.model == "orders.orderitem"]

        created_orders = 0
        updated_orders = 0
        for r in order_rows:
            f = r.fields
            pk = int(r.pk)

            buyer_id = f.get("buyer") or f.get("buyer_id") or 0
            defaults = {
                "buyer_id": int(buyer_id) if buyer_id else 0,
                "status": f.get("status") or "pending",
                "phone": f.get("phone") or "",
                "delivery_address": f.get("delivery_address") or "",
                "city": f.get("city") or "",
                "delivery_note": f.get("delivery_note") or "",
                "payment_method": f.get("payment_method") or "cash",
                "vendor_note": f.get("vendor_note"),
            }

            order, created = Order.objects.update_or_create(id=pk, defaults=defaults)
            if created:
                created_orders += 1
            else:
                updated_orders += 1

            created_at = _parse_dt(f.get("created_at"))
            if created_at is not None:
                Order.objects.filter(id=order.id).update(created_at=created_at)

            est = f.get("estimated_delivery")
            if est:
                try:
                    Order.objects.filter(id=order.id).update(estimated_delivery=est)
                except Exception:
                    pass

        created_items = 0
        updated_items = 0
        for r in item_rows:
            f = r.fields
            pk = int(r.pk)
            order_id = f.get("order")
            if not order_id:
                continue
            product_id = f.get("product") or f.get("product_id") or 0
            defaults = {
                "order_id": int(order_id),
                "product_id": int(product_id) if product_id else 0,
                "quantity": int(f.get("quantity") or 1),
            }
            item, created = OrderItem.objects.update_or_create(id=pk, defaults=defaults)
            if created:
                created_items += 1
            else:
                updated_items += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete.\n"
                f"- orders: created {created_orders}, updated {updated_orders}\n"
                f"- order items: created {created_items}, updated {updated_items}"
            )
        )

