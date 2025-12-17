import streamlit as st
import pandas as pd
import json
import datetime
import calendar

# --- 页面基本设置 ---
st.set_page_config(
    page_title="广岛南区垃圾分类助手",
    page_icon="🗑️",
    layout="centered", # 手机端显示更友好
    initial_sidebar_state="collapsed"
)

# 自定义 CSS 优化手机端体验
st.markdown("""
    <style>
    .stAlert { padding: 0.5rem; }
    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.4rem; }
    h3 { font-size: 1.1rem; }
    .garbage-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #00cc66;
    }
    .big-font { font-size: 1.2rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 核心逻辑函数 ---

@st.cache_data
def load_data():
    """加载 JSON 数据"""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("找不到 data.json 文件，请检查项目目录。")
        return {"schedule_rules": {}, "dictionary": []}

def get_week_of_month(date):
    """计算日期是当月的第几个星期几 (例如：第2个周三)"""
    day = date.day
    # 简单的数学计算：(日 - 1) // 7 + 1
    return (day - 1) // 7 + 1

def get_garbage_for_date(target_date, rules):
    """根据日期和规则返回垃圾类型"""
    weekday_name = target_date.strftime("%A") # e.g., "Monday"
    rule = rules.get(weekday_name, [])
    
    # 1. 如果是空列表，直接返回空
    if not rule:
        return []
    
    # 2. 如果是列表，说明是固定规则（如周一可燃）
    if isinstance(rule, list):
        return rule
    
    # 3. 如果是字典，说明有特殊逻辑
    if isinstance(rule, dict):
        week_num = get_week_of_month(target_date)
        
        # 处理周三的“奇偶周”交替逻辑
        if rule.get("type") == "alternating":
            if week_num in [1, 3, 5]:
                return rule.get("odd_weeks", [])
            else:
                return rule.get("even_weeks", [])
        
        # 处理周四的“每月第2周不燃”逻辑
        if rule.get("type") == "monthly_rule":
            special = rule.get("special", {})
            if special.get("condition") == "2nd_week" and week_num == 2:
                return special.get("item", [])
            else:
                return rule.get("default", [])
                
    return []

def get_relative_day_text(target_date, today):
    """返回人性化的日期描述"""
    delta = (target_date - today).days
    if delta == 0: return "今天"
    if delta == 1: return "明天"
    if delta == 2: return "后天"
    return target_date.strftime("%m/%d")

# --- 主程序 ---

data = load_data()
schedule_rules = data.get("schedule_rules", {})

st.title("🗑️ 广岛南区垃圾助手")
st.caption("适用地区：段原、皆实町等 (南区5区分)")

# 1. 获取时间
now = datetime.datetime.now()
today = now.date()
# 为了演示效果，如果现在是晚上8点后，直接显示明天的提醒
display_date = today + datetime.timedelta(days=1) if now.hour >= 20 else today
tomorrow = today + datetime.timedelta(days=1)

# --- 模块一：智能提醒 ---
st.header("📢 垃圾投放提醒")

# 计算未来3天的垃圾
upcoming = []
for i in range(3): # 今天、明天、后天
    d = today + datetime.timedelta(days=i)
    g_list = get_garbage_for_date(d, schedule_rules)
    if g_list:
        upcoming.append((d, g_list))

if upcoming:
    # 只显示最近的一个投放日
    target_d, target_g = upcoming[0]
    day_text = get_relative_day_text(target_d, today)
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][target_d.weekday()]
    
    st.info(f"**{day_text} ({weekday_cn}) 请扔：**")
    
    for g in target_g:
        st.markdown(f"""
        <div class="garbage-card">
            <div class="big-font">{g}</div>
        </div>
        """, unsafe_allow_html=True)
        
    if day_text == "今天":
        st.warning("⚠️ 请在早上 8:30 前扔出！")
else:
    st.success("最近三天没有垃圾收集，休息一下吧！☕")

# --- 模块二：分类查询 ---
st.markdown("---")
st.header("🔍 怎么扔？")
search_query = st.text_input("输入物品名称 (支持中文/日语)", placeholder="例如：电池、鸡蛋、pizza...")

if search_query:
    df = pd.DataFrame(data["dictionary"])
    # 模糊搜索 (中日文皆可)
    result = df[df['item'].str.contains(search_query, case=False, na=False)]
    
    if not result.empty:
        for _, row in result.iterrows():
            with st.container():
                st.markdown(f"**{row['item']}**")
                st.markdown(f"分类：:red[**{row['type']}**]")
                if row['note']:
                    st.caption(f"💡 注意：{row['note']}")
                st.divider()
    else:
        st.write("🤔 没找到这个物品。")
        st.markdown("""
        **常见归类参考：**
        * 软塑料包装 → **可回收塑料**
        * 硬塑料玩具/用品 → **其他塑料**
        * 脏了洗不掉的 → **可燃垃圾**
        """)

# --- 模块三：本周日历概览 ---
with st.expander("查看本周完整日程"):
    week_schedule = []
    for i in range(7):
        d = today + datetime.timedelta(days=i)
        g = get_garbage_for_date(d, schedule_rules)
        d_str = d.strftime("%m/%d")
        w_str = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()]
        
        # 格式化输出
        content = " / ".join(g) if g else "无收集"
        week_schedule.append(f"**{d_str} ({w_str})**: {content}")
    
    st.markdown("\n\n".join(week_schedule))

st.markdown("---")
st.caption("数据来源：广岛市环境局 (2025年度版)")