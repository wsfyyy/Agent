from openai import OpenAI
from mcp_client import ServerConnection
import asyncio
import json

def check_point(messages):
    # print(f"check_point：{messages}")
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


async def main():


    mcp_client = ServerConnection("mcp",uri="ws://127.0.0.1:8000")
    client = OpenAI(base_url="http://127.0.0.1:8080", api_key="123")

    await mcp_client.connect()
    #获取tool列表
    tool_list = await mcp_client.get_tool_list()


    messages = [{"role": "system", "content": r"你是一个助手,你可以调用工具获取信息,可以使用文件夹'D:\Project\Python\langchain\ai_dir',回答用户的问题/no_think"}]

    num_round = 0
    while True:
        question = input("user:")
        if question == "end":
            break
        messages.append({"role": "user", "content": question})



        while True:
            response = client.chat.completions.create(
                model="qwen3-8b",
                messages= messages,
                tools=tool_list,
            )


            assistant_message = response.choices[0].message
            print(assistant_message)
            if assistant_message.content:
                messages.append({"role": "assistant",
                                 "content": assistant_message.content,})
                                # "reasoning_content": assistant_message.reasoning_content



            if assistant_message.tool_calls:
                tool_name = assistant_message.tool_calls[0].function.name
                tool_args = json.loads(assistant_message.tool_calls[0].function.arguments)
                tool_id = assistant_message.tool_calls[0].id

                #call_tool的信息添加到measages
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                #工具调用
                print(f"[使用工具 {tool_name}]")
                result =  await mcp_client.call_tool(tool_name, tool_args, tool_id)
                #将工具调用的结果，转化成openai的格式(必须包含role,content)
                result["role"] = "tool"
                result["content"] = result.pop("result")
                result["tool_call_id"] = result.pop("call_id")
                messages.append(result)

                continue
            break
        check_point(messages)
        print(f"assistant:{response.choices[0].message.content}")
        num_round += 1
    await mcp_client.disconnect()
    print(f"num_round:{num_round}")

asyncio.run(main())
