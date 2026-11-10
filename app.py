"""
PV System Monitor - real-time photovoltaic monitoring dashboard (IHM)

Authors:    Ghofrane Bouzidi, Donia El Manaa
Supervisor: Prof. Mouez Bousaada
License:    MIT

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import serial
import json
import serial.tools.list_ports

# Page configuration
st.set_page_config(
    page_title="PV System Monitor",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');
    
    .main {
        padding: 0rem 1rem;
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #00d4ff !important;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    .stMetric {
        background: linear-gradient(135deg, rgba(15, 12, 41, 0.8) 0%, rgba(48, 43, 99, 0.8) 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .stMetric label {
        color: #00d4ff !important;
        font-family: 'Exo 2', sans-serif !important;
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-family: 'Orbitron', monospace !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, rgba(15, 12, 41, 0.95) 0%, rgba(48, 43, 99, 0.95) 100%);
    }
    
    .stButton button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
        color: white;
        font-family: 'Exo 2', sans-serif;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 10px 20px;
        transition: all 0.3s ease;
        box-shadow: none;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: 2px solid #00d4ff !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.5) !important;
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #7689f7 0%, #8359b1 100%) !important;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.7) !important;
    }
    
    .status-online {
        color: #2ecc71;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(46, 204, 113, 0.8);
    }
    
    .status-warning {
        color: #f39c12;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(243, 156, 18, 0.8);
    }
    
    .status-offline {
        color: #e74c3c;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(231, 76, 60, 0.8);
    }
    
    .floating-notifications {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 320px;
        max-height: 500px;
        overflow-y: auto;
        z-index: 9999;
        background: linear-gradient(135deg, rgba(15, 12, 41, 0.98) 0%, rgba(48, 43, 99, 0.98) 100%);
        border: 2px solid rgba(0, 212, 255, 0.4);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        font-family: 'Exo 2', sans-serif;
    }
    
    .floating-notifications h3 {
        margin: 0 0 15px 0;
        font-size: 18px;
        color: #00d4ff !important;
        text-align: center;
        font-family: 'Orbitron', sans-serif !important;
        text-shadow: 0 0 15px rgba(0, 212, 255, 0.6);
    }
    
    .notification-item {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-left: 4px solid;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-size: 13px;
        color: #ffffff;
        animation: slideIn 0.3s ease-out;
    }
    
    .notification-error {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.15) 0%, rgba(192, 57, 43, 0.1) 100%);
    }
    
    .notification-warning {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, rgba(243, 156, 18, 0.15) 0%, rgba(230, 126, 34, 0.1) 100%);
    }
    
    .notification-info {
        border-left-color: #3498db;
        background: linear-gradient(135deg, rgba(52, 152, 219, 0.15) 0%, rgba(41, 128, 185, 0.1) 100%);
    }
    
    .notification-success {
        border-left-color: #2ecc71;
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.15) 0%, rgba(39, 174, 96, 0.1) 100%);
    }
    
    .notification-item strong {
        display: block;
        margin-bottom: 5px;
        font-size: 14px;
        font-weight: 700;
    }
    
    .notification-item small {
        font-size: 12px;
        opacity: 0.9;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(350px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .floating-notifications::-webkit-scrollbar {
        width: 6px;
    }
    
    .floating-notifications::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    .floating-notifications::-webkit-scrollbar-thumb {
        background: rgba(0, 212, 255, 0.5);
        border-radius: 10px;
    }
    
    .floating-notifications::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 212, 255, 0.7);
    }
    
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'overview'

if 'data_history' not in st.session_state:
    st.session_state.data_history = pd.DataFrame(columns=[
        'timestamp', 'voltage', 'current', 'power', 'temperature', 'efficiency', 'energy'
    ])
    st.session_state.total_energy = 0
    st.session_state.peak_power = 0
    st.session_state.uptime_start = datetime.now()

if 'serial_port' not in st.session_state:
    st.session_state.serial_port = None

if 'connection_mode' not in st.session_state:
    st.session_state.connection_mode = 'simulation'

if 'connection_status' not in st.session_state:
    st.session_state.connection_status = 'disconnected'

if 'last_data_time' not in st.session_state:
    st.session_state.last_data_time = None

# Navigation functions
def navigate_to(page):
    st.session_state.page = page

# Function to list available serial ports
def get_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Connection function
def connect_to_arduino(port, baud_rate=9600):
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        st.session_state.connection_status = 'connected'
        return ser
    except Exception as e:
        st.error(f"Échec de connexion à Arduino: {e}")
        st.session_state.connection_status = 'error'
        return None

# Read Arduino data
def read_arduino_data(ser):
    try:
        if ser and ser.is_open and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line.startswith('{') and line.endswith('}'):
                data = json.loads(line)
                if 'voltage' in data and 'current' in data and 'temperature' in data:
                    st.session_state.last_data_time = datetime.now()
                    st.session_state.connection_status = 'receiving'
                    return data
    except json.JSONDecodeError as e:
        st.warning(f"Erreur de parsing JSON: {e}")
    except Exception as e:
        st.warning(f"Erreur de lecture Arduino: {e}")
        st.session_state.connection_status = 'error'
    return None

# Simulate PV data (VALEURS RÉALISTES)
def get_simulated_data():
    now = datetime.now()
    
    # Tension typique PV: 32-42V
    voltage = np.random.uniform(32, 42)
    
    # Courant typique: 2-8A (dépend de l'irradiance)
    current = np.random.uniform(2, 8)
    
    power = voltage * current
    
    # Température module: 20-60°C
    temperature = np.random.uniform(20, 60)
    
    # Efficacité panneau: 14-18% (coefficient de température réel)
    base_efficiency = 17.0
    temp_coefficient = -0.45
    optimal_temp = 25
    efficiency = base_efficiency + (temp_coefficient * (temperature - optimal_temp)) / 10
    efficiency = max(10, min(18, efficiency))
    
    energy_increment = power / 3600
    
    return {
        'timestamp': now,
        'voltage': voltage,
        'current': current,
        'power': power,
        'temperature': temperature,
        'efficiency': efficiency,
        'energy': energy_increment
    }

# Get PV data
def get_pv_data():
    now = datetime.now()
    
    if st.session_state.connection_mode == 'arduino' and st.session_state.serial_port:
        if st.session_state.last_data_time:
            time_since_last = (now - st.session_state.last_data_time).total_seconds()
            if time_since_last > 5:
                st.session_state.connection_status = 'timeout'
        
        arduino_data = read_arduino_data(st.session_state.serial_port)
        
        if arduino_data and 'voltage' in arduino_data and 'current' in arduino_data and 'temperature' in arduino_data:
            voltage = float(arduino_data['voltage'])
            current = float(arduino_data['current'])
            temperature = float(arduino_data['temperature'])
            power = voltage * current
            
            # Calcul efficacité basé sur température
            base_efficiency = 17.0
            temp_coefficient = -0.45
            optimal_temp = 25
            efficiency = base_efficiency + (temp_coefficient * (temperature - optimal_temp)) / 10
            efficiency = max(10, min(18, efficiency))
            
            energy_increment = power / 3600
            
            return {
                'timestamp': now,
                'voltage': voltage,
                'current': current,
                'power': power,
                'temperature': temperature,
                'efficiency': efficiency,
                'energy': energy_increment
            }
    
    return get_simulated_data()

# Update data
def update_data():
    new_data = get_pv_data()
    new_row = pd.DataFrame([new_data])
    st.session_state.data_history = pd.concat([
        st.session_state.data_history, 
        new_row
    ], ignore_index=True)
    
    st.session_state.total_energy += new_data['energy']
    
    if new_data['power'] > st.session_state.peak_power:
        st.session_state.peak_power = new_data['power']
    
    if len(st.session_state.data_history) > 200:
        st.session_state.data_history = st.session_state.data_history.tail(200)

# Alert system (AJUSTÉ POUR PV)
def check_alerts(data):
    alerts = []
    
    # Tension anormale
    if data['voltage'] < 32 or data['voltage'] > 45:
        alerts.append(("⚠️ Tension Anormale", f"{data['voltage']:.2f}V (Normal: 32-45V)", "warning"))
    
    # Courant très faible (ombrage possible)
    if data['current'] < 1.0:
        alerts.append(("☁️ Courant Faible", f"{data['current']:.2f}A (Ombrage possible)", "info"))
    
    # Surintensité
    if data['current'] > 9.5:
        alerts.append(("⚠️ Surintensité", f"{data['current']:.2f}A (Max: 9.5A)", "warning"))
    
    # Température critique
    if data['temperature'] > 65:
        alerts.append(("🌡️ Surchauffe Module", f"{data['temperature']:.2f}°C (Critique: >65°C)", "error"))
    elif data['temperature'] > 50:
        alerts.append(("🌡️ Température Élevée", f"{data['temperature']:.2f}°C (Perte efficacité)", "warning"))
    
    # Efficacité faible
    if data['efficiency'] < 12:
        alerts.append(("📉 Faible Efficacité", f"{data['efficiency']:.2f}% (Min: 12%)", "warning"))
    
    # Puissance très faible
    if data['power'] < 50:
        alerts.append(("💡 Puissance Très Faible", f"{data['power']:.2f}W (Vérifier ensoleillement)", "info"))
    
    return alerts

# Calculate statistics
def calculate_statistics(df):
    if len(df) == 0:
        return {}
    
    stats = {
        'voltage': {
            'current': df['voltage'].iloc[-1],
            'mean': df['voltage'].mean(),
            'std': df['voltage'].std(),
            'min': df['voltage'].min(),
            'max': df['voltage'].max(),
        },
        'current': {
            'current': df['current'].iloc[-1],
            'mean': df['current'].mean(),
            'std': df['current'].std(),
            'min': df['current'].min(),
            'max': df['current'].max(),
        },
        'power': {
            'current': df['power'].iloc[-1],
            'mean': df['power'].mean(),
            'std': df['power'].std(),
            'min': df['power'].min(),
            'max': df['power'].max(),
            'median': df['power'].median(),
            'peak_capacity': (df['power'].max() / 400) * 100  # Capacité basée sur 400W nominal
        },
        'temperature': {
            'current': df['temperature'].iloc[-1],
            'mean': df['temperature'].mean(),
            'std': df['temperature'].std(),
            'min': df['temperature'].min(),
            'max': df['temperature'].max(),
        },
        'efficiency': {
            'current': df['efficiency'].iloc[-1],
            'mean': df['efficiency'].mean(),
            'min': df['efficiency'].min(),
            'max': df['efficiency'].max(),
        }
    }
    return stats

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ PANNEAU DE CONTRÔLE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Arduino Connection Section
    st.markdown("<h3>🔌 CONNEXION</h3>", unsafe_allow_html=True)
    
    connection_mode = st.radio(
        "Source de données",
        options=['simulation', 'arduino'],
        format_func=lambda x: '🎲 Mode Simulation' if x == 'simulation' else '📡 Mode Arduino',
        key='connection_mode_radio'
    )
    st.session_state.connection_mode = connection_mode
    
    if connection_mode == 'arduino':
        available_ports = get_serial_ports()
        
        if available_ports:
            selected_port = st.selectbox("Sélectionner le port COM", available_ports)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔗 Connecter", use_container_width=True):
                    if st.session_state.serial_port:
                        st.session_state.serial_port.close()
                    st.session_state.serial_port = connect_to_arduino(selected_port)
                    if st.session_state.serial_port:
                        st.success("Connecté!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Déconnecter", use_container_width=True):
                    if st.session_state.serial_port:
                        st.session_state.serial_port.close()
                        st.session_state.serial_port = None
                        st.session_state.connection_status = 'disconnected'
                        st.info("Déconnecté")
                    st.rerun()
            
            # Status display
            if st.session_state.serial_port and st.session_state.serial_port.is_open:
                if st.session_state.connection_status == 'receiving':
                    st.success(f"✅ Connecté à {selected_port} - Réception données")
                elif st.session_state.connection_status == 'timeout':
                    st.warning(f"⚠️ Connecté à {selected_port} - Aucune donnée")
                elif st.session_state.connection_status == 'connected':
                    st.info(f"🔗 Connecté à {selected_port} - En attente")
                else:
                    st.error(f"❌ Erreur de connexion")
            else:
                st.warning("⚠️ Non connecté")
        else:
            st.error("❌ Aucun port COM trouvé")
            st.info("Connectez votre Arduino et rafraîchissez")
    else:
        st.info("🎲 Utilisation de données simulées")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("<h3>📍 NAVIGATION</h3>", unsafe_allow_html=True)
    
    if st.button("🏠 Vue d'ensemble", use_container_width=True, key="nav_overview"):
        navigate_to('overview')
        st.rerun()
    
    if st.button("⚡ Analyse Électrique", use_container_width=True, key="nav_electrical"):
        navigate_to('electrical')
        st.rerun()
    
    if st.button("💡 Puissance & Énergie", use_container_width=True, key="nav_power"):
        navigate_to('power')
        st.rerun()
    
    if st.button("🌡️ Gestion Thermique", use_container_width=True, key="nav_thermal"):
        navigate_to('thermal')
        st.rerun()
    
    if st.button("📊 Performances", use_container_width=True, key="nav_performance"):
        navigate_to('performance')
        st.rerun()
    
    if st.button("📈 Historique", use_container_width=True, key="nav_history"):
        navigate_to('history')
        st.rerun()
    
    st.markdown("---")
    
    # Settings
    st.markdown("<h3>🔧 PARAMÈTRES</h3>", unsafe_allow_html=True)
    refresh_rate = st.slider("Taux de rafraîchissement (secondes)", 1, 10, 1)
    
    st.markdown("---")
    
    # System info
    st.markdown("<h3>📊 INFO SYSTÈME</h3>", unsafe_allow_html=True)
    uptime = datetime.now() - st.session_state.uptime_start
    
    st.info(f"""
**⏱️ Durée:** {str(uptime).split('.')[0]}  
**📊 Points de données:** {len(st.session_state.data_history)}  
**⚡ Puissance pic:** {st.session_state.peak_power:.2f}W  
**🔋 Énergie totale:** {st.session_state.total_energy:.2f}Wh
    """)
    
    st.markdown("---")
    
    # System status
    if st.session_state.data_history.shape[0] > 0:
        current_data = st.session_state.data_history.iloc[-1]
        alerts = check_alerts(current_data)
        
        if len(alerts) == 0:
            status_class = "status-online"
            status_text = "🟢 OPÉRATIONNEL"
        elif any(alert[2] == 'error' for alert in alerts):
            status_class = "status-offline"
            status_text = "🔴 CRITIQUE"
        else:
            status_class = "status-warning"
            status_text = "🟡 ALERTE"
        
        st.markdown(f"<h3>État du système</h3>", unsafe_allow_html=True)
        st.markdown(f"<p class='{status_class}'>{status_text}</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.data_history = pd.DataFrame(columns=[
            'timestamp', 'voltage', 'current', 'power', 'temperature', 'efficiency', 'energy'
        ])
        st.session_state.total_energy = 0
        st.session_state.peak_power = 0
        st.session_state.uptime_start = datetime.now()
        st.rerun()

# Update data
update_data()
current_data = st.session_state.data_history.iloc[-1] if len(st.session_state.data_history) > 0 else None

# Floating notification panel
if current_data is not None:
    alerts = check_alerts(current_data)
    
    notifications_html = '<div class="floating-notifications">'
    
    if alerts:
        notifications_html += '<h3>🚨 ALERTES ACTIVES</h3>'
        for title, message, alert_type in alerts:
            if alert_type == "error":
                notifications_html += f'<div class="notification-item notification-error"><strong>{title}</strong><small>{message}</small></div>'
            elif alert_type == "warning":
                notifications_html += f'<div class="notification-item notification-warning"><strong>{title}</strong><small>{message}</small></div>'
            else:
                notifications_html += f'<div class="notification-item notification-info"><strong>{title}</strong><small>{message}</small></div>'
    else:
        notifications_html += '<h3>✅ ÉTAT DU SYSTÈME</h3>'
        notifications_html += '<div class="notification-item notification-success"><strong>Système opérationnel</strong><small>Aucune alerte détectée</small></div>'
    
    notifications_html += '</div>'
    
    st.markdown(notifications_html, unsafe_allow_html=True)

# Top navigation
st.markdown("""
<div style='text-align: left; margin-bottom: 20px;'>
    <span style='font-family: Orbitron, sans-serif; font-size: 28px; font-weight: 900; color: #00d4ff; text-shadow: 0 0 20px rgba(0, 212, 255, 0.8);'>
        ☀️ MONITEUR PV PRO
    </span>
</div>
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🏠 Vue", key="nav_btn_overview", use_container_width=True,
                 type="primary" if st.session_state.page == 'overview' else "secondary"):
        navigate_to('overview')
        st.rerun()

with col2:
    if st.button("⚡ Électrique", key="nav_btn_electrical", use_container_width=True,
                 type="primary" if st.session_state.page == 'electrical' else "secondary"):
        navigate_to('electrical')
        st.rerun()

with col3:
    if st.button("💡 Puissance", key="nav_btn_power", use_container_width=True,
                 type="primary" if st.session_state.page == 'power' else "secondary"):
        navigate_to('power')
        st.rerun()

with col4:
    if st.button("🌡️ Thermique", key="nav_btn_thermal", use_container_width=True,
                 type="primary" if st.session_state.page == 'thermal' else "secondary"):
        navigate_to('thermal')
        st.rerun()

with col5:
    if st.button("📊 Performances", key="nav_btn_performance", use_container_width=True,
                 type="primary" if st.session_state.page == 'performance' else "secondary"):
        navigate_to('performance')
        st.rerun()

with col6:
    if st.button("📈 Historique", key="nav_btn_history", use_container_width=True,
                 type="primary" if st.session_state.page == 'history' else "secondary"):
        navigate_to('history')
        st.rerun()

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
st.markdown("---")

# PAGES

if st.session_state.page == 'overview':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>☀️ VUE D'ENSEMBLE DU SYSTÈME</h1>", unsafe_allow_html=True)
    
    if current_data is not None:
        st.markdown("<h2>📊 MÉTRIQUES EN TEMPS RÉEL</h2>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="⚡ TENSION",
                value=f"{current_data['voltage']:.2f} V",
                delta=f"{current_data['voltage'] - 37:.2f}V"
            )
        
        with col2:
            st.metric(
                label="🔌 COURANT",
                value=f"{current_data['current']:.2f} A",
                delta=f"{current_data['current'] - 5:.2f}A"
            )
        
        with col3:
            st.metric(
                label="💡 PUISSANCE",
                value=f"{current_data['power']:.0f} W",
                delta=f"{((current_data['power']/400)*100):.1f}%"
            )
        
        with col4:
            st.metric(
                label="🌡️ TEMPÉRATURE",
                value=f"{current_data['temperature']:.1f} °C",
                delta=f"{current_data['temperature'] - 40:.1f}°C"
            )
        
        with col5:
            st.metric(
                label="⚙️ EFFICACITÉ",
                value=f"{current_data['efficiency']:.2f} %",
                delta=f"{current_data['efficiency'] - 17:.2f}%"
            )
        
        st.markdown("---")
        
        if len(st.session_state.data_history) > 1:
            st.markdown("<h2>📈 TENDANCE PUISSANCE (50 dernières lectures)</h2>", unsafe_allow_html=True)
            df = st.session_state.data_history.tail(50)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['power'],
                mode='lines',
                name='Puissance',
                line=dict(color='#00d4ff', width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 212, 255, 0.3)'
            ))
            
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2'),
                xaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(255, 255, 255, 0.1)', title='Puissance (W)'),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == 'electrical':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>⚡ ANALYSE ÉLECTRIQUE</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.data_history) > 1:
        df = st.session_state.data_history
        stats = calculate_statistics(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h2>📊 ANALYSE TENSION</h2>", unsafe_allow_html=True)
            st.metric("Actuelle", f"{stats['voltage']['current']:.2f}V")
            subcol1, subcol2, subcol3 = st.columns(3)
            with subcol1:
                st.metric("Moyenne", f"{stats['voltage']['mean']:.2f}V")
            with subcol2:
                st.metric("Min", f"{stats['voltage']['min']:.2f}V")
            with subcol3:
                st.metric("Max", f"{stats['voltage']['max']:.2f}V")
            
            st.write(f"**Écart type:** {stats['voltage']['std']:.3f}V")
            
            fig_volt = go.Figure(data=[go.Histogram(
                x=df['voltage'],
                nbinsx=20,
                marker_color='#FF6B6B',
                marker=dict(line=dict(color='#ffffff', width=1))
            )])
            fig_volt.update_layout(
                title="Distribution de tension",
                xaxis_title="Tension (V)",
                yaxis_title="Fréquence",
                height=350,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_volt, use_container_width=True)
            
            fig_volt_time = go.Figure()
            fig_volt_time.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['voltage'],
                mode='lines+markers',
                name='Tension',
                line=dict(color='#FF6B6B', width=2),
                marker=dict(size=4)
            ))
            fig_volt_time.add_hline(y=37, line_dash="dash", line_color="#2ecc71", opacity=0.7)
            fig_volt_time.update_layout(
                title="Tendance tension",
                xaxis_title="Temps",
                yaxis_title="Tension (V)",
                height=350,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_volt_time, use_container_width=True)
        
        with col2:
            st.markdown("<h2>📊 ANALYSE COURANT</h2>", unsafe_allow_html=True)
            st.metric("Actuel", f"{stats['current']['current']:.2f}A")
            subcol1, subcol2, subcol3 = st.columns(3)
            with subcol1:
                st.metric("Moyenne", f"{stats['current']['mean']:.2f}A")
            with subcol2:
                st.metric("Min", f"{stats['current']['min']:.2f}A")
            with subcol3:
                st.metric("Max", f"{stats['current']['max']:.2f}A")
            
            st.write(f"**Écart type:** {stats['current']['std']:.3f}A")
            
            fig_curr = go.Figure(data=[go.Histogram(
                x=df['current'],
                nbinsx=20,
                marker_color='#4ECDC4',
                marker=dict(line=dict(color='#ffffff', width=1))
            )])
            fig_curr.update_layout(
                title="Distribution de courant",
                xaxis_title="Courant (A)",
                yaxis_title="Fréquence",
                height=350,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_curr, use_container_width=True)
            
            fig_curr_time = go.Figure()
            fig_curr_time.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['current'],
                mode='lines',
                name='Courant',
                line=dict(color='#4ECDC4', width=2),
                fill='tozeroy',
                fillcolor='rgba(78, 205, 196, 0.3)'
            ))
            fig_curr_time.add_hline(y=5, line_dash="dash", line_color="#2ecc71", opacity=0.7)
            fig_curr_time.update_layout(
                title="Tendance courant",
                xaxis_title="Temps",
                yaxis_title="Courant (A)",
                height=350,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_curr_time, use_container_width=True)

elif st.session_state.page == 'power':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>💡 ANALYSE PUISSANCE & ÉNERGIE</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.data_history) > 1:
        df = st.session_state.data_history
        stats = calculate_statistics(df)
        
        st.markdown("<h2>📊 STATISTIQUES PUISSANCE</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Puissance actuelle", f"{stats['power']['current']:.0f}W")
        with col2:
            st.metric("Puissance moyenne", f"{stats['power']['mean']:.0f}W")
        with col3:
            st.metric("Puissance pic", f"{stats['power']['max']:.0f}W")
        with col4:
            st.metric("Capacité pic", f"{stats['power']['peak_capacity']:.1f}%")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_power = go.Figure()
            fig_power.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['power'],
                mode='lines',
                name='Réel',
                line=dict(color='#00d4ff', width=2)
            ))
            ma = df['power'].rolling(window=10).mean()
            fig_power.add_trace(go.Scatter(
                x=df['timestamp'],
                y=ma,
                mode='lines',
                name='Moy. mobile (10)',
                line=dict(color='#F38181', width=3, dash='dash')
            ))
            fig_power.update_layout(
                title="Puissance avec moyenne mobile",
                xaxis_title="Temps",
                yaxis_title="Puissance (W)",
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_power, use_container_width=True)
            
            st.write(f"**Puissance minimale:** {stats['power']['min']:.2f}W")
            st.write(f"**Puissance médiane:** {stats['power']['median']:.2f}W")
            st.write(f"**Écart type:** {stats['power']['std']:.2f}W")
        
        with col2:
            fig_hist = go.Figure(data=[go.Histogram(
                x=df['power'],
                nbinsx=25,
                marker_color='#95E1D3',
                marker=dict(line=dict(color='#ffffff', width=1))
            )])
            fig_hist.update_layout(
                title="Distribution de puissance",
                xaxis_title="Puissance (W)",
                yaxis_title="Fréquence",
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown("---")
        st.markdown("<h2>🔋 PRODUCTION D'ÉNERGIE</h2>", unsafe_allow_html=True)
        
        cumulative_energy = df['energy'].cumsum()
        fig_energy = go.Figure()
        fig_energy.add_trace(go.Scatter(
            x=df['timestamp'],
            y=cumulative_energy,
            mode='lines',
            name='Énergie',
            line=dict(color='#FCBAD3', width=3),
            fill='tozeroy',
            fillcolor='rgba(252, 186, 211, 0.3)'
        ))
        fig_energy.update_layout(
            title="Production d'énergie cumulée",
            xaxis_title="Temps",
            yaxis_title="Énergie (Wh)",
            height=400,
            plot_bgcolor='rgba(15, 12, 41, 0.8)',
            paper_bgcolor='rgba(15, 12, 41, 0.5)',
            font=dict(color='#ffffff', family='Exo 2'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_energy, use_container_width=True)

elif st.session_state.page == 'thermal':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>🌡️ GESTION THERMIQUE</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.data_history) > 1:
        df = st.session_state.data_history
        stats = calculate_statistics(df)
        
        st.markdown("<h2>📊 STATISTIQUES THERMIQUES</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Temp. actuelle", f"{stats['temperature']['current']:.1f}°C")
        with col2:
            st.metric("Temp. moyenne", f"{stats['temperature']['mean']:.1f}°C")
        with col3:
            st.metric("Temp. min", f"{stats['temperature']['min']:.1f}°C")
        with col4:
            st.metric("Temp. max", f"{stats['temperature']['max']:.1f}°C")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Plage température:** {stats['temperature']['max'] - stats['temperature']['min']:.2f}°C")
            st.write(f"**Écart type:** {stats['temperature']['std']:.2f}°C")
            
            optimal_count = len(df[df['temperature'] <= 40])
            warning_count = len(df[(df['temperature'] > 40) & (df['temperature'] <= 50)])
            critical_count = len(df[df['temperature'] > 50])
            
            st.markdown("#### Zones de température")
            st.success(f"✅ **Optimal (<40°C):** {optimal_count} lectures ({optimal_count/len(df)*100:.1f}%)")
            st.warning(f"⚠️ **Alerte (40-50°C):** {warning_count} lectures ({warning_count/len(df)*100:.1f}%)")
            st.error(f"🔥 **Critique (>50°C):** {critical_count} lectures ({critical_count/len(df)*100:.1f}%)")
            
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['temperature'],
                mode='lines+markers',
                name='Température',
                line=dict(color='#F38181', width=2),
                marker=dict(size=4)
            ))
            fig_temp.add_hrect(y0=40, y1=50, fillcolor="yellow", opacity=0.1)
            fig_temp.add_hrect(y0=50, y1=70, fillcolor="red", opacity=0.1)
            fig_temp.update_layout(
                title="Tendance température",
                xaxis_title="Temps",
                yaxis_title="Température (°C)",
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Optimal', 'Alerte', 'Critique'],
                values=[optimal_count, warning_count, critical_count],
                marker_colors=['#52B788', '#FFB703', '#E63946'],
                textfont=dict(size=14, color='#ffffff', family='Exo 2')
            )])
            fig_pie.update_layout(
                title="Distribution par zone",
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            fig_hist = go.Figure(data=[go.Histogram(
                x=df['temperature'],
                nbinsx=20,
                marker_color='#F38181',
                marker=dict(line=dict(color='#ffffff', width=1))
            )])
            fig_hist.update_layout(
                title="Distribution température",
                xaxis_title="Température (°C)",
                yaxis_title="Fréquence",
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_hist, use_container_width=True)

elif st.session_state.page == 'performance':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>📊 MÉTRIQUES DE PERFORMANCE</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.data_history) > 1 and current_data is not None:
        df = st.session_state.data_history
        stats = calculate_statistics(df)
        
        st.markdown("<h2>⚙️ ANALYSE D'EFFICACITÉ</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Efficacité actuelle", f"{stats['efficiency']['current']:.2f}%")
        with col2:
            st.metric("Eff. moyenne", f"{stats['efficiency']['mean']:.2f}%")
        with col3:
            st.metric("Eff. min", f"{stats['efficiency']['min']:.2f}%")
        with col4:
            st.metric("Eff. max", f"{stats['efficiency']['max']:.2f}%")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3>🎯 Score de santé système</h3>", unsafe_allow_html=True)
            
            voltage_score = 100 if 35 <= current_data['voltage'] <= 42 else 70
            current_score = 100 if 3 <= current_data['current'] <= 8 else 80
            temp_score = 100 if current_data['temperature'] <= 40 else (70 if current_data['temperature'] <= 50 else 40)
            efficiency_score = (current_data['efficiency'] / 18) * 100
            
            overall_health = (voltage_score + current_score + temp_score + efficiency_score) / 4
            
            health_color = '#52B788' if overall_health >= 80 else ('#FFB703' if overall_health >= 60 else '#E63946')
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = overall_health,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Santé système", 'font': {'color': '#ffffff', 'family': 'Orbitron'}},
                delta = {'reference': 85},
                gauge = {
                    'axis': {'range': [None, 100], 'tickcolor': '#ffffff'},
                    'bar': {'color': health_color},
                    'steps': [
                        {'range': [0, 60], 'color': "rgba(231, 76, 60, 0.3)"},
                        {'range': [60, 80], 'color': "rgba(243, 156, 18, 0.3)"},
                        {'range': [80, 100], 'color': "rgba(46, 204, 113, 0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig_gauge.update_layout(
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.markdown("<h3>📊 Détails performance</h3>", unsafe_allow_html=True)
            
            scores = {
                'Tension': voltage_score,
                'Courant': current_score,
                'Température': temp_score,
                'Efficacité': efficiency_score
            }
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=list(scores.keys()),
                    y=list(scores.values()),
                    marker_color=['#FF6B6B', '#4ECDC4', '#F38181', '#AA96DA'],
                    text=[f"{v:.0f}%" for v in scores.values()],
                    textposition='auto',
                    textfont=dict(color='#ffffff', size=14, family='Orbitron')
                )
            ])
            fig_bar.update_layout(
                title="Scores par composant",
                yaxis_title="Score (%)",
                yaxis_range=[0, 100],
                height=400,
                plot_bgcolor='rgba(15, 12, 41, 0.8)',
                paper_bgcolor='rgba(15, 12, 41, 0.5)',
                font=dict(color='#ffffff', family='Exo 2')
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['efficiency'],
            mode='lines+markers',
            name='Efficacité',
            line=dict(color='#AA96DA', width=2),
            marker=dict(size=4)
        ))
        fig_eff.add_hline(y=17, line_dash="dash", line_color="#2ecc71", opacity=0.7)
        fig_eff.update_layout(
            title="Tendance efficacité",
            xaxis_title="Temps",
            yaxis_title="Efficacité (%)",
            height=400,
            plot_bgcolor='rgba(15, 12, 41, 0.8)',
            paper_bgcolor='rgba(15, 12, 41, 0.5)',
            font=dict(color='#ffffff', family='Exo 2'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_eff, use_container_width=True)

elif st.session_state.page == 'history':
    st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>📈 DONNÉES HISTORIQUES</h1>", unsafe_allow_html=True)
    
    if len(st.session_state.data_history) > 1:
        df = st.session_state.data_history
        
        st.markdown("<h2>📊 VUE COMPLÈTE DU SYSTÈME</h2>", unsafe_allow_html=True)
        
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=('Tension (V)', 'Courant (A)', 'Puissance (W)', 
                          'Température (°C)', 'Efficacité (%)', 'Énergie (Wh)'),
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        timestamps = df['timestamp']
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=df['voltage'], 
                      mode='lines+markers', name='Tension',
                      line=dict(color='#FF6B6B', width=2),
                      marker=dict(size=3)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=df['current'], 
                      mode='lines', name='Courant',
                      line=dict(color='#4ECDC4', width=2),
                      fill='tozeroy', fillcolor='rgba(78, 205, 196, 0.3)'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=df['power'], 
                      mode='lines', name='Puissance',
                      line=dict(color='#00d4ff', width=2)),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=df['temperature'], 
                      mode='lines+markers', name='Température',
                      line=dict(color='#F38181', width=2),
                      marker=dict(size=3)),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(x=timestamps, y=df['efficiency'], 
                      mode='lines+markers', name='Efficacité',
                      line=dict(color='#AA96DA', width=2),
                      marker=dict(size=3)),
            row=3, col=1
        )
        
        cumulative_energy = df['energy'].cumsum()
        fig.add_trace(
            go.Scatter(x=timestamps, y=cumulative_energy, 
                      mode='lines', name='Énergie',
                      line=dict(color='#FCBAD3', width=2),
                      fill='tozeroy', fillcolor='rgba(252, 186, 211, 0.3)'),
            row=3, col=2
        )
        
        fig.update_layout(
            height=900,
            showlegend=False,
            hovermode='x unified',
            plot_bgcolor='rgba(15, 12, 41, 0.8)',
            paper_bgcolor='rgba(15, 12, 41, 0.5)',
            font=dict(color='#ffffff', family='Exo 2')
        )
        
        for i in range(1, 4):
            for j in range(1, 3):
                fig.update_xaxes(gridcolor='rgba(255, 255, 255, 0.1)', row=i, col=j)
                fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)', row=i, col=j)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("<h2>📋 TABLEAU DE DONNÉES BRUTES</h2>", unsafe_allow_html=True)
        
        st.dataframe(
            df.tail(50).style.format({
                'voltage': '{:.2f}V',
                'current': '{:.2f}A',
                'power': '{:.2f}W',
                'temperature': '{:.2f}°C',
                'efficiency': '{:.2f}%',
                'energy': '{:.4f}Wh'
            }),
            use_container_width=True,
            height=400
        )

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()
