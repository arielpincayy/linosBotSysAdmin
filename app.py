from graph.departments import bashScripting
from langchain_ollama import ChatOllama
from graph.departments import sysadmin_agent
from langchain_core.prompts import ChatPromptTemplate
from graph.utils import Greettings
from graph.promts import ROUTER_PROMPT
import gc

MODELO_PLANIFICADOR = "qwen2.5-coder:3b" 
MODELO_CODER = "qwen2.5-coder:3b"
MODELO_LINUX_EXPERT = "qwen2.5-coder:3b"
MODELO_ROUTER = "qwen2.5:1.5b"



llm_router = ChatOllama(model=MODELO_ROUTER, temperature=0.0, keep_alive=0)
llm_arch = ChatOllama(model=MODELO_PLANIFICADOR, temperature=0.1, top_p=0.8, top_k=40, repeat_penalty=1.08, keep_alive=0)
llm_linux_expert = ChatOllama(model=MODELO_LINUX_EXPERT, temperature=0.3, top_p=0.7, top_k=30, repeat_penalty=1.2, keep_alive=0)
llm_coder = ChatOllama(model=MODELO_CODER, temperature=0.1, top_p=0.7, top_k=30, repeat_penalty=1.1, keep_alive=0)


router_prompt = ChatPromptTemplate.from_template(ROUTER_PROMPT)


def router_decision(pregunta: str) -> str:
    """Devuelve: sysadmin_rag | bash_script | otro"""
    result = (router_prompt | llm_router | (lambda x: x.content.strip())).invoke(
        {"pregunta": pregunta}
    )
    return result.lower()


def router_handler(pregunta: str):
    """Selecciona automáticamente qué pipeline ejecutar."""
    decision = router_decision(pregunta)
    print(f"\nRouter decidió: {decision}\n")

    if decision == "sysadmin_rag":
        show_sources = bool(input("¿Deseas mostrar las fuentes? (Sí | No): ") == 'Sí')
        print("Enviando a *sysadmin_agent* con RAG...")
        sysadmin_agent(llm_linux_expert, pregunta, show_sources)

    elif decision == "bash_script":
        print("Enviando a *Generador de Scripts Bash*...")
        bashScripting(llm_arch, llm_coder, pregunta)

    else:
        print("No clasificable. Respuesta simple:")
        respuesta = llm_router.invoke(f"Responde brevemente: {pregunta}")
        print(respuesta)


if __name__ == "__main__":

    Greettings(100)

    while True:
        entrada = input("\nCharlemos :D (Si ya no quieres hablar escribe 'salir', 'exit' o 'quit' :c)\n> ").strip()
        if entrada.lower() in ("salir", "exit", "quit"):
            gc.collect()
            llm_arch = None
            llm_router = None
            llm_linux_expert = None
            llm_coder = None
            break
        router_handler(entrada)
