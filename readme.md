🗑️ 广岛南区垃圾分类助手 (Hiroshima Garbage Helper)

这是一个基于 Python 和 Streamlit 开发的网页应用，专为居住在 广岛市南区（段原、皆实町等地区） 的居民设计。它可以帮助您快速查询“明天扔什么垃圾”，以及如何正确分类生活垃圾。

🔗 在线访问: 点击这里访问应用 (部署后替换为您的实际链接)

✨ 功能特点

智能提醒：自动判断当前日期，告诉您今天、明天该扔什么垃圾（考虑了“第1、3个周三”等复杂规则）。

分类查询：支持中日文模糊搜索（例如搜“电池”、“フライパン”），快速获取分类建议。

日程概览：一键查看本周七天的完整垃圾收集安排。

移动端友好：界面专为手机优化，方便早晨出门前查看。

📂 数据来源

本项目的数据基于广岛市环境局发布的 2025年度（令和7年） 官方文档：

日历规则：基于 mi05n.pdf (南区5区分：段原、皆实町等)。

分类指南：基于 20250310.pdf (广岛市家庭垃圾分类指南)。

🛠️ 本地运行指南

如果您想在自己的电脑上运行此项目：

克隆仓库

git clone [https://github.com/您的用户名/hiroshima-garbage-helper.git](https://github.com/您的用户名/hiroshima-garbage-helper.git)
cd hiroshima-garbage-helper


安装依赖
建议使用 Python 3.8+。

pip install -r requirements.txt


启动应用

streamlit run app.py


☁️ 部署方法 (Streamlit Community Cloud)

本项目可直接免费部署到 Streamlit Community Cloud：

将此仓库 Fork 到您的 GitHub。

访问 share.streamlit.io 并登录。

点击 New app。

选择您的仓库、分支（main），并将 Main file path 设置为 app.py。

点击 Deploy 即可！

📄 文件结构

app.py: 应用程序的主逻辑代码。

data.json: 核心数据库，包含收集日历规则和垃圾分类字典。

requirements.txt: Python 依赖库列表。

Disclaimer: 本应用仅供参考，具体收集规则若有临时变动（如年末年始），请以广岛市官方通知为准。
