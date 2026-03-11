"""
=============================================================================
 Maritime Route Optimization & Risk Assessment Tool
 Vietnam (Ho Chi Minh City Port) ➜ Singapore Port
=============================================================================

 Requirements (also listed in requirements.txt):
   streamlit>=1.30.0
   pandas>=2.0.0
   numpy>=1.24.0
   networkx>=3.1
   folium>=0.15.0
   streamlit-folium>=0.15.0

 Run with:  streamlit run app.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import folium
import streamlit.components.v1 as components
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# =============================================================================
# 1. PAGE CONFIGURATION & CUSTOM STYLING
# =============================================================================
st.set_page_config(
    page_title="Maritime Route Optimizer | Vietnam ➜ SEA",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Hide Streamlit Defaults ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Global ── */
html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0a0e27 0%, #0d1b3e 40%, #0f2547 100%);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b3e 0%, #162a54 50%, #1a3260 100%) !important;
    border-right: 1px solid rgba(66, 135, 245, 0.15);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em;
}

/* ── Metrics Cards UI (st.metric) ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 41, 59, 0.85));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(66, 135, 245, 0.2);
    border-radius: 16px;
    padding: 20px 24px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #4287f5, #42d4f5, #42f5a7);
    border-radius: 16px 16px 0 0;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 40px rgba(66, 135, 245, 0.25);
    border-color: rgba(66, 135, 245, 0.45);
}
[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #94a3b8 !important;
    font-weight: 600 !important;
}

/* ── Tabs & Expanders ── */
div[data-testid="stExpander"] {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(66, 135, 245, 0.2) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
div[data-testid="stTabs"] button {
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* ── Container Card ── */
.route-compare {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.9));
    backdrop-filter: blur(16px);
    border: 1px solid rgba(66, 135, 245, 0.2);
    border-radius: 16px;
    padding: 28px;
    margin: 12px 0;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
}
.route-compare h3 {
    color: #e2e8f0;
    margin-bottom: 14px;
    font-weight: 700;
}

/* ── Header ── */
.hero-title {
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(135deg, #60a5fa 0%, #34d399 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.hero-sub {
    font-size: 16px;
    color: #64748b;
    font-weight: 400;
    margin-top: 4px;
}

/* ── Streamlit button override ── */
div.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    letter-spacing: 0.04em;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35) !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    box-shadow: 0 6px 24px rgba(37, 99, 235, 0.5) !important;
    transform: translateY(-1px);
}

/* ── Map container ── */
.map-container {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(66, 135, 245, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* ── Waypoint table ── */
.waypoint-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    font-size: 13px;
}
.waypoint-table th {
    background: rgba(30, 41, 59, 0.9);
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 12px 16px;
    font-size: 11px;
}
.waypoint-table td {
    background: rgba(15, 23, 42, 0.6);
    color: #cbd5e1;
    padding: 10px 16px;
    border-top: 1px solid rgba(51, 65, 85, 0.5);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =============================================================================
# 2. DATA MODELS & CONSTANTS
# =============================================================================
@dataclass
class Waypoint:
    """Represents a geographic waypoint on the maritime graph."""
    name: str
    lat: float
    lon: float
    description: str


@dataclass
class EdgeRisk:
    """Risk profile for a graph edge (route segment)."""
    piracy: float        # 0.0 – 1.0
    conflict: float      # 0.0 – 1.0
    weather: float       # 0.0 – 1.0


# ── Destinations ──
DESTINATIONS = {
    "Singapore (Singapore Port)": "singapore_port",
    "Thailand (Laem Chabang)": "laem_chabang",
    "Indonesia (Tanjung Priok - Jakarta)": "tanjung_priok",
    "Philippines (Port of Manila)": "manila_port",
    "Malaysia (Port Klang)": "port_klang",
    "Brunei (Muara Port)": "muara_port"
}

# ── Waypoints (nodes) ──
# These represent realistic navigation points along the Vietnam-SEA corridors.
WAYPOINTS: Dict[str, Waypoint] = {
    "hcm_port": Waypoint(
        "Ho Chi Minh City Port", 10.7769, 106.7009,
        "Cat Lai Terminal – primary container port of southern Vietnam"
    ),
    "vung_tau": Waypoint(
        "Vũng Tàu Anchorage", 10.3460, 107.0843,
        "Deep-water anchorage and pilot boarding area"
    ),
    "con_dao": Waypoint(
        "Côn Đảo Islands", 8.6900, 106.6100,
        "Archipelago waypoint south of Vietnam mainland"
    ),
    "ca_mau": Waypoint(
        "Cà Mau Cape", 8.5800, 104.7200,
        "Southernmost tip of Vietnam – Gulf of Thailand entrance"
    ),
    "phu_quoc": Waypoint(
        "Phú Quốc Anchorage", 10.0000, 104.0000,
        "Highly sheltered island bay – used for severe typhoon evasion"
    ),
    "scs_central": Waypoint(
        "South China Sea Central", 6.5000, 108.5000,
        "Open sea crossing – disputed waters, higher risk zone"
    ),
    "scs_east": Waypoint(
        "SCS Eastern Bypass", 8.0000, 110.5000,
        "Far offshore route to bypass central weather systems"
    ),
    "gulf_thai": Waypoint(
        "Gulf of Thailand", 6.8000, 103.5000,
        "Sheltered waters west of the South China Sea"
    ),
    "natuna_sea": Waypoint(
        "Natuna Sea", 4.0000, 107.5000,
        "Indonesian waters between Borneo and Peninsular Malaysia"
    ),
    "anambas": Waypoint(
        "Anambas Archipelago", 3.2000, 106.2000,
        "Navigational waypoint with moderate weather protection"
    ),
    "east_malaysia": Waypoint(
        "East Peninsular Malaysia", 3.0000, 104.5000,
        "Coastal passage along the Malaysian east coast"
    ),
    "tioman": Waypoint(
        "Tioman Coastal Bypass", 2.8000, 104.1500,
        "Highly sheltered coastal route avoiding open sea swell"
    ),
    "singapore_strait": Waypoint(
        "Singapore Strait Approach", 1.8000, 104.2000,
        "Traffic Separation Scheme approach to Singapore"
    ),
    "singapore_port": Waypoint(
        "Singapore Port (PSA)", 1.2644, 103.8200,
        "PSA Singapore – world's second-busiest container port"
    ),
    "laem_chabang": Waypoint(
        "Laem Chabang Port (Thailand)", 13.0833, 100.8833, 
        "Thailand's largest deep sea port"
    ),
    "tanjung_priok": Waypoint(
        "Tanjung Priok (Indonesia)", -6.1000, 106.8833, 
        "Jakarta's main seaport"
    ),
    "karimata_strait": Waypoint(
        "Karimata Strait", -1.5000, 108.0000, 
        "Strait connecting South China Sea to Java Sea"
    ),
    "manila_port": Waypoint(
        "Port of Manila (Philippines)", 14.5833, 120.9667, 
        "Premier international gateway to the Philippines"
    ),
    "palawan_passage": Waypoint(
        "Palawan Passage", 10.0000, 118.0000, 
        "Deep water route west of Palawan"
    ),
    "malacca_strait": Waypoint(
        "Strait of Malacca", 2.5000, 101.5000, 
        "One of the most important shipping lanes in the world"
    ),
    "port_klang": Waypoint(
        "Port Klang (Malaysia)", 3.0000, 101.4000, 
        "Main gateway by sea into Malaysia"
    ),
    "brunei_coast": Waypoint(
        "Brunei Coastal Waters", 5.5000, 114.5000, 
        "Navigation point off the coast of Brunei"
    ),
    "muara_port": Waypoint(
        "Muara Port (Brunei)", 5.0333, 115.0667, 
        "Only deep water port in Brunei"
    ),
}

# ── Edges: (node_a, node_b, distance_nm, EdgeRisk) ──
# Distances in nautical miles (approximate).
EDGES: List[Tuple[str, str, float, EdgeRisk]] = [
    # Departure segment
    ("hcm_port", "vung_tau", 45, EdgeRisk(0.02, 0.01, 0.05)),

    # Vũng Tàu ➜ diverging corridors
    ("vung_tau", "con_dao", 152, EdgeRisk(0.05, 0.03, 0.15)),
    ("vung_tau", "ca_mau", 195, EdgeRisk(0.03, 0.02, 0.20)),
    ("vung_tau", "scs_east", 250, EdgeRisk(0.15, 0.30, 0.50)),

    # Côn Đảo corridor
    ("con_dao", "scs_central", 210, EdgeRisk(0.45, 0.55, 0.35)),
    ("con_dao", "natuna_sea", 380, EdgeRisk(0.20, 0.15, 0.25)),

    # SCS Eastern Bypass (Far offshore detour)
    ("scs_east", "scs_central", 180, EdgeRisk(0.40, 0.60, 0.45)),
    ("scs_east", "natuna_sea", 320, EdgeRisk(0.35, 0.45, 0.40)),

    # Cà Mau ➜ Gulf of Thailand & Phu Quoc Detour
    ("ca_mau", "gulf_thai", 230, EdgeRisk(0.08, 0.05, 0.25)),
    ("ca_mau", "phu_quoc", 110, EdgeRisk(0.02, 0.01, 0.05)),
    ("phu_quoc", "gulf_thai", 200, EdgeRisk(0.03, 0.01, 0.08)),

    # SCS Central Convergence
    ("scs_central", "natuna_sea", 275, EdgeRisk(0.50, 0.40, 0.30)),
    ("scs_central", "anambas", 310, EdgeRisk(0.35, 0.30, 0.25)),

    # Gulf of Thailand Convergence
    ("gulf_thai", "east_malaysia", 260, EdgeRisk(0.06, 0.03, 0.15)),
    ("gulf_thai", "natuna_sea", 310, EdgeRisk(0.12, 0.08, 0.18)),
    ("gulf_thai", "anambas", 280, EdgeRisk(0.09, 0.06, 0.12)),

    # Natuna Sea
    ("natuna_sea", "anambas", 120, EdgeRisk(0.12, 0.08, 0.15)),
    ("natuna_sea", "singapore_strait", 350, EdgeRisk(0.15, 0.10, 0.10)),

    # Anambas Archipelago (Midway)
    ("anambas", "east_malaysia", 140, EdgeRisk(0.08, 0.04, 0.10)),
    ("anambas", "singapore_strait", 220, EdgeRisk(0.10, 0.05, 0.12)),

    # East Malaysia Coastal
    ("east_malaysia", "tioman", 30, EdgeRisk(0.03, 0.01, 0.05)),
    ("east_malaysia", "singapore_strait", 180, EdgeRisk(0.04, 0.02, 0.10)),

    # Tioman (Highly sheltered bypass before Singapore)
    ("tioman", "singapore_strait", 155, EdgeRisk(0.02, 0.01, 0.04)),

    # Final approach to Singapore
    ("singapore_strait", "singapore_port", 55, EdgeRisk(0.02, 0.01, 0.05)),

    # Thailand (Laem Chabang) Extensions
    ("gulf_thai", "laem_chabang", 400, EdgeRisk(0.02, 0.01, 0.10)),
    ("phu_quoc", "laem_chabang", 250, EdgeRisk(0.01, 0.01, 0.05)),

    # Indonesia (Jakarta) Extensions
    ("natuna_sea", "karimata_strait", 350, EdgeRisk(0.10, 0.05, 0.15)),
    ("singapore_strait", "karimata_strait", 250, EdgeRisk(0.12, 0.05, 0.15)),
    ("karimata_strait", "tanjung_priok", 280, EdgeRisk(0.05, 0.02, 0.10)),

    # Philippines (Manila) Extensions
    ("scs_east", "palawan_passage", 450, EdgeRisk(0.20, 0.25, 0.35)),
    ("scs_central", "palawan_passage", 550, EdgeRisk(0.25, 0.30, 0.40)),
    ("palawan_passage", "manila_port", 300, EdgeRisk(0.10, 0.15, 0.25)),

    # Malaysia (Port Klang) Extensions
    ("singapore_strait", "malacca_strait", 150, EdgeRisk(0.15, 0.05, 0.08)),
    ("malacca_strait", "port_klang", 100, EdgeRisk(0.10, 0.02, 0.05)),

    # Brunei (Muara) Extensions
    ("scs_east", "brunei_coast", 350, EdgeRisk(0.15, 0.10, 0.20)),
    ("natuna_sea", "brunei_coast", 400, EdgeRisk(0.12, 0.08, 0.15)),
    ("brunei_coast", "muara_port", 40, EdgeRisk(0.02, 0.01, 0.05)),
]

# ── Cargo-type risk multipliers ──
# These multipliers inflate the risk penalty for certain cargo types.
CARGO_RISK_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "Dry Bulk": {"piracy": 1.0, "conflict": 1.0, "weather": 1.0},
    "Liquid (Oil/Gas)": {"piracy": 1.3, "conflict": 1.2, "weather": 1.1},
    "Containers": {"piracy": 1.2, "conflict": 1.1, "weather": 1.0},
    "Hazardous (IMDG)": {"piracy": 2.0, "conflict": 1.8, "weather": 1.5},
    "Refrigerated (Reefer)": {"piracy": 1.1, "conflict": 1.0, "weather": 1.3},
}


# =============================================================================
# 3. GRAPH CONSTRUCTION
# =============================================================================
def build_maritime_graph(
    cargo_weight: float,
    vessel_length: float,
    cargo_type: str,
) -> Tuple[nx.Graph, nx.Graph]:
    """
    Build two NetworkX graphs:
      • G_dist  – edges weighted by raw nautical-mile distance only.
      • G_risk  – edges weighted by distance + risk penalty.

    Risk penalty formula per edge:
        penalty = base_distance × Σ(risk_i × cargo_multiplier_i) × vessel_factor
    where vessel_factor is a gentle upscale for larger/heavier ships navigating
    narrow or patrolled waters.

    Returns (G_dist, G_risk)
    """
    # ── Vessel factor ──
    # Heavier cargo & longer vessels are slightly more vulnerable and harder
    # to maneuver through risky areas.  We cap the factor at 1.5×.
    weight_factor = min(1.0 + (cargo_weight / 100_000) * 0.15, 1.3)
    length_factor = min(1.0 + (vessel_length / 400) * 0.1, 1.2)
    vessel_factor = weight_factor * length_factor

    multipliers = CARGO_RISK_MULTIPLIERS.get(cargo_type, CARGO_RISK_MULTIPLIERS["Dry Bulk"])

    G_dist = nx.Graph()
    G_risk = nx.Graph()

    # Add nodes with position metadata
    for node_id, wp in WAYPOINTS.items():
        attrs = {"pos": (wp.lat, wp.lon), "label": wp.name, "desc": wp.description}
        G_dist.add_node(node_id, **attrs)
        G_risk.add_node(node_id, **attrs)

    # Add edges
    for src, dst, dist_nm, risk in EDGES:
        # Pure-distance graph
        G_dist.add_edge(src, dst, weight=dist_nm, distance=dist_nm, risk_score=0)

        # Risk-penalized graph
        risk_penalty = dist_nm * (
            risk.piracy * multipliers["piracy"]
            + risk.conflict * multipliers["conflict"]
            + risk.weather * multipliers["weather"]
        ) * vessel_factor

        combined_weight = dist_nm + risk_penalty
        G_risk.add_edge(
            src, dst,
            weight=combined_weight,
            distance=dist_nm,
            risk_score=risk_penalty,
            piracy=risk.piracy,
            conflict=risk.conflict,
            weather=risk.weather,
        )

    return G_dist, G_risk


# =============================================================================
# 4. ROUTE CALCULATION
# =============================================================================
@dataclass
class RouteResult:
    """Container for a computed route and its statistics."""
    path: List[str]
    total_distance: float
    total_risk_score: float
    waypoints: List[Waypoint]
    segment_details: List[dict]


def compute_route(
    graph: nx.Graph,
    source: str = "hcm_port",
    target: str = "singapore_port",
) -> Optional[RouteResult]:
    """
    Use Dijkstra's algorithm to find the shortest-weight path between *source*
    and *target* on the given graph.  Returns a RouteResult or None if no path.
    """
    try:
        path = nx.dijkstra_path(graph, source, target, weight="weight")
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

    total_distance = 0.0
    total_risk = 0.0
    segments: List[dict] = []

    for i in range(len(path) - 1):
        edge = graph.edges[path[i], path[i + 1]]
        seg_dist = edge.get("distance", edge["weight"])
        seg_risk = edge.get("risk_score", 0)
        total_distance += seg_dist
        total_risk += seg_risk
        segments.append({
            "from": WAYPOINTS[path[i]].name,
            "to": WAYPOINTS[path[i + 1]].name,
            "distance_nm": round(seg_dist, 1),
            "risk_score": round(seg_risk, 1),
        })

    wps = [WAYPOINTS[n] for n in path]

    return RouteResult(
        path=path,
        total_distance=round(total_distance, 1),
        total_risk_score=round(total_risk, 1),
        waypoints=wps,
        segment_details=segments,
    )


# =============================================================================
# 5. MAP RENDERING (FOLIUM)
# =============================================================================
def render_map(
    shortest: Optional[RouteResult],
    safest: Optional[RouteResult],
    target_node: str = "singapore_port"
) -> folium.Map:
    """
    Build a Folium map centered on Southeast Asia showing:
      • Red polyline for the shortest-distance route
      • Green polyline for the safest (risk-optimized) route
      • Markers for each waypoint
    """
    sea_map = folium.Map(
        location=[5.5, 106.0],
        zoom_start=6,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # ── Shortest route (red / orange) ──
    if shortest:
        coords_short = [(wp.lat, wp.lon) for wp in shortest.waypoints]
        folium.PolyLine(
            coords_short,
            color="#ef4444",
            weight=4,
            opacity=0.85,
            dash_array="8 6",
            tooltip="Shortest Distance Route",
        ).add_to(sea_map)

        # Start / end markers
        folium.Marker(
            [shortest.waypoints[0].lat, shortest.waypoints[0].lon],
            icon=folium.Icon(color="red", icon="ship", prefix="fa"),
            tooltip=f"🚩 START – {shortest.waypoints[0].name}",
            popup=folium.Popup(
                f"<b>{shortest.waypoints[0].name}</b><br>{shortest.waypoints[0].description}",
                max_width=260,
            ),
        ).add_to(sea_map)

    # ── Safest route (green / teal) ──
    if safest:
        coords_safe = [(wp.lat, wp.lon) for wp in safest.waypoints]
        folium.PolyLine(
            coords_safe,
            color="#22c55e",
            weight=4,
            opacity=0.9,
            tooltip="Safest Optimal Route",
        ).add_to(sea_map)

    # ── Waypoint markers (all nodes) ──
    for node_id, wp in WAYPOINTS.items():
        is_terminal = node_id in ("hcm_port", target_node)
        is_on_shortest = shortest and node_id in shortest.path
        is_on_safest = safest and node_id in safest.path

        if is_terminal:
            icon_color = "darkblue"
            icon_name = "anchor"
        elif is_on_safest and is_on_shortest:
            icon_color = "purple"
            icon_name = "circle"
        elif is_on_shortest:
            icon_color = "red"
            icon_name = "circle"
        elif is_on_safest:
            icon_color = "green"
            icon_name = "circle"
        else:
            icon_color = "gray"
            icon_name = "circle"

        folium.Marker(
            [wp.lat, wp.lon],
            icon=folium.Icon(color=icon_color, icon=icon_name, prefix="fa"),
            tooltip=wp.name,
            popup=folium.Popup(
                f"<b>{wp.name}</b><br><em>{wp.description}</em><br>"
                f"📍 {wp.lat:.4f}°N, {wp.lon:.4f}°E",
                max_width=280,
            ),
        ).add_to(sea_map)

    # End marker
    end_wp = WAYPOINTS[target_node]
    folium.Marker(
        [end_wp.lat, end_wp.lon],
        icon=folium.Icon(color="darkblue", icon="flag-checkered", prefix="fa"),
        tooltip=f"🏁 END – {end_wp.name}",
        popup=folium.Popup(
            f"<b>{end_wp.name}</b><br>{end_wp.description}",
            max_width=260,
        ),
    ).add_to(sea_map)

    # ── Legend ──
    legend_html = """
    <div style="
        position: fixed; bottom: 30px; left: 30px; z-index: 1000;
        background: rgba(15,23,42,0.92); backdrop-filter: blur(10px);
        border: 1px solid rgba(100,150,255,0.25); border-radius: 12px;
        padding: 14px 18px; font-family: Inter, sans-serif;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);">
        <div style="color:#e2e8f0;font-weight:700;font-size:13px;margin-bottom:8px;">
            🗺️ Route Legend
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
            <div style="width:30px;height:3px;background:#ef4444;border-radius:2px;
                        border-top:2px dashed #ef4444;"></div>
            <span style="color:#f87171;font-size:12px;">Shortest Distance</span>
        </div>
        <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
            <div style="width:30px;height:3px;background:#22c55e;border-radius:2px;"></div>
            <span style="color:#4ade80;font-size:12px;">Safest Optimal</span>
        </div>
    </div>
    """
    sea_map.get_root().html.add_child(folium.Element(legend_html))

    return sea_map


# =============================================================================
# 6. HELPER FUNCTIONS – UI COMPONENTS
# =============================================================================
# (Removed text-heavy UI functions in favor of native metrics/tabs/expanders)
def risk_badge(score: float, max_score: float = 500) -> str:
    """Return an HTML risk badge (low / medium / high) based on score."""
    ratio = score / max(max_score, 1)
    if ratio < 0.25:
        return f'<span class="risk-low">● LOW RISK</span>'
    elif ratio < 0.55:
        return f'<span class="risk-medium">● MEDIUM RISK</span>'
    else:
        return f'<span class="risk-high">● HIGH RISK</span>'



def segment_table_html(segments: List[dict]) -> str:
    """Render a styled HTML table of route segments."""
    rows = ""
    for s in segments:
        rows += f"""
        <tr>
            <td>{s['from']}</td>
            <td>{s['to']}</td>
            <td style="text-align:right;">{s['distance_nm']} nm</td>
            <td style="text-align:right;">{s['risk_score']}</td>
        </tr>"""
    return f"""
    <table class="waypoint-table">
        <thead>
            <tr>
                <th>From</th>
                <th>To</th>
                <th style="text-align:right;">Distance</th>
                <th style="text-align:right;">Risk Score</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """


# =============================================================================
# 7. SIDEBAR – USER INPUTS
# =============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:10px 0 18px 0;">
            <span style="font-size:40px;">🚢</span>
            <h2 style="margin:6px 0 2px 0;font-weight:800;
                       background:linear-gradient(135deg,#60a5fa,#34d399);
                       -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                Route Optimizer
            </h2>
            <p style="color:#64748b;font-size:13px;margin:0;">
                Vietnam ➜ Southeast Asia
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("#### 🎯 Destination")
    target_selection = st.selectbox(
        "Destination Port",
        list(DESTINATIONS.keys()),
        index=0,
        help="Select the destination port in Southeast Asia."
    )
    target_node = DESTINATIONS[target_selection]

    st.divider()
    with st.expander("📦 Vessel & Cargo Parameters", expanded=True):
        cargo_weight = st.number_input(
            "Cargo Weight (tons)",
            min_value=100,
            max_value=500_000,
            value=25_000,
            step=1_000,
            help="Total weight of cargo in metric tons.",
        )
        vessel_length = st.number_input(
            "Vessel / Cargo Length (m)",
            min_value=30,
            max_value=400,
            value=180,
            step=10,
            help="Length overall (LOA) of the vessel in meters.",
        )
        cargo_type = st.selectbox(
            "Cargo Type",
            list(CARGO_RISK_MULTIPLIERS.keys()),
            index=2,
            help="Select the primary cargo classification.",
        )

    st.divider()
    with st.expander("⚙️ Risk Weight Tuning"):
        st.caption("Adjust how much each risk factor influences route selection.")
        # These sliders let the user fine-tune (advanced mode)
        piracy_weight = st.slider("Piracy Sensitivity", 0.0, 2.0, 1.0, 0.1)
        conflict_weight = st.slider("Conflict Zone Sensitivity", 0.0, 2.0, 1.0, 0.1)
        weather_weight = st.slider("Bad Weather Sensitivity", 0.0, 2.0, 1.0, 0.1)

    st.divider()
    run_btn = st.button("🧭  Find Optimal Route", type="primary", use_container_width=True)


# =============================================================================
# 8. MAIN PAGE – HEADER
# =============================================================================
st.markdown(
    """
    <div style="padding:8px 0 4px 0;">
        <div class="hero-title">Maritime Route Intelligence</div>
        <p class="hero-sub">
            Real-time route optimization & risk assessment&ensp;·&ensp;
            Ho&nbsp;Chi&nbsp;Minh&nbsp;City&ensp;➜&ensp;Southeast&nbsp;Asia
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("")


# =============================================================================
# 9. EXECUTION – BUILD GRAPH, COMPUTE, RENDER
# =============================================================================
if run_btn:
    # ── Validate inputs ──
    errors: List[str] = []
    if cargo_weight <= 0:
        errors.append("Cargo weight must be a positive number.")
    if vessel_length <= 0:
        errors.append("Vessel length must be a positive number.")
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    with st.spinner("🔄  Constructing maritime graph and computing optimal routes …"):
        # ── Apply user risk-weight tuning to the edge risks ──
        # We temporarily patch the EDGES list with tuned risk values.
        tuned_edges_backup = []
        for idx, (src, dst, dist, risk) in enumerate(EDGES):
            tuned_risk = EdgeRisk(
                piracy=risk.piracy * piracy_weight,
                conflict=risk.conflict * conflict_weight,
                weather=risk.weather * weather_weight,
            )
            tuned_edges_backup.append(EDGES[idx])
            EDGES[idx] = (src, dst, dist, tuned_risk)

        # Build graphs
        G_dist, G_risk = build_maritime_graph(cargo_weight, vessel_length, cargo_type)

        # Restore original edges
        for idx, original in enumerate(tuned_edges_backup):
            EDGES[idx] = original

        # Compute routes
        shortest_route = compute_route(G_dist, target=target_node)
        safest_route = compute_route(G_risk, target=target_node)

    if shortest_route is None or safest_route is None:
        st.error(
            f"⚠️  Could not find a valid route between Ho Chi Minh City and the selected destination. "
            "Please check the maritime graph configuration."
        )
        st.stop()

    # ── Compute Shortest Risk correctly for comparisons ──
    G_dist_check, G_risk_check = build_maritime_graph(cargo_weight, vessel_length, cargo_type)
    shortest_risk_on_risk_graph = 0.0
    for i in range(len(shortest_route.path) - 1):
        edge = G_risk_check.edges.get((shortest_route.path[i], shortest_route.path[i + 1]), {})
        shortest_risk_on_risk_graph += edge.get("risk_score", 0)
        
    risk_diff = shortest_risk_on_risk_graph - safest_route.total_risk_score if shortest_risk_on_risk_graph > safest_route.total_risk_score else 0
    dist_diff = safest_route.total_distance - shortest_route.total_distance
    pct_longer = (dist_diff / max(shortest_route.total_distance, 1)) * 100

    # ── KPI Row ──
    st.markdown("---")
    st.markdown(
        "<h3 style='color:#e2e8f0;font-weight:700;margin-bottom:2px;'>"
        "📊&ensp;Key Performance Indicators</h3>",
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            label="🟢 Safest Distance", 
            value=f"{safest_route.total_distance:,.0f} nm",
            delta=f"{dist_diff:,.0f} nm longer",
            delta_color="inverse" if dist_diff > 0 else "off"
        )
    with k2:
        st.metric(
            label="🛡️ Safest Risk Score", 
            value=f"{safest_route.total_risk_score:,.0f}",
            delta=f"- {risk_diff:,.0f} risk pts",
            delta_color="normal"
        )
    with k3:
        st.metric(
            label="🔴 Shortest Distance", 
            value=f"{shortest_route.total_distance:,.0f} nm"
        )
    with k4:
        st.metric(
            label="⚠️ Shortest Risk Score", 
            value=f"{shortest_risk_on_risk_graph:,.0f}"
        )

    st.markdown("---")

    # ── TABS ──
    tab_map, tab_compare, tab_ai = st.tabs([
        "🗺️ Interactive View", 
        "📋 Route Details", 
        "💡 Recommendations & Export"
    ])

    with tab_map:
        st.markdown(
            "<h3 style='color:#e2e8f0;font-weight:700;margin-bottom:2px;'>"
            "🗺️&ensp;Interactive Route Map</h3>",
            unsafe_allow_html=True,
        )
        st.caption("Red dashed = Shortest Distance  ·  Green solid = Safest Optimal  ·  Click markers for details")
        route_map = render_map(shortest_route, safest_route, target_node)
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        components.html(route_map._repr_html_(), height=520)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_compare:
        col_safe, col_short = st.columns(2)

        with col_safe:
            st.markdown(
                '<div class="route-compare">'
                '<h3>🟢 Safest Optimal Route</h3>',
                unsafe_allow_html=True,
            )
            st.success(f"**Pathway:** {' → '.join(wp.name for wp in safest_route.waypoints)}", icon="🟢")
            m1, m2, m3 = st.columns(3)
            m1.metric("Distance", f"{safest_route.total_distance:,.1f} nm")
            m2.metric("Risk Score", f"{safest_route.total_risk_score:,.1f}")
            eta_safe = safest_route.total_distance / 14
            m3.metric("Transit ETA", f"{eta_safe:,.1f} hrs")
            
            with st.expander("📍 View Segment Breakdown", expanded=False):
                st.markdown(segment_table_html(safest_route.segment_details), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_short:
            st.markdown(
                '<div class="route-compare">'
                '<h3>🔴 Shortest Distance Route</h3>',
                unsafe_allow_html=True,
            )
            st.warning(f"**Pathway:** {' → '.join(wp.name for wp in shortest_route.waypoints)}", icon="🔴")
            m1, m2, m3 = st.columns(3)
            m1.metric("Distance", f"{shortest_route.total_distance:,.1f} nm")
            m2.metric("Risk Score", f"{shortest_risk_on_risk_graph:,.1f}")
            eta_short = shortest_route.total_distance / 14
            m3.metric("Transit ETA", f"{eta_short:,.1f} hrs")
            
            with st.expander("📍 View Segment Breakdown", expanded=False):
                st.markdown(segment_table_html(shortest_route.segment_details), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_ai:
        same_route = shortest_route.path == safest_route.path
        if same_route:
            st.success("**Both routes are identical.** Under the current parameters, the shortest distance route is already the safest option. No trade-off required.", icon="✅")
        else:
            fuel_save_est = dist_diff * 0.06
            st.info(f"🔀 **The routes diverge.** The safest route adds **{dist_diff:,.0f} nm** (+{pct_longer:.1f}%) compared to the shortest path, but reduces the cumulative risk score by **{risk_diff:,.0f} points**.", icon="🔀")
            st.markdown(f"• **Shortest route** passes through **higher piracy & conflict zones** (South China Sea Central / Natuna Sea corridor).")
            st.markdown(f"• **Safest route** favours the **Gulf of Thailand / East Malaysia coastal** passage, which is longer but avoids disputed waters.")
            st.markdown(f"• Estimated additional fuel consumption for the safer route: ~**{fuel_save_est:,.0f} metric tons** (at 0.06 t/nm avg).")

            if cargo_type in ("Hazardous (IMDG)", "Liquid (Oil/Gas)"):
                st.error("🏷️ **Recommendation for " + cargo_type + " cargo:** Given the elevated risk profile of this cargo type, the **safest route is strongly recommended** despite the extra distance. Insurance premiums and potential incident costs far outweigh fuel savings.", icon="🚨")
            else:
                st.warning("🏷️ **Recommendation for " + cargo_type + " cargo:** Both routes are viable. Consider the safest route if **war risk insurance premiums** for the SCS corridor exceed the fuel-cost savings of the shorter path.", icon="💡")

        st.markdown("")
        st.markdown(
            "<h3 style='color:#e2e8f0;font-weight:700;'>"
            "📥&ensp;Export Route Data</h3>",
            unsafe_allow_html=True,
        )
        exp1, exp2 = st.columns(2)
        with exp1:
            df_safe = pd.DataFrame(safest_route.segment_details)
            csv_safe = df_safe.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️  Download Safest Route CSV", csv_safe, "safest_route.csv", "text/csv", use_container_width=True)
        with exp2:
            df_short = pd.DataFrame(shortest_route.segment_details)
            csv_short = df_short.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️  Download Shortest Route CSV", csv_short, "shortest_route.csv", "text/csv", use_container_width=True)

else:
    # ── Welcome state (no route calculated yet) ──
    st.markdown("")
    w1, w2, w3 = st.columns([1, 2, 1])
    with w2:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 20px;">
                <div style="font-size:72px;margin-bottom:16px;">🌏</div>
                <h2 style="color:#e2e8f0;font-weight:700;margin-bottom:8px;">
                    Configure Your Voyage
                </h2>
                <p style="color:#64748b;font-size:15px;max-width:500px;margin:0 auto;">
                    Set your vessel parameters and cargo details in the sidebar,
                    then press <strong style="color:#60a5fa;">Find Optimal Route</strong>
                    to compute the shortest and safest maritime corridors from
                    Vietnam to your selected destination in Southeast Asia.
                </p>
                <div style="margin-top:32px;display:flex;justify-content:center;gap:24px;
                            flex-wrap:wrap;">
                    <div style="text-align:center;">
                        <div style="font-size:28px;">📦</div>
                        <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                            Cargo Config
                        </div>
                    </div>
                    <div style="font-size:20px;color:#334155;align-self:center;">→</div>
                    <div style="text-align:center;">
                        <div style="font-size:28px;">🧮</div>
                        <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                            Risk Analysis
                        </div>
                    </div>
                    <div style="font-size:20px;color:#334155;align-self:center;">→</div>
                    <div style="text-align:center;">
                        <div style="font-size:28px;">🗺️</div>
                        <div style="color:#94a3b8;font-size:12px;margin-top:4px;">
                            Route Map
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Show the base map even before calculation
    st.markdown("")
    st.markdown(
        "<h3 style='color:#e2e8f0;font-weight:700;'>"
        "🗺️&ensp;Southeast Asia Maritime Overview</h3>",
        unsafe_allow_html=True,
    )
    base_map = render_map(None, None, target_node)
    components.html(base_map._repr_html_(), height=450)

    # ── Graph topology preview ──
    st.markdown("")
    st.markdown(
        "<h3 style='color:#e2e8f0;font-weight:700;'>"
        "🔗&ensp;Maritime Graph Topology</h3>",
        unsafe_allow_html=True,
    )
    st.caption("Available waypoints and route segments in the navigation graph.")

    topo_data = []
    for src, dst, dist, risk in EDGES:
        topo_data.append({
            "From": WAYPOINTS[src].name,
            "To": WAYPOINTS[dst].name,
            "Distance (nm)": dist,
            "Piracy Risk": f"{risk.piracy:.0%}",
            "Conflict Risk": f"{risk.conflict:.0%}",
            "Weather Risk": f"{risk.weather:.0%}",
        })
    st.dataframe(
        pd.DataFrame(topo_data),
        use_container_width=True,
        hide_index=True,
    )


# =============================================================================
# 10. FOOTER
# =============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;padding:16px 0 8px 0;">
        <p style="color:#475569;font-size:12px;">
            Maritime Route Optimizer v1.0 &ensp;·&ensp;
            Built with Streamlit, NetworkX & Folium &ensp;·&ensp;
            Data is simulated for demonstration purposes
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
