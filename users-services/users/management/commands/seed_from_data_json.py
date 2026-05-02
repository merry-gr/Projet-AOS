import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from users.models import BuyerProfile, User, VendorProfile


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    # Fixtures often use "Z" for UTC.
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
    help = "Seed users-service DB from the shared Microservices/data.json (legacy fixture format)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default=None,
            help="Path to data.json (defaults to ../../data.json from this service root).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        service_root = Path(__file__).resolve().parents[4]  # .../users-services
        default_path = (service_root / ".." / "data.json").resolve()
        path = Path(options["path"]).resolve() if options["path"] else default_path

        rows = _load_rows(path)

        user_rows = [r for r in rows if r.model == "users.user"]
        vendor_rows = [r for r in rows if r.model == "users.vendorprofile"]
        buyer_rows = [r for r in rows if r.model == "users.buyerprofile"]

        created_users = 0
        updated_users = 0
        for r in user_rows:
            f = r.fields
            pk = int(r.pk)
            defaults = {
                "username": f.get("username") or "",
                "first_name": f.get("first_name") or "",
                "last_name": f.get("last_name") or "",
                "email": f.get("email") or "",
                "is_superuser": bool(f.get("is_superuser", False)),
                "is_staff": bool(f.get("is_staff", False)),
                "is_active": bool(f.get("is_active", True)),
                "role": f.get("role") or "acheteur",
                "validation_status": f.get("validation_status") or "pending",
            }

            user, created = User.objects.update_or_create(id=pk, defaults=defaults)
            if created:
                created_users += 1
            else:
                updated_users += 1

            # Preserve hashed password from the old DB (already encoded).
            pw = f.get("password")
            if pw and user.password != pw:
                User.objects.filter(id=user.id).update(password=pw)

            # Preserve timestamps if present.
            date_joined = _parse_dt(f.get("date_joined"))
            last_login = _parse_dt(f.get("last_login"))
            update_fields = {}
            if date_joined is not None:
                update_fields["date_joined"] = date_joined
            if last_login is not None:
                update_fields["last_login"] = last_login
            if update_fields:
                User.objects.filter(id=user.id).update(**update_fields)

        created_vendor = 0
        updated_vendor = 0
        for r in vendor_rows:
            f = r.fields
            user_id = f.get("user")
            if not user_id:
                continue
            defaults = {
                "company_name": f.get("company_name") or "",
                "phone": f.get("phone") or "",
                "address": f.get("address") or "",
            }
            obj, created = VendorProfile.objects.update_or_create(user_id=int(user_id), defaults=defaults)
            if created:
                created_vendor += 1
            else:
                updated_vendor += 1

        created_buyer = 0
        updated_buyer = 0
        for r in buyer_rows:
            f = r.fields
            user_id = f.get("user")
            if not user_id:
                continue
            defaults = {
                "company_name": f.get("company_name") or "",
                "phone": f.get("phone") or "",
                "address": f.get("address") or "",
            }
            obj, created = BuyerProfile.objects.update_or_create(user_id=int(user_id), defaults=defaults)
            if created:
                created_buyer += 1
            else:
                updated_buyer += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Seed complete.\n"
                f"- users: created {created_users}, updated {updated_users}\n"
                f"- vendor profiles: created {created_vendor}, updated {updated_vendor}\n"
                f"- buyer profiles: created {created_buyer}, updated {updated_buyer}"
            )
        )

