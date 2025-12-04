from langchain_ollama import ChatOllama
from .agent_statet import AgentState
from typing import Literal
from graph.nodes import nodo_arquitecto, nodo_corrector, nodo_desarrollador, nodo_verificador
from langgraph.graph import StateGraph, END
from functools import partial


def decidir_siguiente_paso(state: AgentState, ntrials:int=2) -> Literal["corrector", "fin"]:
    """
    Decide si enviar a corrección o terminar.
    Límite: máximo 2 correcciones para evitar loops infinitos.
    """
    needs_correction = state.get('needs_correction', False)
    correction_count = state.get('correction_count', 0)
    
    # Límite de seguridad
    if correction_count >= ntrials:
        print(f"\nLÍMITE DE CORRECCIONES ALCANZADO ({correction_count}). Finalizando...")
        return "fin"
    
    if needs_correction:
        print(f"\nSe detectaron problemas. Enviando a corrección (intento {correction_count + 1}/{ntrials})...")
        return "corrector"
    else:
        print(f"\nCódigo APROBADO. Finalizando...")
        return "fin"


def bashscripting_workflow(llm_planificador:ChatOllama, llm_coder:ChatOllama):
    workflow = StateGraph(AgentState)

    # Agregamos los nodos
    workflow.add_node("arquitecto", partial(nodo_arquitecto, llm_planificador))
    workflow.add_node("desarrollador", partial(nodo_desarrollador, llm_coder))
    workflow.add_node("verificador", partial(nodo_verificador, llm_planificador))
    workflow.add_node("corrector", partial(nodo_corrector, llm_coder))
    
    # Definimos el flujo
    workflow.set_entry_point("arquitecto")
    workflow.add_edge("arquitecto", "desarrollador")
    workflow.add_edge("desarrollador", "verificador")
    
    # Condicional: ¿necesita corrección?
    workflow.add_conditional_edges(
        "verificador",
        decidir_siguiente_paso,
        {
            "corrector": "corrector",
            "fin": END
        }
    )
    
    # El corrector vuelve al verificador
    workflow.add_edge("corrector", "verificador")
    
    app = workflow.compile()

    return app