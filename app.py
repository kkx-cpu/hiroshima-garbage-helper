import streamlit as st
import pandas as pd
import json
import datetime

# --- 1. 页面配置与 CSS 样式 ---
st.set_page_config(
    page_title="广岛生活助手",
    page_icon="🍃",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 高级感 CSS：卡片阴影、圆角、字体优化
st.markdown("""
    <style>
    /* 全局字体优化 */
    .main { font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", sans-serif; }
    
    /* 垃圾卡片样式 */
    .garbage-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border: 1px solid #f0f0f0;
        transition: transform 0.2s;
    }
    .garbage-card:hover { transform: translateY(-2px); }
    
    /* 标题样式 */
    .card-title { font-size: 1.1rem; color: #888; margin-bottom: 5px; font-weight: 600; }
    .garbage-name { font-size: 1.6rem; font-weight: bold; margin-bottom: 10px; color: #333; }
    .garbage-examples { font-size: 0.9rem; color: #666; line-height: 1.5; background-color: #f8f9fa; padding: 10px; border-radius: 8px; }
    
    /* 颜色标签 */
    .tag { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; color: white; margin-right: 5px; }
    .tag-burn { background-color: #ff6b6b; } /* 可燃-红 */
    .tag-plastic { background-color: #4ecdc4; } /* 塑料-青 */
    .tag-resource { background-color: #95a5a6; } /* 资源-灰 */
    .tag-toxic { background-color: #f7b731; } /* 有害-黄 */
    .tag-other { background-color: #a55eea; } /* 其他-紫 */
    
    /* 搜索框美化 */
    .stTextInput>div>div>input { border-radius: 20px; border: 1px solid #ddd; }
    
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. 数据加载与处理逻辑 ---

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
    """返回：(垃圾名称列表, 原始规则对象)"""
    rules = data.get("schedule_rules", {})
    weekday_name = target_date.strftime("%A")
    rule = rules.get(weekday_name, [])
    
    if not rule: return []
    
    if isinstance(rule, list):
        return rule
    
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

def get_style_class(garbage_name):
    """根据垃圾类型返回 CSS 类名"""
    if "可燃" in garbage_name: return "tag-burn"
    if "塑料" in garbage_name or "PET" in garbage_name: return "tag-plastic"
    if "资源" in garbage_name: return "tag-resource"
    if "有害" in garbage_name: return "tag-toxic"
    return "tag-other"

def render_garbage_card(title, date_obj, garbage_list):
    """渲染精美的 HTML 卡片"""
    date_str = date_obj.strftime("%m/%d")
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date_obj.weekday()]
    
    if not garbage_list:
        html_content = f"""
        <div class="garbage-card" style="border-left: 5px solid #ddd;">
            <div class="card-title">{title} · {date_str} ({weekday_cn})</div>
            <div class="garbage-name" style="color: #aaa;">☕ 无收集</div>
            <div class="garbage-examples">无需倒垃圾，享受生活吧。</div>
        </div>
        """
    else:
        # 获取详细描述
        main_garbage = garbage_list[0]
        desc_map = data.get("descriptions", {})
        # 简单的模糊匹配来找描述
        description = "暂无详细描述"
        for key, value in desc_map.items():
            if key in main_garbage:
                description = value
                break
        
        style_class = get_style_class(main_garbage)
        color_hex = "#ff6b6b" if "可燃" in main_garbage else "#4ecdc4" if "塑料" in main_garbage else "#95a5a6"
        
        # 拼接多个垃圾类型
        garbage_html = ""
        for g in garbage_list:
             garbage_html += f"<span>{g}</span><br>"

        html_content = f"""
        <div class="garbage-card" style="border-left: 5px solid {color_hex};">
            <div class="card-title">{title} · {date_str} ({weekday_cn})</div>
            <div class="garbage-name">{garbage_html}</div>
            <div class="garbage-examples">💡 <b>请扔：</b>{description}</div>
        </div>
        """
    
    st.markdown(html_content, unsafe_allow_html=True)

# --- 3. 主界面布局 ---

st.title("🍃 广岛生活助手")
st.caption("📍 南区 (段原・皆实町区域)")

# 获取日期
now = datetime.datetime.now()
today = now.date()
tomorrow = today + datetime.timedelta(days=1)

# === 核心功能区：今天 vs 明天 ===
st.subheader("📅 投放提醒")
col1, col2 = st.columns(2)

with col1:
    g_today = get_garbage_info(today)
    render_garbage_card("今天", today, g_today)

with col2:
    g_tomorrow = get_garbage_info(tomorrow)
    render_garbage_card("明天", tomorrow, g_tomorrow)

# === 功能分栏 ===
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["🔍 垃圾分类搜", "🗓 本周日程", "📘 投放指南"])

# Tab 1: 搜索
with tab1:
    search_query = st.text_input("输入物品名称...", placeholder="例如：鸡蛋壳, 电池, pizza盒")
    if search_query:
        df = pd.DataFrame(data["dictionary"])
        result = df[df['item'].str.contains(search_query, case=False, na=False)]
        
        if not result.empty:
            for _, row in result.iterrows():
                # 使用 Streamlit 原生卡片样式
                with st.container():
                    c1, c2 = st.columns([1, 3])
                    with c1:
                        st.markdown(f"**{row['item']}**")
                    with c2:
                        st.markdown(f":red[{row['type']}]")
                        if row['note']:
                            st.caption(f"注意：{row['note']}")
                    st.divider()
        else:
            st.info("🤔 词典里没找到，请参考下方通用规则。")

# Tab 2: 本周日程
with tab2:
    for i in range(7):
        d = today + datetime.timedelta(days=i)
        g = get_garbage_info(d)
        d_str = d.strftime("%m/%d")
        w_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]
        
        if g:
            st.markdown(f"**{d_str} ({w_str})** : {', '.join(g)}")
        else:
            st.markdown(f"<span style='color:#ccc'>{d_str} ({w_str}) : 无收集</span>", unsafe_allow_html=True)

# Tab 3: 指南
with tab3:
    st.markdown("""
    #### ⚠️ 常见错误提示
    * **食用油**：不能直接倒下水道，需用报纸吸干或凝固后扔 **可燃垃圾**。
    * **喷雾罐**：必须用完，不要打孔，扔 **资源垃圾** 或 **不燃垃圾**（视具体规定）。
    * **大型垃圾**：最长边超过 30cm 的通常需要预约收费回收。
    
    #### 🕒 投放时间
    请在收集日当天 **早上 8:30 前** 将垃圾扔到指定收集点。
    """)

# 底部
st.markdown("---")
st.caption("Designed for Hiroshima Residents | Data: 2025 Edition")
