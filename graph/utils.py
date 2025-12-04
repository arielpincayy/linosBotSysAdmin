from rich.console import Console
from rich.markdown import Markdown

console = Console()
def render_mds(text_md):
    md = Markdown(text_md)
    console.print(md)


def format_docs(docs):
    """Formatea los documentos recuperados"""
    return "\n\n".join(doc.page_content for doc in docs)


def Greettings(width=60):
    # Definimos colores ANSI (funcionan nativamente en Linux/Bash)
    COLOR_CYAN = "\033[96m"
    COLOR_RESET = "\033[0m"
    
    print(f"--- Cargando modelos en memoria (GPU) ---")
    
    print("=" * width)
    
    title = "Hola, soy Linos"
    subtitle = "Tu asistente personal de sysadmin para Linux."
    
    # Centrado de texto normal
    print(title.center(width))
    print(subtitle.center(width))
    print("Estoy aquí para ayudarte con tus necesidades de administración de sistemas y scripting.\n".center(width))
    
    ascii_art = r"""
     _      _                 
    | |    (_)                
    | |     _ _ __   ___  ___ 
    | |    | | '_ \ / _ \/ __|
    | |____| | | | | (_) \__ \
    \_____/|_|_| |_|\___/|___/
    """
    
    lines = [line for line in ascii_art.split("\n") if line]
    
    if lines:
        max_line_length = max(len(line) for line in lines)
        
        padding_left = (width - max_line_length) // 2
        margin = " " * padding_left
    
        print(COLOR_CYAN) # Activamos color
        for line in lines:
            print(margin + line)
        print(COLOR_RESET) # Desactivamos color (muy importante)
    
    print("=" * width)