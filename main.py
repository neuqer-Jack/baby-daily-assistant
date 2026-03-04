import os
import requests
from datetime import date, datetime


PUSHPLUS_TOKEN = os.environ["PUSHPLUS_TOKEN"]
DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
BABY_BIRTHDAY = os.environ["BABY_BIRTHDAY"]


def get_baby_age():
    birthday = datetime.strptime(BABY_BIRTHDAY, "%Y-%m-%d").date()
    today = date.today()
    months = (today.year - birthday.year) * 12 + (today.month - birthday.month)
    days = (today - birthday).days
    return months, days


def generate_content(months, days):
    prompt = f"""你是专业育儿顾问。孩子今天 {months} 个月大。

生成今日育儿日报：

# 育儿日报 · {months}个月

## ⚡ 今日3个要点
每条3句话，简洁实用。

## 📖 今日深度（1篇，200字）
针对{months}个月龄，选一个重要主题深入讲解，附实操建议。

语气温暖专业，内容具体可操作。"""

    response = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def send_to_wechat(title, content):
    response = requests.post(
        "https://www.pushplus.plus/send",
        json={
            "token": PUSHPLUS_TOKEN,
            "title": title,
            "content": content,
            "template": "markdown",
            "topic": "zizai young",
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    if result.get("code") != 200:
        raise Exception(f"PushPlus error: {result}")
    print("✅ 推送成功！")


def main():
    months, days = get_baby_age()
    print(f"孩子今天 {months} 个月大")

    print("正在生成今日育儿内容...")
    content = generate_content(months, days)

    years = months // 12
    remaining_months = months % 12
    title = f"育儿日报 · 宝宝{years}岁{remaining_months}个月"
    send_to_wechat(title, content)


if __name__ == "__main__":
    main()
