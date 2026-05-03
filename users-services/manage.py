#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Tentative d'enregistrement sur Consul uniquement si on ne fait pas une migration
    # On évite d'enregistrer le service pendant 'makemigrations' ou 'migrate'
    if len(sys.argv) > 1 and sys.argv[1] not in ['makemigrations', 'migrate', 'collectstatic']:
        try:
            from consul_register import register
            register()
            print("✅ Service enregistré sur Consul avec succès.")
        except Exception as e:
            print(f"⚠️ Consul n'est pas disponible (le service ne sera pas enregistré) : {e}")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()