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
    }
    
    /* 隐藏默认头部 */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* 卡片基础样式 */
    .garbage-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05); /* 柔和阴影 */
        border: 1px solid #f0f0f0;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .garbage-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }

    /* 重点卡片（明天）的高亮样式 */
    .card-highlight {
        border: 2px solid #6c5ce7; /* 紫色边框 */
        background: linear-gradient(145deg, #ffffff 0%, #fdfdff 100%);
    }
    
    /* 标签标记 */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .badge-tomorrow { background: linear-gradient(90deg, #6c5ce7, #a29bfe); }
    .badge-today { background: linear-gradient(90deg, #b2bec3, #dfe6e9); color: #636e72; }

    /* 日期文字 */
    .card-date {
        font-size: 1rem;
        color: #b2bec3;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    /* 垃圾名称大字 */
    .garbage-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 10px 0;
        color: #2d3436;
        letter-spacing: -0.5px;
    }
    
    /* 详细描述区域 */
    .garbage-desc {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 12px;
        font-size: 0.9rem;
        color: #636e72;
        line-height: 1.6;
        margin-top: 15px;
        border-left: 4px solid #dfe6e9;
    }

    /* 颜色定义 (用于动态边框) */
    .color-burn { border-left-color: #ff7675 !important; }
    .color-plastic { border-left-color: #74b9ff !important; }
    .color-resource { border-left-color: #55efc4 !important; }
    .color-toxic { border-left-color: #ffeaa7 !important; }
    .color-other { border-left-color: #a29bfe !important; }
    
    /* 搜索框美化 */
    .stTextInput input {
        border-radius: 50px !important;
        padding: 10px 20px !important;
        border: 2px solid #dfe6e9 !important;
        transition: border 0.3s;
    }
    .stTextInput input:focus {
        border-color: #6c5ce7 !important;
        box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.2) !important;
    }
    
    /* 标题区域 */
    .main-header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        background: linear-gradient(90deg, #6c5ce7, #00cec9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 逻辑处理 (保持不变) ---

@st.cache_data
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"schedule_rules": {}, "dictionary": [], "descriptions": {}}

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

def get_desc_color_class(garbage_name):
    if "可燃" in garbage_name: return "color-burn"
    if "塑料" in garbage_name or "PET" in garbage_name: return "color-plastic"
    if "资源" in garbage_name: return "color-resource"
    if "有害" in garbage_name: return "color-toxic"
    return "color-other"

def render_card(title, date_obj, is_highlight=False):
    """渲染高级卡片"""
    garbage_list = get_garbage_info(date_obj)
    date_str = date_obj.strftime("%m/%d")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    # 样式判断
    highlight_class = "card-highlight" if is_highlight else ""
    badge_class = "badge-tomorrow" if is_highlight else "badge-today"
    badge_text = "✨ 明天准备" if is_highlight else "📅 今天状况"
    
    if not garbage_list:
        html = f"""
        <div class="garbage-card {highlight_class}">
            <div class="badge {badge_class}">{badge_text}</div>
            <div class="card-date">{date_str} {weekday_cn}</div>
            <div class="garbage-title" style="color: #b2bec3;">无收集 ☕</div>
            <div class="garbage-desc">无需扔垃圾，轻松的一天。</div>
        </div>
        """
    else:
        # 获取描述和颜色
        main_garbage = garbage_list[0]
        desc_map = data.get("descriptions", {})
        description = "暂无详细描述"
        color_class = get_desc_color_class(main_garbage)
        
        # 匹配描述
        for key, value in desc_map.items():
            if key in main_garbage:
                description = value
                break
                
        # 拼接名称
        names_html = "".join([f"<div>{g}</div>" for g in garbage_list])
        
        html = f"""
        <div class="garbage-card {highlight_class}">
            <div class="badge {badge_class}">{badge_text}</div>
            <div class="card-date">{date_str} {weekday_cn}</div>
            <div class="garbage-title">{names_html}</div>
            <div class="garbage-desc {color_class}">
                <b>💡 包含物品：</b><br>{description}
            </div>
        </div>
        """
    
    st.markdown(html, unsafe_allow_html=True)

# --- 4. 主界面布局 ---

st.markdown('<div class="main-header">広島 Life Helper</div>', unsafe_allow_html=True)

now = datetime.datetime.now()
today = now.date()
tomorrow = today + datetime.timedelta(days=1)

# === 核心区域：左右互换 ===
# 左侧放明天（高亮），右侧放今天
col_tomorrow, col_today = st.columns([1.1, 1]) # 左侧稍微宽一点点，强调明天

with col_tomorrow:
    render_card("明天", tomorrow, is_highlight=True)

with col_today:
    render_card("今天", today, is_highlight=False)

# === 功能区 ===
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["🔍 极速查询", "🗓 本周概览", "📘 投放指南"])

with tab1:
    col_search, _ = st.columns([3, 1])
    with col_search:
        search_query = st.text_input("", placeholder="输入物品名称 (如: 电池, 披萨盒...)", label_visibility="collapsed")
    
    if search_query:
        df = pd.DataFrame(data["dictionary"])
        result = df[df['item'].str.contains(search_query, case=False, na=False)]
        
        if not result.empty:
            for _, row in result.iterrows():
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:10px; margin-bottom:10px; border-left:4px solid #6c5ce7; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                    <div style="font-weight:bold; font-size:1.1rem;">{row['item']}</div>
                    <div style="color:#6c5ce7; margin-top:5px;">分类：{row['type']}</div>
                    <div style="font-size:0.85rem; color:#888; margin-top:5px;">{f"⚠️ {row['note']}" if row['note'] else ""}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("🤔 未找到匹配项，请尝试输入更通用的名称。")
    else:
        st.caption("👆 在上方输入想要丢弃的物品，立即获取分类建议。")

with tab2:
    st.markdown("##### 未来7天日程表")
    for i in range(7):
        d = today + datetime.timedelta(days=i)
        g = get_garbage_info(d)
        d_str = d.strftime("%m/%d")
        w_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]
        
        # 简单列表样式
        if g:
            g_text = " / ".join(g)
            icon = "🔴" if "可燃" in g_text else "🔵" if "塑料" in g_text else "🟢"
            st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid #eee;'><b>{d_str} ({w_str})</b> <span style='float:right; color:#2d3436;'>{icon} {g_text}</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='padding:8px 0; border-bottom:1px solid #eee; color:#b2bec3;'>{d_str} ({w_str}) <span style='float:right;'>休息</span></div>", unsafe_allow_html=True)

with tab3:
    st.info("💡 早上 8:30 前请务必将垃圾排出。")
    with st.expander("❓ 常见易错分类"):
        st.markdown("""
        * **必看！食用油**：不能直接倒！要用凝固剂或吸油纸处理后扔 **可燃垃圾**。
        * **喷雾罐**：必须彻底用完，扔 **资源垃圾** 或 **有害垃圾**（视具体区域可能有细微差别，请确认罐体说明）。
        * **披萨盒**：如果沾有油渍，不能回收，属于 **可燃垃圾**。
        """)
