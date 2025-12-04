from graph.promts import ARCH_PROMPT, CORRECTOR_PROMPT, DEVELOPER_PROMPT, SYSADMIN_PROMPT, VERIFIER_PROMPT
from graph.rag_retrieve import rag_configuration
from .utils import format_docs
from .agent_statet import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import re

def nodo_sysadmin_agent(llm: ChatOllama):
    """
    Usa RAG para responder preguntas de SysAdmin Linux y escribe todo en un .md
    
    Args:
        llm: Modelo usado.
        output: RAG chain
    """

    print("\n[ Buscando en conocimiento embebido...]\n")

    retriever = rag_configuration()

    print(" Retrievers combinados correctamente.")
    
    template = SYSADMIN_PROMPT
    
    prompt = ChatPromptTemplate.from_template(template)
    print("Configurando cadena RAG...")
    rag_chain = ({"context": retriever | format_docs, "question": RunnablePassthrough() } | prompt | llm | StrOutputParser())

    return rag_chain, retriever, prompt



def nodo_arquitecto(llm_planificador: ChatOllama, state: AgentState):
    """
    El Arquitecto (Qwen) consulta el RAG y crea el plan de implementación.
    """
    print(f"\n---  ARQUITECTO CONSULTANDO RAG Y PLANIFICANDO... ---")
    
    user_request = state['user_request']
    
    # CONSULTAR RAG PRIMERO
    print(" Paso 1: Consultando conocimiento en RAG...")
    retriever = rag_configuration()
    
    # Buscar información relevante
    docs = retriever.invoke(user_request)
    
    # Formatear el contexto del RAG
    rag_context = "\n\n".join([
        f"--- Fragmento {i+1} ---\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ])
    
    # Extraer páginas
    paginas = set()
    for doc in docs:
        if hasattr(doc, 'metadata') and 'page' in doc.metadata:
            paginas.add(doc.metadata['page'])
    
    if paginas:
        paginas_str = ", ".join(str(p) for p in sorted(paginas))
        print(f" Información encontrada en páginas: {paginas_str}")
    else:
        print("  No se encontró información específica en el RAG")
    
    # GENERAR EL PLAN CON EL CONTEXTO DEL RAG
    print(" Paso 2: Generando plan arquitectónico...")
    
    sys_msg = SystemMessage(content=ARCH_PROMPT)
    
    # Construir el mensaje con contexto RAG
    context_section = ""
    if rag_context.strip():
        context_section = f"""
    
CONTEXTO TÉCNICO EXTRAÍDO DE LA DOCUMENTACIÓN:
{rag_context}

---

"""
    
    human_msg = HumanMessage(content=f"""{context_section}Requerimiento del usuario: {user_request}
Crea el plan de implementación considerando la información técnica proporcionada.""")
    
    response = llm_planificador.invoke([sys_msg, human_msg])
    
    print("\n PLAN DEL ARQUITECTO GENERADO (con contexto RAG)")
    
    return {
        "architect_instructions": response.content,
        "correction_count": 0
    }



def nodo_desarrollador(llm_coder:ChatOllama, state: AgentState):
    """
    El Desarrollador toma el plan y escribe el código .sh final.
    """
    
    instructions = state['architect_instructions']
    
    sys_msg = SystemMessage(content=DEVELOPER_PROMPT)
    
    human_msg = HumanMessage(content=f"""
    Instrucciones del Arquitecto:
    {instructions}
    
    Genera el script ejecutable ahora:
    """)
    
    response = llm_coder.invoke([sys_msg, human_msg])
    
    print("\n SCRIPT GENERADO")
    
    # Limpieza básica por si el modelo añade texto fuera de los backticks
    content = response.content
    patron = r"```(?:bash)?\n(.*?)```"
    coincidencia = re.search(patron, content, re.DOTALL)
    if coincidencia:
        final_code = coincidencia.group(1).strip()
    else:
        final_code = content
        
    return {
        "final_script": final_code
    }


def nodo_verificador(llm_planificador:ChatOllama, state: AgentState):
    """
    El Verificador (Arquitecto) audita el código generado contra el plan original.
    """
    
    instructions = state['architect_instructions']
    script = state.get('corrected_script') or state['final_script']
    user_request = state['user_request']
    correction_count = state.get('correction_count', 0)
    
    sys_msg = SystemMessage(content=VERIFIER_PROMPT)
    
    human_msg = HumanMessage(content=f"""
    SOLICITUD ORIGINAL:
    {user_request}
    
    PLAN ARQUITECTÓNICO:
    {instructions}
    
    CÓDIGO A VERIFICAR:
    {script}
    
    ITERACIÓN: {correction_count + 1}
    
    Realiza la auditoría completa.
    """)
    
    response = llm_planificador.invoke([sys_msg, human_msg])
    
    print("\n REPORTE DE VERIFICACIÓN:")
    print(response.content[:500] + "...\n")
    
    # Determinar si necesita corrección
    needs_correction = "REQUIERE_CORRECCIÓN" in response.content or "REQUIERE CORRECCIÓN" in response.content
    
    return {
        "verification_report": response.content,
        "needs_correction": needs_correction
    }


def nodo_corrector(llm_coder:ChatOllama, state: AgentState):
    """
    El Corrector (Desarrollador) arregla el código según el reporte de verificación.
    """
    
    script = state.get('corrected_script') or state['final_script']
    verification = state['verification_report']
    instructions = state['architect_instructions']
    correction_count = state['correction_count']
    
    sys_msg = SystemMessage(content=CORRECTOR_PROMPT)
    
    human_msg = HumanMessage(content=f"""
    PLAN ARQUITECTÓNICO:
    {instructions}
    
    CÓDIGO CON PROBLEMAS:
    {script}
    
    REPORTE DE AUDITORÍA:
    {verification}
    
    Genera el código CORREGIDO ahora:
    """)
    
    response = llm_coder.invoke([sys_msg, human_msg])
    
    print("\nCÓDIGO CORREGIDO GENERADO")
    
    # Limpieza
    content = response.content
    patron = r"```(?:bash)?\n(.*?)```"
    coincidencia = re.search(patron, content, re.DOTALL)
    if coincidencia:
        corrected_code = coincidencia.group(1).strip()
    else:
        corrected_code = content
    
    return {
        "corrected_script": corrected_code,
        "correction_count": correction_count + 1
    }
