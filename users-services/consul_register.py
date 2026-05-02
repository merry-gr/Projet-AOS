import consul
import socket

def register():
    c = consul.Consul(host='consul', port=8500)

    service_name = "users"
    service_id = socket.gethostname()

    c.agent.service.register(
        name=service_name,
        service_id=service_id,
        address="users",
        port=8000
    )