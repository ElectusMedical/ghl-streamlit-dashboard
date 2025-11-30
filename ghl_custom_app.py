import streamlit as st
import requests

# --- 1. Configuration ---
# Use the same n8n Webhook Test URL for now.
N8N_WEBHOOK_URL = "https://n8n.srv849550.hstgr.cloud/webhook-test/dfecde57-b2c3-4022-bdcb-57e6875bc7e0"

# --- 2. Initialize Session State for Credentials ---
# Session state allows the app to remember data (like inputs) between user interactions.
if 'auth_token' not in st.session_state:
    st.session_state['auth_token'] = ''
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ''
if 'sub_account_id' not in st.session_state:
    st.session_state['sub_account_id'] = ''
if 'n8n_response' not in st.session_state:
    st.session_state.n8n_response = "Por favor, ingresa las credenciales y haz clic en el botón."


# --- 3. UI and Input Fields ---
st.set_page_config(page_title="GHL Credential Test", layout="wide")
st.title("🔑 Prueba de Conexión y Credenciales (n8n)")
st.caption("Verificando el paso de API Key, User ID, y Sub-account ID al backend de n8n.")

# Input fields using st.text_input. The 'type="password"' hides the token.
token_input = st.text_input(
    "API Token / Key (REQUIRED)", 
    value=st.session_state['auth_token'], 
    type="password" 
)
user_id_input = st.text_input(
    "User ID (REQUIRED)", 
    value=st.session_state['user_id']
)
sub_account_id_input = st.text_input(
    "Sub-account ID (REQUIRED)", 
    value=st.session_state['sub_account_id']
)

# Display the response message
st.info(st.session_state.n8n_response)


# --- 4. Button Logic to Send Data ---
if st.button("Enviar Credenciales a n8n"):
    
    # 4a. Input Validation
    if not (token_input and user_id_input and sub_account_id_input):
        st.error("Debes ingresar los tres campos para la prueba.")
        st.stop()
    
    # 4b. Update Session State (Store the new values)
    st.session_state['auth_token'] = token_input
    st.session_state['user_id'] = user_id_input
    st.session_state['sub_account_id'] = sub_account_id_input

    st.toast("Enviando credenciales a n8n...", icon="⬆️")
    
    # 4c. Payload: The JSON data to send to n8n
    payload = {
        "auth_token": st.session_state['auth_token'],
        "user_id": st.session_state['user_id'],
        "sub_account_id": st.session_state['sub_account_id']
    }

    try:
        # Send the POST request to the n8n webhook
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
        response.raise_for_status() 

        # 4d. Handle the n8n Response
        n8n_data = response.json()

        # Assuming n8n returns a simple JSON object: {"status": "success", "message": "..."}
        if isinstance(n8n_data, dict) and "message" in n8n_data:
            final_message = n8n_data["message"]
            st.session_state.n8n_response = f"¡Éxito! Mensaje de n8n: **{final_message}**"
            st.toast("Credenciales enviadas y respuesta de n8n recibida!", icon="✅")
        
        # If n8n returns an array, handle it (like our previous fix)
        elif isinstance(n8n_data, list) and len(n8n_data) > 0 and "message" in n8n_data[0]:
            final_message = n8n_data[0]["message"]
            st.session_state.n8n_response = f"¡Éxito! Mensaje de n8n: **{final_message}**"
            st.toast("Credenciales enviadas y respuesta de n8n recibida!", icon="✅")
        
        else:
            st.session_state.n8n_response = f"Error: Formato de respuesta de n8n inesperado. Respuesta: {n8n_data}"

    except requests.exceptions.Timeout:
        st.session_state.n8n_response = "Error: El servidor de n8n tardó demasiado en responder (Timeout)."
    except requests.exceptions.ConnectionError:
        st.session_state.n8n_response = "Error de Conexión: No se pudo conectar al URL del webhook de n8n. Verifica el URL y si n8n está activo."
    except requests.exceptions.RequestException as e:
        st.session_state.n8n_response = f"Error al procesar la solicitud o recibir la respuesta: {e}"
    
    # Force Streamlit to rerun to display the updated message
    st.rerun()