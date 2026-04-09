"""
TradeFlow.ai — AI-Powered Home Renovation Project Plan Generator
Streamlit App powered by Groq (Free)

MAI 104 — AI in Project Management | Final Project
Groq LLaMA reads the user description and returns a fully custom structured plan.
No keyword matching. No hard-coded archetypes. Everything driven by the description.
"""

import streamlit as st
import requests
import json
import csv
import io
import re
import time
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TradeFlow.ai — AI Renovation Planner",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f0f17; color: #f0ede8; }
    [data-testid="stSidebar"] {
        background-color: #111118;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(245,166,35,0.3);
        border-radius: 16px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    }
    .main-header h1 {
        font-size: 2.2rem; font-weight: 800; color: #f0ede8;
        margin: 0; letter-spacing: -1px;
    }
    .main-header h1 span { color: #f5a623; }
    .main-header p { color: #888898; margin: 0.5rem 0 0 0; font-size: 1rem; }
    .badge {
        display: inline-block;
        background: rgba(245,166,35,0.15); border: 1px solid rgba(245,166,35,0.4);
        color: #f5a623; font-size: 0.72rem; font-weight: 600;
        padding: 4px 12px; border-radius: 100px;
        letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.75rem;
    }
    .phase-card {
        background: #16161f; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 0.75rem;
    }
    .phase-card.hold {
        border-color: rgba(248,113,113,0.5);
        background: rgba(248,113,113,0.04);
    }
    .phase-card h4 {
        color: #f5a623; margin: 0 0 0.3rem 0;
        font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.07em;
    }
    .phase-card h3 { color: #f0ede8; margin: 0 0 0.5rem 0; font-size: 1rem; font-weight: 600; }
    .phase-card .meta { color: #888898; font-size: 0.82rem; line-height: 1.6; }
    .phase-card .note { color: #60a5fa; font-size: 0.82rem; margin-top: 0.4rem; }
    .trade-chip {
        display: inline-block;
        background: rgba(245,166,35,0.1); border: 1px solid rgba(245,166,35,0.3);
        color: #f5a623; font-size: 0.78rem; font-weight: 500;
        padding: 4px 12px; border-radius: 100px; margin: 3px;
    }
    .tradeoff-card {
        background: #16161f; border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1.2rem 1.5rem; height: 100%;
    }
    .tradeoff-card h4 { margin: 0 0 0.75rem 0; font-size: 0.95rem; font-weight: 600; }
    .tradeoff-card p { color: #888898; font-size: 0.85rem; line-height: 1.65; margin: 0; }
    .info-box {
        background: rgba(96,165,250,0.08); border: 1px solid rgba(96,165,250,0.3);
        border-radius: 10px; padding: 0.9rem 1.2rem;
        color: #93c5fd; font-size: 0.86rem; margin: 0.75rem 0;
    }
    .warn-box {
        background: rgba(245,166,35,0.08); border: 1px solid rgba(245,166,35,0.3);
        border-radius: 10px; padding: 0.9rem 1.2rem;
        color: #fcd34d; font-size: 0.86rem; margin: 0.75rem 0;
    }
    .danger-box {
        background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.3);
        border-radius: 10px; padding: 0.9rem 1.2rem;
        color: #fca5a5; font-size: 0.86rem; margin: 0.75rem 0;
    }
    .success-box {
        background: rgba(74,222,128,0.08); border: 1px solid rgba(74,222,128,0.3);
        border-radius: 10px; padding: 0.9rem 1.2rem;
        color: #86efac; font-size: 0.86rem; margin: 0.75rem 0;
    }
    .bar-wrap {
        background: #1c1c28; border-radius: 6px; overflow: hidden; height: 10px; margin-top: 5px;
    }
    .bar-fill {
        height: 10px; border-radius: 6px;
        background: linear-gradient(90deg, #f5a623, #e8693a);
    }
    [data-testid="stMetricValue"] { color: #f5a623 !important; font-size: 1.4rem !important; }
    [data-testid="stMetricLabel"] { color: #888898 !important; }
    .stButton > button {
        background: #f5a623; color: #000; border: none;
        border-radius: 10px; font-weight: 700; font-size: 0.95rem;
        padding: 0.6rem 1.5rem; width: 100%;
    }
    .stButton > button:hover { opacity: 0.85; border: none; }
    hr { border-color: rgba(255,255,255,0.08); }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GROQ CALL  —  returns fully structured JSON plan
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are TradeFlow.ai, an expert construction project manager.
A homeowner has described a home project. Read it carefully and return ONLY
a valid JSON object — no markdown fences, no prose, nothing else.

JSON schema (all fields required):
{
  "project_type": "short label — exactly what this project is, e.g. Exterior House Painting, Roof Replacement, Deck Construction, Master Bathroom Renovation, Kitchen Renovation, Landscaping, Flooring Replacement, etc.",
  "summary": "2-3 sentence plain-English overview of the full scope",
  "total_days_min": integer,
  "total_days_max": integer,
  "total_weeks_min": number,
  "total_weeks_max": number,
  "budget_estimate_min": integer,
  "budget_estimate_max": integer,
  "currency": "CAD",
  "trades": [
    { "name": "trade name", "role": "what they do on THIS project", "days": integer }
  ],
  "phases": [
    {
      "phase_number": integer,
      "phase_name": "string",
      "duration_days": integer,
      "tasks": [
    {
      "task": "task description",
      "contractor": "who does it",
      "duration_days": integer,
      "permit_required": boolean,
      "is_hold_point": boolean,
      "prerequisites": ["exact task name", "another prereq task name"],
      "dependency_note": "one sentence: why this task comes at this point in the sequence"
    }
      ]
    }
  ],
  "tradeoffs": [
    {
      "title": "the decision, e.g. DIY vs Professional Painter",
      "option_a": "label",
      "option_a_detail": "pros and cons of A for this project",
      "option_b": "label",
      "option_b_detail": "pros and cons of B for this project",
      "recommendation": "which to pick and why, given the homeowner's situation"
    }
  ],
  "risks": [
    { "level": "HIGH or MEDIUM or LOW", "risk": "what could go wrong", "mitigation": "how to prevent or handle it" }
  ],
  "homeowner_tips": ["tip 1", "tip 2", "tip 3", "tip 4", "tip 5"],
  "permits_summary": "one sentence: what permits, if any, are needed for this project type"
}

CRITICAL RULES:
1. project_type must reflect the actual project described. If the user says painting, return Exterior/Interior Painting. If roofing, return Roof Replacement. Never default to Kitchen Renovation.
2. trades must only include trades actually needed for the described scope.
3. tradeoffs must be 3-5 REAL decisions the homeowner faces for THIS specific project.
4. Each task MUST list EXACT prerequisite tasks by name in "prerequisites" array (e.g., plastering wall: ["Electrical rough-in", "Plumbing rough-in"]). Use realistic construction sequencing: framing→electrical/plumbing→insulation→drywall, etc.
5. All time and cost estimates must be realistic for Ontario, Canada.
6. Return ONLY the JSON object. Nothing before it. Nothing after it.

"""


def call_groq(api_key: str, user_desc: str, budget: str,
              timeline: str, model_name: str) -> dict:
    url = "https://api.groq.com/openai/v1/chat/completions"
    user_msg = (
        f"Project description: {user_desc}\n"
        f"Budget: {budget or 'not specified'}\n"
        f"Desired timeline: {timeline or 'not specified'}\n\n"
        "Return the JSON plan for this project."
    )
    payload = {
        "model": model_name,
        "max_tokens": 3000,
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=90)
    if resp.status_code != 200:
        raise RuntimeError(f"Groq API returned {resp.status_code}: {resp.text[:500]}")
    raw = resp.json()["choices"][0]["message"]["content"]
    raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def build_schedule_rows(plan: dict, start: datetime) -> list[dict]:
    rows = []
    cur = start
    for phase in plan.get("phases", []):
        for task in phase.get("tasks", []):
            d = max(task.get("duration_days", 1), 1)
            end = cur + timedelta(days=d)
            prereqs = ', '.join(task.get("prerequisites", [])) if task.get("prerequisites") else "None"
            rows.append({
                "Phase": phase.get("phase_name", ""),
                "Task": task.get("task", ""),
                "Contractor": task.get("contractor", ""),
                "Prerequisites": prereqs,
                "Start": cur.strftime("%Y-%m-%d"),
                "End": end.strftime("%Y-%m-%d"),
                "Days": d,
                "Permit?": "Yes" if task.get("permit_required") else "No",
                "Hold Point?": "Yes" if task.get("is_hold_point") else "No",
            })
            cur = end
    return rows

def build_dependency_graph(plan: dict):
    try:
        import networkx as nx
        import plotly.graph_objects as go
        
        G = nx.DiGraph()
        node_info = {}
        task_id = 0
        
        # Add all tasks as nodes
        for phase in plan.get('phases', []):
            for task in phase.get('tasks', []):
                task_name = task.get('task', f'Task {task_id}')
                phase_num = phase.get('phase_number', 0)
                
                node_label = f"{task_name}\\n{task.get('contractor', '')}"
                node_info[task_id] = {
                    'label': node_label,
                    'phase': phase_num,
                    'hold': task.get('is_hold_point', False),
                    'permit': task.get('permit_required', False),
                    'prereqs': task.get('prerequisites', [])
                }
                G.add_node(task_id, label=node_label)
                task_id += 1
        
        # Add edges from prerequisites
        all_tasks = {i: info['label'].split('\\n')[0].strip().lower() for i, info in node_info.items()}
        for node, info in node_info.items():
            for prereq_name in info['prereqs']:
                for other_node, task_label in all_tasks.items():
                    if other_node != node and prereq_name.lower() in task_label:
                        G.add_edge(other_node, node)
                        break
        
        if G.number_of_nodes() == 0:
            return None, 'No tasks found'
        
        pos = nx.spring_layout(G, iterations=50)
        
        # Edges
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=3, color='#f5a623'),
            hoverinfo='none',
            mode='lines',
            line_shape='spline'
        )
        
        # Nodes
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        for node in G.nodes():
            x, y = pos[node]
            info = node_info[node]
            text = info['label']
            color = '#ef4444' if info['hold'] else ('#f59e0b' if info['permit'] else '#3b82f6')
            node_x.append(x)
            node_y.append(y)
            node_text.append(text)
            node_colors.append(color)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                showscale=False,
                size=25,
                color=node_colors,
                line=dict(width=2, color='#ffffff')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                            title='📊 Task Dependencies (Arrows: prereq → task)',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=50),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        return fig, f'{G.number_of_nodes()} tasks, {G.number_of_edges()} dependencies'
    
    except Exception as e:
        return None, f'Error: {str(e)}'


def export_csv_str(rows: list[dict]) -> str:
    out = io.StringIO()
    if rows:
        w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return out.getvalue()


def export_txt_str(plan: dict, user_desc: str, budget: str) -> str:
    L = []
    sep = "=" * 68
    thin = "-" * 68
    L += [sep, f"  TRADEFLOW.AI — {plan.get('project_type','PROJECT').upper()}", sep]
    L += [f"\nGenerated : {datetime.now().strftime('%Y-%m-%d %H:%M')}"]
    L += [f"Description: {user_desc}"]
    L += [f"Budget     : {budget or 'Not specified'}"]
    L += [f"\nSUMMARY\n{plan.get('summary','')}"]
    L += [f"\nTIMELINE : {plan.get('total_weeks_min',0):.0f}–{plan.get('total_weeks_max',0):.0f} weeks"
          f" ({plan.get('total_days_min',0)}–{plan.get('total_days_max',0)} working days)"]
    blo, bhi = plan.get("budget_estimate_min",0), plan.get("budget_estimate_max",0)
    L += [f"BUDGET   : ${blo:,}–${bhi:,} {plan.get('currency','')}"]
    L += [f"\n{thin}\nTRADES INVOLVED\n{thin}"]
    for t in plan.get("trades", []):
        L.append(f"  • {t['name']} — {t.get('role','')} (~{t.get('days',0)} days)")
    L += [f"\n{thin}\nPHASE-BY-PHASE PLAN\n{thin}"]
    for phase in plan.get("phases", []):
        L.append(f"\nPHASE {phase['phase_number']}: {phase['phase_name']} ({phase.get('duration_days',0)} days)")
        for task in phase.get("tasks", []):
            flags = []
            if task.get("permit_required"): flags.append("PERMIT")
            if task.get("is_hold_point"):   flags.append("HOLD POINT")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            L.append(f"  ✓ {task['task']} | {task['contractor']} | {task.get('duration_days',1)}d{flag_str}")
            if task.get("dependency_note"):
                L.append(f"    → {task['dependency_note']}")
    L += [f"\n{thin}\nTRADE-OFFS\n{thin}"]
    for to in plan.get("tradeoffs", []):
        L.append(f"\n{to['title']}")
        L.append(f"  A — {to.get('option_a','')}: {to.get('option_a_detail','')}")
        L.append(f"  B — {to.get('option_b','')}: {to.get('option_b_detail','')}")
        L.append(f"  ✅ Recommendation: {to.get('recommendation','')}")
    L += [f"\n{thin}\nRISK REGISTER\n{thin}"]
    for r in plan.get("risks", []):
        L.append(f"  [{r['level']}] {r['risk']}")
        L.append(f"    Mitigation: {r['mitigation']}")
    L += [f"\n{thin}\nHOMEOWNER TIPS\n{thin}"]
    for i, tip in enumerate(plan.get("homeowner_tips", []), 1):
        L.append(f"  {i}. {tip}")
    L += [f"\n{sep}\n  MAI 104 — AI in Project Management | TradeFlow.ai\n{sep}"]
    return "\n".join(L)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="badge">🔑 Groq API Key</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box" style="font-size:0.78rem">'
        '🆓 <strong>100% Free.</strong> '
        '<a href="https://console.groq.com" target="_blank" style="color:#60a5fa">console.groq.com</a>'
        ' → API Keys → Create. No credit card.</div>',
        unsafe_allow_html=True,
    )
    api_key = st.text_input("API Key", type="password", placeholder="gsk_...",
                            label_visibility="collapsed")
    groq_model = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant",
         "mixtral-8x7b-32768", "gemma2-9b-it"],
        help="llama-3.3-70b gives the richest plans.",
    )
    st.markdown("---")

    st.markdown('<div class="badge">📋 Optional Details</div>', unsafe_allow_html=True)
    budget    = st.text_input("Budget", placeholder="e.g. $8,000")
    timeline  = st.text_input("Desired Timeline", placeholder="e.g. 3 weeks")
    start_date = st.date_input("Start Date", value=datetime.today())
    st.markdown("---") 
    
    


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div class="badge">MAI 104 — AI in Project Management</div>
  <h1>TradeFlow<span>.ai</span></h1>
  <p>Describe any home project — get a fully custom plan with trades, timeline, tradeoffs &amp; risks.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### 📝 Describe Your Project")
st.markdown(
    '<div class="info-box">'
    '💡 Describe <strong>any</strong> home project in plain language — painting, roofing, deck, '
    'bathroom, flooring, landscaping, etc. Groq reads your description and builds a completely '
    'custom plan. No dropdown. No templates.<br>'
    '<strong>Examples:</strong> '
    '<em>"paint the exterior of my two-storey house"</em> &nbsp;·&nbsp; '
    '<em>"replace the roof on my bungalow"</em> &nbsp;·&nbsp; '
    '<em>"build a 12×16 backyard deck"</em> &nbsp;·&nbsp; '
    '<em>"gut and redo the master bathroom"</em>'
    '</div>',
    unsafe_allow_html=True,
)
user_desc = st.text_area(
    "description",
    placeholder=(
        "e.g. I want to paint the exterior of my two-storey detached house. "
        "It has about 2,000 sq ft of painted surface — siding, trim, fascia, and two garage doors. "
        "The current paint is peeling in a few spots. I'd like premium exterior latex. "
        "Budget around $8,000, ideally done within 3 weeks."
    ),
    height=150,
    label_visibility="collapsed",
)
generate_btn = st.button("✨ Generate My Plan", use_container_width=True)
st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE
# ─────────────────────────────────────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.error("⚠️ Enter your Groq API key in the sidebar.")
        st.stop()
    if not user_desc.strip():
        st.error("⚠️ Please describe your project first.")
        st.stop()

    with st.spinner("🤖 Groq is reading your description and building a custom plan..."):
        t0 = time.time()
        try:
            plan = call_groq(api_key, user_desc, budget, timeline, groq_model)
            elapsed = time.time() - t0
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON parse error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Groq API error: {e}")
            st.stop()

    rows = build_schedule_rows(plan, datetime.combine(start_date, datetime.min.time()))
    st.session_state.update({
        "plan": plan, "rows": rows,
        "user_desc": user_desc, "budget": budget,
        "elapsed": elapsed, "model": groq_model,
    })


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if "plan" in st.session_state:
    plan      = st.session_state["plan"]
    rows      = st.session_state["rows"]
    user_desc = st.session_state["user_desc"]
    budget    = st.session_state["budget"]
    elapsed   = st.session_state["elapsed"]
    model     = st.session_state["model"]

    proj_type = plan.get("project_type", "Custom Project")

    st.markdown(
        f'<div class="success-box">✅ Plan generated in <strong>{elapsed:.1f}s</strong> '
        f'using <strong>{model}</strong> &nbsp;·&nbsp; '
        f'Project detected: <strong>{proj_type}</strong></div>',
        unsafe_allow_html=True,
    )

    # top metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Project", proj_type[:18])
    with c2:
        st.metric("Timeline",
                  f"{plan.get('total_weeks_min',0):.0f}–{plan.get('total_weeks_max',0):.0f} wks")
    with c3:
        st.metric("Working Days",
                  f"{plan.get('total_days_min',0)}–{plan.get('total_days_max',0)}")
    with c4:
        st.metric("Trades", len(plan.get("trades", [])))
    with c5:
        blo = plan.get("budget_estimate_min", 0)
        bhi = plan.get("budget_estimate_max", 0)
        st.metric("Est. Budget", f"${blo:,}–${bhi:,}")

    # Dependency metric
    total_deps = sum(len(task.get('prerequisites', [])) for phase in plan.get('phases', []) for task in phase.get('tasks', []))
    c6, = st.columns(1)
    with c6:
        st.metric("Dependencies", total_deps)

    st.markdown(
        '<div class="warn-box">⚠️ AI-generated guidance only. '
        'Verify costs, permits and timelines with licensed contractors in your area.</div>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Overview", "🗓️ Phase Plan", "📊 Dependencies", "⚖️ Trade-Offs", "⚠️ Risks & Tips", "⬇️ Export"
    ])

    # ── TAB 1: OVERVIEW ──────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Project Summary")
        st.markdown(
            f'<div class="phase-card"><p style="color:#f0ede8;font-size:1rem;'
            f'line-height:1.75;margin:0">{plan.get("summary","")}</p></div>',
            unsafe_allow_html=True,
        )

        permits = plan.get("permits_summary", "")
        if permits:
            st.markdown(
                f'<div class="warn-box">🔴 <strong>Permits:</strong> {permits}</div>',
                unsafe_allow_html=True,
            )

        # Trades chips
        st.markdown("### Trades Involved")
        chips = "".join(
            f'<span class="trade-chip">🔨 {t["name"]}</span>'
            for t in plan.get("trades", [])
        )
        st.markdown(chips, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # Trades bars
        st.markdown("#### Time allocated per trade")
        trades = plan.get("trades", [])
        max_days = max((t.get("days", 1) for t in trades), default=1)
        for t in trades:
            d = t.get("days", 1)
            pct = max(int(d / max_days * 100), 4)
            st.markdown(f"""
<div style="margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;font-size:0.84rem;margin-bottom:4px">
    <span style="color:#f0ede8;font-weight:500">{t['name']}</span>
    <span style="color:#888898">{t.get('role','')} &nbsp;·&nbsp;
      <strong style="color:#f5a623">{d} day(s)</strong></span>
  </div>
  <div class="bar-wrap"><div class="bar-fill" style="width:{pct}%"></div></div>
</div>""", unsafe_allow_html=True)

        # Phase timeline bars
        st.markdown("### Timeline Overview")
        phases = plan.get("phases", [])
        max_p = max((p.get("duration_days", 1) for p in phases), default=1)
        for phase in phases:
            d = phase.get("duration_days", 0)
            pct = max(int(d / max_p * 100), 3)
            n_tasks = len(phase.get("tasks", []))
            st.markdown(f"""
<div style="margin-bottom:12px">
  <div style="display:flex;justify-content:space-between;font-size:0.83rem;margin-bottom:4px">
    <span style="color:#f5a623;font-weight:600">
      Phase {phase['phase_number']}: {phase['phase_name']}
    </span>
    <span style="color:#888898">{n_tasks} task(s) &nbsp;·&nbsp;
      <strong style="color:#f0ede8">{d} day(s)</strong></span>
  </div>
  <div class="bar-wrap"><div class="bar-fill" style="width:{pct}%"></div></div>
</div>""", unsafe_allow_html=True)

    # ── TAB 2: PHASE PLAN ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Phase-by-Phase Plan")
        st.markdown(
            f'<div class="info-box">📅 Total estimate: '
            f'<strong>{plan.get("total_days_min",0)}–{plan.get("total_days_max",0)} working days</strong> '
            f'({plan.get("total_weeks_min",0):.1f}–{plan.get("total_weeks_max",0):.1f} weeks).'
            f' Sequential — parallel scheduling could shorten this.</div>',
            unsafe_allow_html=True,
        )

        for phase in plan.get("phases", []):
            tasks = phase.get("tasks", [])
            has_permit = any(t.get("permit_required") for t in tasks)
            has_hold   = any(t.get("is_hold_point")   for t in tasks)
            label = (
                f"**Phase {phase['phase_number']}: {phase['phase_name']}** "
                f"— {phase.get('duration_days',0)} day(s) · {len(tasks)} tasks"
                + (" · 🔴 PERMIT" if has_permit else "")
                + (" · ⛔ HOLD" if has_hold else "")
            )
            with st.expander(label, expanded=True):
                for task in tasks:
                    is_hold   = task.get("is_hold_point", False)
                    is_permit = task.get("permit_required", False)
                    card_cls  = "phase-card hold" if is_hold else "phase-card"
                    badge_html = ""
                    if task.get('prerequisites'):
                        prereq_str = ', '.join(task.get('prerequisites', [])[:2])
                        if len(task.get('prerequisites', [])) > 2:
                            prereq_str += ' +{} more'.format(len(task.get('prerequisites', []))-2)
                        badge_html += f' <span style="background:rgba(59,130,246,0.15);color:#60a5fa;font-size:0.74rem;padding:2px 8px;border-radius:6px;font-weight:600">⛓️ {prereq_str}</span>'
                    if is_permit:
                        badge_html += (' <span style="background:rgba(248,113,113,0.15);'
                                       'color:#fca5a5;font-size:0.74rem;padding:2px 8px;'
                                       'border-radius:6px;font-weight:600">🔴 PERMIT</span>')
                    if is_hold:
                        badge_html += (' <span style="background:rgba(248,113,113,0.15);'
                                       'color:#fca5a5;font-size:0.74rem;padding:2px 8px;'
                                       'border-radius:6px;font-weight:600">⛔ HOLD POINT</span>')
                    st.markdown(f"""
<div class="{card_cls}">
  <h4>Phase {phase['phase_number']} — {phase['phase_name']}</h4>
  <h3>{task.get('task','')} {badge_html}</h3>
  <p class="meta">
    🔨 <strong>{task.get('contractor','')}</strong>
    &nbsp;|&nbsp; ⏱ <strong>{task.get('duration_days',1)} day(s)</strong>
  </p>
  <p class="note">{task.get('dependency_note','')}</p>
</div>""", unsafe_allow_html=True)

    # ── TAB 3: DEPENDENCIES ───────────────────────────────────────────────────
    with tab3:
        st.markdown("### 📊 Task Dependencies")
        st.markdown('<div class="info-box">Visual graph showing prerequisite relationships between tasks. Arrows point from prerequisites to dependent tasks. Red nodes are hold points.</div>', unsafe_allow_html=True)
        
        fig, stats = build_dependency_graph(plan)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            st.success(f"✅ {stats}")
        else:
            st.warning(stats)
        
        # Text fallback table
        st.markdown("#### Dependencies Table")
        dep_table = []
        for phase in plan.get("phases", []):
            for task in phase.get("tasks", []):
                if task.get("prerequisites"):
                    dep_table.append({
                        "Task": task.get("task", ""),
                        "Contractor": task.get("contractor", ""),
                        "Prerequisites": ", ".join(task.get("prerequisites", []))
                    })
        if dep_table:
            import pandas as pd
            df = pd.DataFrame(dep_table)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No explicit prerequisites detected (sequential by phase order)")
    
    # ── TAB 4: TRADE-OFFS ────────────────────────────────────────────────────
    with tab4:
        st.markdown("### ⚖️ Trade-Offs for This Project")
        st.markdown(
            '<div class="info-box">These are the real decisions you\'ll face. '
            'Understanding them upfront helps you brief contractors correctly '
            'and avoid mid-project regret.</div>',
            unsafe_allow_html=True,
        )

        for to in plan.get("tradeoffs", []):
            st.markdown(f"#### ⚖️ {to.get('title','')}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
<div class="tradeoff-card" style="border-color:rgba(96,165,250,0.35)">
  <h4 style="color:#60a5fa">Option A — {to.get('option_a','')}</h4>
  <p>{to.get('option_a_detail','')}</p>
</div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
<div class="tradeoff-card" style="border-color:rgba(245,166,35,0.35)">
  <h4 style="color:#f5a623">Option B — {to.get('option_b','')}</h4>
  <p>{to.get('option_b_detail','')}</p>
</div>""", unsafe_allow_html=True)
            st.markdown(
                f'<div class="success-box" style="margin-top:8px">'
                f'✅ <strong>Recommendation:</strong> {to.get("recommendation","")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("---")

    # ── TAB 5: RISKS & TIPS ──────────────────────────────────────────────────
    with tab5:
        st.markdown("### ⚠️ Risk Register")
        color_map = {"HIGH": "danger-box", "MEDIUM": "warn-box", "LOW": "info-box"}
        for r in plan.get("risks", []):
            box = color_map.get(r.get("level", "LOW"), "info-box")
            st.markdown(
                f'<div class="{box}"><strong>[{r["level"]}]</strong> {r["risk"]}<br>'
                f'<em>Mitigation: {r["mitigation"]}</em></div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### 💡 Homeowner Tips")
        for i, tip in enumerate(plan.get("homeowner_tips", []), 1):
            st.markdown(
                f'<div class="phase-card" style="margin-bottom:8px">'
                f'<span style="color:#f5a623;font-weight:700">{i}.</span> '
                f'<span style="color:#f0ede8">{tip}</span></div>',
                unsafe_allow_html=True,
            )

    # ── TAB 6: EXPORT ────────────────────────────────────────────────────────
    with tab6:
        st.markdown("### ⬇️ Export Your Plan")
        proj_slug = proj_type.replace(" ", "_")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "⬇️ Full Plan (.txt)",
                data=export_txt_str(plan, user_desc, budget),
                file_name=f"TradeFlow_{proj_slug}.txt",
                mime="text/plain", use_container_width=True,
            )
        with c2:
            st.download_button(
                "⬇️ Schedule (.csv)",
                data=export_csv_str(rows),
                file_name=f"TradeFlow_{proj_slug}_Schedule.csv",
                mime="text/csv", use_container_width=True,
            )
        with c3:
            st.download_button(
                "⬇️ Full JSON",
                data=json.dumps(plan, indent=2),
                file_name=f"TradeFlow_{proj_slug}.json",
                mime="application/json", use_container_width=True,
            )

        if rows:
            st.markdown("---")
            st.markdown("#### Schedule Preview")
            import pandas as pd
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# WELCOME STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
<div style="background:#16161f;border:1px solid rgba(255,255,255,0.08);
     border-radius:16px;padding:2.5rem;text-align:center;margin:2rem 0">
  <div style="font-size:3rem;margin-bottom:1rem">🏗️</div>
  <h3 style="color:#f0ede8;margin:0 0 0.75rem 0">Describe any home project — get a custom plan</h3>
  <p style="color:#888898;max-width:580px;margin:0 auto;line-height:1.75">
    Painting, roofing, decks, bathrooms, flooring, landscaping — just describe it.
    Groq reads your words and generates <strong style="color:#f5a623">a fully custom plan</strong>
    with the right trades, correct phase order, time estimates, trade-off analysis, and risk register.
    No dropdowns. No templates. Just describe your project.
  </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("### What you get")
    cols = st.columns(5)
    items = [
        ("🔍", "Smart Detection",  "Project type identified from your own words — painting stays painting"),
        ("🔨", "Trades & Time",    "Every trade needed, with days allocated and time-to-completion estimate"),
        ("🗓️", "Phase Plan",       "Tasks in correct order with one-sentence dependency explanation per task"),
        ("⚖️", "Trade-Offs",       "3–5 real decisions you face: DIY vs pro, budget vs premium, speed vs cost"),
        ("📤", "3 Export Formats", "Download .txt plan, .csv schedule (MS Project), or full .json"),
    ]
    for col, (icon, title, desc) in zip(cols, items):
        with col:
            st.markdown(f"""
<div class="phase-card" style="text-align:center;height:100%">
  <div style="font-size:1.8rem;margin-bottom:0.5rem">{icon}</div>
  <h3 style="text-align:center;font-size:0.88rem;margin-bottom:8px">{title}</h3>
  <p class="meta" style="text-align:center;font-size:0.8rem">{desc}</p>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#555568;font-size:0.8rem;padding:1rem 0">
  <strong style="color:#888898">TradeFlow.ai</strong> &nbsp;·&nbsp;
  MAI 104 — AI in Project Management &nbsp;·&nbsp;
  Powered by Groq (Free) &nbsp;·&nbsp; © 2025
</div>
""", unsafe_allow_html=True)