import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product


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
            # Some Windows exports can contain legacy encodings; fallback to latin-1.
            text = data.decode("latin-1")
    raw = json.loads(text)
    rows: list[FixtureRow] = []
    for item in raw:
        rows.append(FixtureRow(model=item["model"], pk=item.get("pk"), fields=dict(item["fields"])))
    return rows


def _none_if_blank(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


class Command(BaseCommand):
    help = "Seed product_service DB from the shared Microservices/data.json (legacy fixture format)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=None,
            help="Path to data.json (defaults to ../../data.json from this service root).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        service_root = Path(__file__).resolve().parents[4]  # .../product_service
        default_path = (service_root / ".." / "data.json").resolve()
        path = Path(options["path"]).resolve() if options["path"] else default_path

        rows = _load_rows(path)
        product_rows = [r for r in rows if r.model == "products.product"]

        created = 0
        updated = 0
        for r in product_rows:
            f = r.fields
            pk = int(r.pk)

            # Legacy export used "vendor" (FK). Our service stores vendor_id int.
            vendor_id = f.get("vendor") or f.get("vendor_id") or 0

            defaults = {
                "vendor_id": int(vendor_id) if vendor_id else 0,
                "name": f.get("name") or "",
                "description": f.get("description") or "",
                "category": f.get("category") or "other",
                "price": Decimal(str(f.get("price") or "0")),
                "stock": int(f.get("stock") or 0),
            }

            obj, was_created = Product.objects.update_or_create(id=pk, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

            # Images: the fixture stores file paths; ImageField can store the name.
            img_updates = {
                "image": _none_if_blank(f.get("image")),
                "image2": _none_if_blank(f.get("image2")),
                "image3": _none_if_blank(f.get("image3")),
                "image4": _none_if_blank(f.get("image4")),
            }
            img_updates = {k: v for k, v in img_updates.items() if v is not None}
            if img_updates:
                Product.objects.filter(id=obj.id).update(**img_updates)

        self.stdout.write(self.style.SUCCESS(f"Seed complete. products: created {created}, updated {updated}"))

