import streamlit as st
import pandas as pd
import json
import datetime

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="广岛生活助手 Pro",
    page_icon="♻️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. 高级感 CSS 样式 (炫酷版) ---
st.markdown("""
    <style>
    /* 引入现代字体 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans JP', 'Helvetica Neue', sans-serif;
        background-color: #f7f9fc;
    }
    
    /* 隐藏默认头部 */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* 卡片基础样式 */
    .garbage-card {
        background: #ffffff;
        border-radius: 24px;
        padding: 30px 25px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.04);
        border: 1px solid rgba(255,255,255,0.7);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
    }
    
    .garbage-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
    }

    /* 重点卡片（明天）的高亮样式 */
    .card-highlight {
        border: 2px solid #6c5ce7;
        background: linear-gradient(145deg, #ffffff 0%, #f8f7ff 100%);
        box-shadow: 0 15px 35px rgba(108, 92, 231, 0.1);
    }
    
    /* 标签标记 */
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
        align-self: center;
    }
    .badge-tomorrow { background: #6c5ce7; color: white; }
    .badge-today { background: #f1f2f6; color: #57606f; }

    /* 日期文字 */
    .card-date {
        font-size: 0.9rem;
        color: #a4b0be;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    /* 垃圾名称大字 */
    .garbage-title {
        font-size: 2rem;
        font-weight: 800;
        color: #2f3542;
        line-height: 1.2;
        margin: 10px 0;
    }
    
    /* 标题区域 */
    .main-header {
        text-align: center;
        padding: 40px 0 20px 0;
        font-weight: 900;
        font-size: 2.4rem;
        background: linear-gradient(135deg, #6c5ce7, #00cec9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 选项卡美化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #f1f2f6;
        border-radius: 20px;
        color: #57606f;
        padding: 0 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #6c5ce7 !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 逻辑处理 ---

@st.cache_data
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"schedule_rules": {}, "dictionary": []}

data = load_data()

def get_week_of_month(date):
    return (date.day - 1) // 7 + 1

def get_garbage_info(target_date):
    rules = data.get("schedule_rules", {})
    weekday_name = target_date.strftime("%A")
    rule = rules.get(weekday_name, [])
    
    if not rule: return []
    if isinstance(rule, list): return rule
    if isinstance(rule, dict):
        week_num = get_week_of_month(target_date)
        if rule.get("type") == "alternating":
            return rule.get("odd_weeks", []) if week_num in [1, 3, 5] else rule.get("even_weeks", [])
        if rule.get("type") == "monthly_rule":
            special = rule.get("special", {})
            if special.get("condition") == "2nd_week" and week_num == 2:
                return special.get("item", [])
            else:
                return rule.get("default", [])
    return []

def render_card(title, date_obj, is_highlight=False):
    """渲染精简后的高级卡片"""
    garbage_list = get_garbage_info(date_obj)
    date_str = date_obj.strftime("%m月%d日")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    highlight_class = "card-highlight" if is_highlight else ""
    badge_class = "badge-tomorrow" if is_highlight else "badge-today"
    badge_text = "✨ 明天准备" if is_highlight else "📅 今天状况"
    
    if not garbage_list:
        content_html = '<div class="garbage-title" style="color: #dfe4ea;">无收集 ☕</div>'
    else:
        names_html = "".join([f"<div>{g}</div>" for g in garbage_list])
        content_html = f'<div class="garbage-title">{names_html}</div>'
        
    html = f"""
    <div class="garbage-card {highlight_class}">
        <div class="badge {badge_class}">{badge_text}</div>
        <div class="card-date">{date_str} · {weekday_cn}</div>
        {content_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# --- 4. 主界面布局 ---

st.markdown('<div class="main-header">広島生活助手</div>', unsafe_allow_html=True)

now = datetime.datetime.now()
today = now.date()
tomorrow = today + datetime.timedelta(days=1)

# === 核心区域：明天(左) vs 今天(右) ===
col_tomorrow, col_today = st.columns([1.1, 0.9])

with col_tomorrow:
    render_card("明天", tomorrow, is_highlight=True)

with col_today:
    render_card("今天", today, is_highlight=False)

st.markdown("<br>", unsafe_allow_html=True)

# === 功能区 ===
tab1, tab2, tab3 = st.tabs(["🔍 分类查询", "🗓 本周日程", "📘 投放指南"])

with tab1:
    search_query = st.text_input("", placeholder="输入想扔的物品 (如: 电池, 披萨盒...)", label_visibility="collapsed")
    
    if search_query:
        df = pd.DataFrame(data["dictionary"])
        result = df[df['item'].str.contains(search_query, case=False, na=False)]
        
        if not result.empty:
            for _, row in result.iterrows():
                st.markdown(f"""
                <div style="background:white; padding:18px; border-radius:16px; margin-bottom:12px; border-left:5px solid #6c5ce7; box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                    <div style="font-weight:700; font-size:1.1rem; color:#2f3542;">{row['item']}</div>
                    <div style="color:#6c5ce7; font-weight:600; margin-top:4px;">→ {row['type']}</div>
                    {f'<div style="font-size:0.85rem; color:#a4b0be; margin-top:6px;">💡 {row["note"]}</div>' if row['note'] else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("查不到呢，试试输入更简单的词？")
    else:
        st.caption("🔍 快速查询 8 种垃圾分类规则")

with tab2:
    st.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
    for i in range(7):
        d = today + datetime.timedelta(days=i)
        g = get_garbage_info(d)
        w_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]
        
        if g:
            g_text = " / ".join(g)
            color = "#ff7675" if "可燃" in g_text else "#74b9ff" if "塑料" in g_text else "#55efc4"
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #f1f2f6;'>
                <span style='color:#57606f; font-weight:600;'>{d.strftime("%m/%d")} ({w_str})</span>
                <span style='color:{color}; font-weight:700;'>{g_text}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #f1f2f6; opacity:0.3;'>
                <span>{d.strftime("%m/%d")} ({w_str})</span>
                <span>休息</span>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div style="background:#fff7e6; padding:20px; border-radius:16px; border-left:5px solid #ffa502; color:#7f8c8d;">
        <h4 style="margin-top:0; color:#e67e22;">📌 投放须知</h4>
        <ul style="padding-left:20px; margin-bottom:0;">
            <li><b>时间：</b> 早上 8:30 前准时投放。</li>
            <li><b>厨余：</b> 丢弃前请务必沥干水分。</li>
            <li><b>电池：</b> 请贴上绝缘胶带并放入有害垃圾。</li>
            <li><b>容器：</b> 请冲洗干净后再作为塑料类回收。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Designed for Hiroshima South District | 2025 Edition")
