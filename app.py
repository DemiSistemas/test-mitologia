import streamlit as st
from supabase import create_client

# Si el nombre técnico de la columna en Supabase es distinto, cambialo aquí.
TABLE_NAME = "campistas"
CIRSE_COLUMN = "cirse"
MITOLOGIA_COLUMN = "mitologia"

MYTHS = {"G": "Griega", "R": "Romana", "N": "Nórdica", "E": "Egipcia"}
# Desempate fijo: Griega, Romana, Nórdica, Egipcia.
TIE_ORDER = ["G", "R", "N", "E"]

QUESTIONS = [
    ("Mascota elegida", [
        ("Gato siamés", {"E": 1}), ("Husky", {"R": 1}),
        ("Golden Retriever", {"G": 1}), ("San Bernardo", {"N": 2}),
        ("Gato naranja", {"G": 2}), ("Galgo", {"E": 2}),
        ("Fox Terrier", {"N": 1}), ("Ovejero alemán", {"R": 2}),
    ]),
    ("Animal identificado", [
        ("Delfín", {"G": 1, "E": 1}), ("Caballo", {"G": 1, "R": 1}),
        ("Conejo", {"N": 1}), ("Serpiente", {"E": 1, "N": 1}),
        ("Ciervo", {"N": 1, "R": 1}), ("León", {"E": 1}),
        ("Águila", {"R": 1, "G": 1}),
    ]),
    ("Arma", [
        ("Espada", {"G": 1, "R": 1}), ("Lanza", {"R": 1, "E": 1}),
        ("Hacha", {"N": 2}), ("Arco y flecha", {"N": 1, "G": 1}),
        ("Martillo", {"N": 1}), ("Maza", {"E": 2}),
        ("Daga", {"G": 1}), ("Escudo", {"R": 2}),
    ]),
    ("Personaje", [
        ("Obi-Wan", {"R": 1}), ("Gimli", {"N": 1}), ("Peeta", {"G": 1}),
        ("Hawkeye", {"E": 1}), ("Sr. Spock", {"N": 1}),
        ("Burro", {"G": 1}), ("Poison Ivy", {"E": 1}),
    ]),
    ("Villano que enfrentarías", [
        ("Palpatine", {"R": 2}), ("Voldemort", {"G": 1}),
        ("Presidente Snow", {"N": 1}), ("Sauron", {"N": 1}),
        ("Reina Cersei", {"E": 1}), ("Jaffar", {"E": 1}),
        ("Ultron", {"G": 1}), ("Lex Luthor", {"R": 1}),
    ]),
    ("Juego que preferís", [
        ("Piedra, papel o tijera", {"G": 1}), ("Dígalo con mímica", {"G": 1}),
        ("Tutti-Frutti", {"R": 1}), ("Juegos de manos", {"N": 1}),
        ("Adivinanzas", {"E": 1}), ("Truco", {"N": 1}),
        ("Generala (dados)", {"R": 1}),
    ]),
    ("Ante un conflicto", [
        ("Hago lo que tengo que hacer", {"R": 1}), ("Improviso", {"G": 1}),
        ("Ataco", {"N": 1}), ("Busco opciones", {"E": 1}),
    ]),
    ("Un punto cardinal", [
        ("Norte", {"N": 1}), ("Sur", {"E": 1}),
        ("Este", {"R": 1}), ("Oeste", {"G": 1}),
    ]),
]

st.set_page_config(page_title="Test de mitología | Demigods ARG", page_icon="⚡")
st.title("⚡ Test de mitología")
st.caption("Demigods ARG")
st.write("Respondé las preguntas y al final elegí la mitología que más te represente.")

def get_supabase():
    try:
        return create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_SERVICE_ROLE_KEY"],
        )
    except Exception as exc:
        raise RuntimeError(
            "Faltan SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY en Streamlit → Settings → Secrets."
        ) from exc

def lookup_camper(db, cirse):
    try:
        result = (db.table(TABLE_NAME)
                  .select(f"{CIRSE_COLUMN},{MITOLOGIA_COLUMN}")
                  .eq(CIRSE_COLUMN, cirse).limit(2).execute())
    except Exception as exc:
        raise RuntimeError(
            f"No se pudo consultar Supabase. Revisá los nombres de las columnas "
            f"'{CIRSE_COLUMN}' y '{MITOLOGIA_COLUMN}'. Detalle: {exc}"
        ) from exc
    rows = result.data or []
    if len(rows) > 1:
        raise RuntimeError("Hay más de un campista con ese número de Circe. Contactá al equipo.")
    return rows[0] if rows else None

def empty(value):
    return value is None or (isinstance(value, str) and not value.strip())

def score_answers(answers):
    scores = {key: 0 for key in MYTHS}
    for q_index, selected in answers.items():
        scoring = dict(QUESTIONS[q_index][1])[selected]
        for myth, points in scoring.items():
            scores[myth] += points
    return scores

def ranking(scores):
    return sorted(TIE_ORDER, key=lambda myth: (-scores[myth], TIE_ORDER.index(myth)))

def reset_test():
    for key in ("camper_cirse", "answers", "ranking", "done", "final_choice"):
        st.session_state.pop(key, None)

if "camper_cirse" not in st.session_state:
    with st.form("identify"):
        cirse = st.text_input("Número de Circe", placeholder="Ingresá tu número")
        proceed = st.form_submit_button("Continuar", type="primary", use_container_width=True)
    if proceed:
        cirse = cirse.strip()
        if not cirse:
            st.error("Ingresá tu número de Circe para continuar.")
        else:
            try:
                db = get_supabase()
                camper = lookup_camper(db, cirse)
                if camper is None:
                    st.error("El Circe no existe.")
                elif not empty(camper.get(MITOLOGIA_COLUMN)):
                    st.error("Este Circe ya completó el test de mitología.")
                else:
                    st.session_state.camper_cirse = cirse
                    st.rerun()
            except Exception as exc:
                st.error("No pudimos consultar la base de datos. Revisá la configuración e intentá de nuevo.")
                st.caption(f"Detalle técnico: {exc}")

elif st.session_state.get("done"):
    st.success(f"¡Listo! Tu mitología elegida es: {st.session_state.final_choice}.")
    st.write("Tu elección quedó guardada.")
    if st.button("Volver al inicio"):
        reset_test()
        st.rerun()

elif "ranking" not in st.session_state:
    st.success("Circe verificado. ¡Podés comenzar!")
    with st.form("quiz"):
        answers = {}
        for i, (question, options) in enumerate(QUESTIONS):
            st.subheader(f"{i + 1}. {question}")
            labels = [label for label, _ in options]
            answers[i] = st.radio(question, labels, index=None, key=f"question_{i}",
                                  label_visibility="collapsed")
        finished = st.form_submit_button("Ver mi resultado", type="primary", use_container_width=True)
    if finished:
        if any(value is None for value in answers.values()):
            st.error("Respondé todas las preguntas antes de continuar.")
        else:
            st.session_state.answers = answers
            st.session_state.ranking = ranking(score_answers(answers))
            st.rerun()

else:
    st.subheader("¿A qué mitología pertenecés?")
    st.write("Estas son tus afinidades según tus respuestas. Los puntajes no se muestran. Elegí una opción.")
    ordered_labels = [MYTHS[code] for code in st.session_state.ranking]
    with st.form("choose"):
        chosen = st.radio("Elegí una mitología", ordered_labels, index=None)
        save = st.form_submit_button("Confirmar mi elección", type="primary", use_container_width=True)
    if save:
        if not chosen:
            st.error("Elegí una mitología para continuar.")
        else:
            try:
                db = get_supabase()
                # Verificar otra vez que siga vacía para no pisar una elección existente.
                camper = lookup_camper(db, st.session_state.camper_cirse)
                if camper is None:
                    st.error("El Circe ya no figura en la base de datos. Contactá al equipo.")
                elif not empty(camper.get(MITOLOGIA_COLUMN)):
                    st.error("Este Circe ya completó el test. No se modificó la base de datos.")
                else:
                    result = (db.table(TABLE_NAME)
                              .update({MITOLOGIA_COLUMN: chosen})
                              .eq(CIRSE_COLUMN, st.session_state.camper_cirse)
                              .is_(MITOLOGIA_COLUMN, "null")
                              .execute())
                    if not result.data:
                        st.error("No se guardó la elección. Volvé a consultar tu número de Circe.")
                    else:
                        st.session_state.final_choice = chosen
                        st.session_state.done = True
                        st.rerun()
            except Exception as exc:
                st.error("No pudimos guardar tu elección. Revisá la configuración o contactá al equipo.")
                st.caption(f"Detalle técnico: {exc}")
