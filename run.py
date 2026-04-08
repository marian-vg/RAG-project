from src.rag import responder
from src.utils import print_banner

print_banner()
print("Escribe tu consulta.\n")

while True:
    pregunta = input("> ")
    print("\n" + responder(pregunta) + "\n")