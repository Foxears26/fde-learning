"""DeepSeek 天气 agent：python ai-demo/weather_agent.py，输入 Q/q 退出。"""

import json
import os

import requests
from dotenv import load_dotenv
from openai import APIError, OpenAI

# 必须先加载 .env，再读取 DEEPSEEK_API_KEY。
load_dotenv()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询一个城市的当前天气和温度，不提供未来天气预报。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如 Toronto、北京。",
                    }
                },
                "required": ["city"],
                "additionalProperties": False,
            },
        },
    }
]


def get_weather(city):
    """沿用 W3 weathercheck/weather.py 的 geocoding → forecast 流程。"""
    if not isinstance(city, str) or not city.strip():
        return {"error": "city 必须是非空字符串。"}
    city = city.strip()
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "zh"},
            timeout=10,
        )
        response.raise_for_status()
        locations = response.json().get("results")
        if not locations:
            return {"error": f"找不到城市：{city}，请补充或更换城市名。"}

        location = locations[0]
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,weather_code",
                "timezone": "auto",
            },
            timeout=10,
        )
        response.raise_for_status()
        weather = response.json()
        current = weather["current"]
        return {
            "city": location["name"],
            "region": location.get("admin1", ""),
            "country": location.get("country", ""),
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "time": current["time"],
            "timezone": weather["timezone"],
            "temperature": current["temperature_2m"],
            "temperature_unit": weather["current_units"]["temperature_2m"],
            "weather_code": current["weather_code"],
            "source": "Open-Meteo",
        }
    except requests.RequestException:
        return {"error": "天气服务请求失败，请稍后重试。"}
    except (KeyError, ValueError, TypeError, IndexError):
        return {"error": "天气服务返回的数据不完整或格式有误。"}


def execute_tool(tool_call):
    """只执行允许的工具，并检查模型生成的 JSON 参数。"""
    if tool_call.function.name != "get_weather":
        return {"error": f"不支持的工具：{tool_call.function.name}"}
    try:
        arguments = json.loads(tool_call.function.arguments)
    except (ValueError, TypeError):
        return {"error": "工具参数不是有效的 JSON。"}
    if not isinstance(arguments, dict) or set(arguments) != {"city"}:
        return {"error": "get_weather 只接受必填参数 city。"}
    return get_weather(arguments["city"])


def chat_once(client, messages):
    """完成一轮：模型选择工具 → 执行工具 → 模型生成最终回答。"""
    # 本轮成功后才保存历史，避免请求失败留下未配对的工具消息。
    pending = list(messages)
    options = {
        "model": "deepseek-flash",
        "tools": TOOLS,
        "extra_body": {"thinking": {"type": "disabled"}},
    }
    response = client.chat.completions.create(messages=pending, **options)
    message = response.choices[0].message
    pending.append(message.model_dump(exclude_none=True))

    if message.tool_calls:
        for tool_call in message.tool_calls:
            result = execute_tool(tool_call)
            pending.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # 工具结果已齐全；第二次只生成回答，避免再次请求工具。
        response = client.chat.completions.create(
            messages=pending, tool_choice="none", **options
        )
        message = response.choices[0].message
        pending.append(message.model_dump(exclude_none=True))

    messages[:] = pending
    return message.content or "（模型未返回文字回答）"


def main():
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("请在 .env 或环境变量中设置 DEEPSEEK_API_KEY。")
        return 1

    messages = [{
        "role": "system",
        "content": (
            "你是天气助手，请用中文回答。查询当前天气时使用 get_weather，"
            "缺少城市时先询问用户。只根据工具返回的数据报告天气，"
            "说明匹配到的城市、观测时间和温度单位。"
            "工具失败时如实说明，不编造天气；工具仅支持当前天气。"
        ),
    }]
    with OpenAI(
        api_key=api_key, base_url="https://api.deepseek.com",
        timeout=60.0, max_retries=0,
    ) as client:
        print("天气助手已启动，输入 Q/q 退出。")
        while True:
            try:
                question = input("你：").strip()
                if question.lower() == "q":
                    break
                if not question:
                    continue
                messages.append({"role": "user", "content": question})
                try:
                    answer = chat_once(client, messages)
                except APIError:
                    messages.pop()
                    print("请求失败，请检查网络、密钥、账户额度或参数后重试。")
                    continue
                print(f"AI：{answer}")
            except (EOFError, KeyboardInterrupt):
                print("\n对话结束。")
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
