"""DeepSeek 多轮聊天练习。

安装：python -m pip install -r ai-demo/requirements.txt
运行：python ai-demo/deepseek_chat.py --temperature 0.2
流式：python ai-demo/deepseek_chat.py --temperature 1.2 --stream
输入 Q 或 q 退出；history 只保存在本次运行的内存中。
"""

import argparse
import os

from openai import APIError, OpenAI
from dotenv import load_dotenv
load_dotenv()



def parse_args():
    parser = argparse.ArgumentParser(description="DeepSeek 多轮聊天（Q/q 退出）")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="0 到 2，较低通常更稳定，较高通常更多样（默认 0.7）")
    parser.add_argument("--stream", action="store_true", help="逐段打印回复")
    args = parser.parse_args()
    if not 0 <= args.temperature <= 2:
        parser.error("--temperature 必须在 0 到 2 之间")
    return args


def print_usage(usage):
    """每次调用分别统计；输入 token 包含本轮发送的历史对话。"""
    if usage is None:
        print("本次用量：API 未返回 token 统计，无法确认。")
        return
    print(
        f"本次用量：输入 {usage.prompt_tokens} tokens，"
        f"输出 {usage.completion_tokens} tokens，"
        f"合计 {usage.total_tokens} tokens"
    )


def chat_once(client, messages, temperature, stream):
    """发送完整历史，返回完整回复；兼容两种流式用量分块格式。"""
    options = {
        "model": "deepseek-flash",
        "messages": messages,
        "temperature": temperature,
        "stream": stream,
        # DeepSeek 的 temperature 仅在非思考模式下生效。
        "extra_body": {"thinking": {"type": "disabled"}},
    }
    if stream:
        options["stream_options"] = {"include_usage": True}

    response = client.chat.completions.create(**options)
    print("AI：", end="", flush=True)

    if not stream:
        answer = response.choices[0].message.content or ""
        print(answer)
        print_usage(response.usage)
        return answer

    parts = []
    usage = None
    try:
        for chunk in response:
            # 用量可能随最后一个内容块返回，也可能在 choices=[] 的块中。
            if chunk.usage is not None:
                usage = chunk.usage
            if chunk.choices:
                content = chunk.choices[0].delta.content or ""
                parts.append(content)
                print(content, end="", flush=True)
    finally:
        response.close()
        print()
        # 流中断时也打印状态，不把未知用量当成 0。
        print_usage(usage)
    return "".join(parts)


def main():
    args = parse_args()
    try:
        api_key = os.environ["DEEPSEEK_API_KEY"]
    except KeyError:
        print("请先设置环境变量 DEEPSEEK_API_KEY，再运行脚本。")
        return 1
    if not api_key.strip():
        print("环境变量 DEEPSEEK_API_KEY 不能为空。")
        return 1

    # 同一个 messages 列表保存 system、user 和 assistant 的历史消息。
    messages = [{"role": "system", "content": "你是一个有帮助的助手，请用中文回答。"}]
    with OpenAI(api_key=api_key, base_url="https://api.deepseek.com",
                timeout=60.0, max_retries=0) as client:
        print(f"temperature={args.temperature}, stream={args.stream}；输入 Q/q 退出。")
        while True:
            try:
                question = input("你：").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n对话结束。")
                break
            if question.lower() == "q":
                break
            if not question:
                continue

            messages.append({"role": "user", "content": question})
            try:
                answer = chat_once(client, messages, args.temperature, args.stream)
            except APIError:
                # 不打印原始异常，避免服务端错误信息意外包含敏感内容。
                messages.pop()
                print("请求失败，请检查网络、密钥、账户额度或参数后重试。")
                continue
            except KeyboardInterrupt:
                print("\n本轮已中断，对话结束。")
                break
            messages.append({"role": "assistant", "content": answer})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
