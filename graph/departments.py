import datetime
import os
from graph.workflow import bashscripting_workflow
from langchain_ollama import ChatOllama
from .nodes import nodo_sysadmin_agent
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from .utils import format_docs, render_mds

OUTPUT_CODES = "output_codes"
os.makedirs(OUTPUT_CODES, exist_ok=True)

def sysadmin_agent(llm: ChatOllama, pregunta: str, show_sources: bool=True):
    """
    Usa RAG para responder preguntas de SysAdmin Linux y escribe todo en un .md
    
    Args:
        pregunta: La consulta del usuario
        verbose: Mostrar los fragmentos recuperados
        output_file: Nombre del archivo de salida .md
    """

    rag_chain, retriever, prompt = nodo_sysadmin_agent(llm)
    
    rag_chain = ({"context": retriever | format_docs, "question": RunnablePassthrough() } | prompt | llm | StrOutputParser())
    
    docs = retriever.invoke(pregunta)

    # Generar respuesta
    respuesta = rag_chain.invoke(pregunta)

    # Crear contenido del .md
    md_content = f"# Respuesta del agente SysAdmin\n\n"
    md_content += f"**Pregunta:** {pregunta}\n\n"
    md_content += f"## Respuesta\n\n{respuesta}\n\n"
    md_content += f"## Fuentes utilizadas ({len(docs)})\n"

    if show_sources:
        for i, doc in enumerate(docs, 1):
            md_content += f"\n### Fuente {i}\n"
            md_content += f"{doc.page_content}\n"
            if hasattr(doc, 'metadata') and doc.metadata:
                md_content += f"\n**Metadata:** {doc.metadata}\n"

    render_mds(md_content)


def bashScripting(llm_planificador:ChatOllama, llm_coder:ChatOllama, user_input:str):
    app = bashscripting_workflow(llm_planificador, llm_coder)
    
    # Ejecutamos el grafo
    inputs = {
        "user_request": user_input,
        "architect_instructions": "",
        "final_script": "",
        "verification_report": "",
        "needs_correction": False,
        "correction_count": 0,
        "corrected_script": ""
    }
    
    # Invocación
    print("="*60 + "\n")
    print("Empezando el flujo de trabajo")
    result = app.invoke(inputs)
    
    # Guardado de archivos
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Guardar Plan
    plan_file = os.path.join(OUTPUT_CODES, f"plan_{timestamp}.txt")
    with open(plan_file, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("PLAN ARQUITECTÓNICO\n")
        f.write("="*60 + "\n\n")
        f.write(result["architect_instructions"])
    
    # 2. Guardar Script Original
    original_file = os.path.join(OUTPUT_CODES, f"script_{timestamp}_original.sh")
    with open(original_file, "w", encoding="utf-8") as f:
        f.write(result["final_script"])
    
    # 3. Guardar Reporte de Verificación
    report_file = os.path.join(OUTPUT_CODES, f"verification_{timestamp}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("REPORTE DE VERIFICACIÓN\n")
        f.write("="*60 + "\n\n")
        f.write(result["verification_report"])
    
    # 4. Guardar Script Final (corregido si aplica)
    final_script = result.get('corrected_script') or result['final_script']
    final_file = os.path.join(OUTPUT_CODES, f"script_{timestamp}_final.sh")
    with open(final_file, "w", encoding="utf-8") as f:
        f.write(final_script)

    print(f"Script refinado guardado en: {os.path.join(os.getcwd(), final_file)}")

