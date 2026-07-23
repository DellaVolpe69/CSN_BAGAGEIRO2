import streamlit as st
from datetime import date
import subprocess
import sys
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO GERAL
# ============================================================================
st.set_page_config(
    page_title="Formulário de Viagens 🚛",
    page_icon="🟧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Imagens do tema (mesmas do app base) ---
url_imagem = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/AppBackground02.png"
url_logo = "https://raw.githubusercontent.com/DellaVolpe69/Images/main/DellaVolpeLogoBranco.png"

# ============================================================================
# CARREGAR MÓDULOS E PARQUETS
# ============================================================================
modulos_dir = Path(__file__).parent / "Modulos"

# Se o diretório ainda não existir, faz o clone direto do GitHub
if not modulos_dir.exists():
    print("📥 Clonando repositório Modulos do GitHub...")
    subprocess.run([
        "git", "clone",
        "https://github.com/DellaVolpe69/Modulos.git",
        str(modulos_dir)
    ], check=True)

# Garante que o diretório está no caminho de importação
if str(modulos_dir) not in sys.path:
    sys.path.insert(0, str(modulos_dir))

from Modulos import ConectionSupaBase
# ============================================================================
# LISTAS DE OPÇÕES
# ============================================================================

# --- Veículos (mesma lista da imagem enviada) ---
VEICULOS = ["3-4", "CARRETA", "CARRETA VANDERLÉIA", "PICAPE-LEVE", "TOCO", "TRUCK"]

# --- Destinos (lista fixa, extraída da planilha data(49).xlsx) --------------
DESTINOS = [
    "BR CIMENTO - PEDRO LEOPOLDO", "BR CIMENTO SOROCABA MOAGEM",
    "CIBR - AGREGADOS SOROCABA", "CIBR ALHANDRA", "CIBR ARCOS",
    "CIBR BARROSO", "CIBR BARUERI", "CIBR CAAPORA", "CIBR CAJAMAR",
    "CIBR CANDEIAS", "CIBR CANTAGALO", "CIBR COCALZINHO DE GOIAS",
    "CIBR CONGONHAS", "CIBR GUARUJA", "CIBR JAZIDA - PEDRO LEOPOLDO",
    "CIBR MAIRIPORA", "CIBR MONTES CLAROS", "CIBR OURICURI",
    "CIBR PERDIZES", "CIBR PORTO ALEGRE", "CIBR RIO DE JANEIRO",
    "CIBR SALTO DO JACUI", "CIBR SANTO ANDRE", "CIBR SAO JOSE DOS CAMPOS",
    "CIBR SAO VICENTE", "CIBR SERRA", "CIBR VOLTA REDONDA",
]

# ============================================================================
# CSS DO TEMA (reaproveitado do app base)
# ============================================================================
st.markdown(
    """
    <style>
    header, [data-testid="stHeader"] { background: transparent; }
    label { color: #EDEBE6 !important; }
    div[role="alert"] p, div[role="alert"] span { color: #EDEBE6 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
                        url("{url_imagem}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        input, textarea {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        .stSelectbox div[data-baseweb="select"] > div {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        .stDateInput input {{
            border: 1px solid white !important;
            border-radius: 5px !important;
        }}
        .stButton > button {{
            background-color: #FF5D01 !important;
            color: #EDEBE6 !important;
            border: 2px solid white !important;
            padding: 0.6em 1.2em;
            border-radius: 10px !important;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: 0.2s ease;
            text-decoration: none !important;
            display: inline-block;
        }}
        .stButton > button:hover {{
            background-color: #993700 !important;
            color: #FF5D01 !important;
            transform: scale(1.03);
            border: 2px solid #FF5D01 !important;
        }}
        .footer {{
            position: fixed; left: 0; bottom: 0; width: 100%;
            background: rgba(0, 0, 0, 0.6); color: white;
            text-align: center; font-size: 14px; padding: 8px 0;
            text-shadow: 1px 1px 2px black;
        }}
        .footer a {{ color: #FF5D01; text-decoration: none; font-weight: bold; }}
        .footer a:hover {{ text-decoration: underline; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def rodape():
    st.markdown(
        """
        <div class="footer">
            © 2026 <b>Della Volpe</b> | Desenvolvido por
            <a href="#">Raphael Chiavegati Oliveira</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def titulo(texto: str):
    st.markdown(
        f"<h1 style='text-align:center; color:#EDEBE6; text-shadow:1px 1px 3px black;'>{texto}</h1>",
        unsafe_allow_html=True,
    )


# ============================================================================
# FUNÇÕES DE GRAVAÇÃO
# ============================================================================
def salvar_destinos_mais_viagem(valefretes, veiculo, destino, periodo):
    # Tabela ValeFreteCSN: NUM_VALE_FRETE, VEICULO, DESTINO, PERIODO
    # Uma linha por Vale Frete preenchido (mesmo veículo/destino/período).
    linhas = [
        {
            "NUM_VALE_FRETE": vf,
            "VEICULO": veiculo,
            "DESTINO": destino,
            "PERIODO": str(periodo),
        }
        for vf in valefretes if vf
    ]
    supabase = ConectionSupaBase.conexao()
    supabase.table("ValeFreteCSN").insert(linhas).execute()
    return linhas


def salvar_rotas_sem_liberacao(destino, periodo):
    # Tabela Autorizacao_CSN: DESTINO, PERIODO (sem veículo)
    registro = {
        "DESTINO": destino,
        "PERIODO": str(periodo),
    }
    supabase = ConectionSupaBase.conexao()
    supabase.table("Autorizacao_CSN").insert(registro).execute()
    return registro


# ============================================================================
# NAVEGAÇÃO
# ============================================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "menu"


def voltar_menu():
    st.session_state.pagina = "menu"


# ----------------------------------------------------------------------------
# MENU PRINCIPAL
# ----------------------------------------------------------------------------
if st.session_state.pagina == "menu":
    st.markdown(
        f"""
        <div style="text-align:center; padding-top:2em;">
            <img src="{url_logo}" alt="Logo Della Volpe"
                 style="width:40%; max-width:200px; height:auto; margin-bottom:10px;">
            <h1 style="color:#EDEBE6; text-shadow:1px 1px 3px black;">Formulário de Viagens</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br><br><br>", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.button(
            "Destinos com Mais de 1 Viagem",
            use_container_width=True,
            on_click=lambda: st.session_state.update(pagina="destinos"),
        )
        st.button(
            "Rotas sem liberação",
            use_container_width=True,
            on_click=lambda: st.session_state.update(pagina="rotas"),
        )
    rodape()

# ----------------------------------------------------------------------------
# PÁGINA 1 - DESTINOS COM MAIS DE 1 VIAGEM
# ----------------------------------------------------------------------------
elif st.session_state.pagina == "destinos":
    titulo("🚛 Destinos com Mais de 1 Viagem")

    st.markdown("<h4 style='color:#EDEBE6;'>Vale Fretes</h4>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        vf1 = st.text_input("Vale Frete 1")
    with c2:
        vf2 = st.text_input("Vale Frete 2")
    with c3:
        vf3 = st.text_input("Vale Frete 3")

    veiculo = st.selectbox("Veículo", VEICULOS)
    destino = st.selectbox("Destino", DESTINOS)
    periodo = st.date_input("Período (data da viagem)", date.today())

    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        b1, b2 = st.columns(2)
        with b1:
            st.button("Voltar ao Menu", use_container_width=True, on_click=voltar_menu)
        with b2:
            if st.button("Salvar", use_container_width=True):
                valefretes = [vf1.strip(), vf2.strip(), vf3.strip()]
                # Regra: página é "mais de 1 viagem" -> exige ao menos 2 vale-fretes.
                # Ajuste o número se sua regra for outra.
                if sum(bool(v) for v in valefretes) < 2:
                    st.warning("⚠️ Preencha ao menos 2 Vale Fretes.")
                else:
                    try:
                        registro = salvar_destinos_mais_viagem(valefretes, veiculo, destino, periodo)
                        st.session_state.registro = registro
                        st.session_state.pagina = "sucesso"
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar no Supabase: {e}")

# ----------------------------------------------------------------------------
# PÁGINA 2 - ROTAS SEM LIBERAÇÃO
# ----------------------------------------------------------------------------
elif st.session_state.pagina == "rotas":
    titulo("🚧 Rotas sem liberação")

    destino = st.selectbox("Destino", DESTINOS)
    periodo = st.date_input("Período (não liberado)", date.today())

    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        b1, b2 = st.columns(2)
        with b1:
            st.button("Voltar ao Menu", use_container_width=True, on_click=voltar_menu)
        with b2:
            if st.button("Salvar", use_container_width=True):
                try:
                    registro = salvar_rotas_sem_liberacao(destino, periodo)
                    st.session_state.registro = registro
                    st.session_state.pagina = "sucesso"
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar no Supabase: {e}")

# ----------------------------------------------------------------------------
# PÁGINA DE SUCESSO (oculta)
# ----------------------------------------------------------------------------
elif st.session_state.pagina == "sucesso":
    st.markdown("<h3 style='color:white;'>Cadastro efetuado!</h3>", unsafe_allow_html=True)
    st.success("✅ Registro salvo com sucesso!")

    # Mostra o que foi gravado em formato de tabela
    if "registro" in st.session_state:
        registro = st.session_state.registro
        dados = registro if isinstance(registro, list) else [registro]
        st.dataframe(dados, use_container_width=True, hide_index=True)

    _, centro, _ = st.columns([1, 1, 1])
    with centro:
        st.button("Ok", use_container_width=True, on_click=voltar_menu)
