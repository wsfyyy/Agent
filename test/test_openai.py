from openai import OpenAI


client = OpenAI(base_url="http://127.0.0.1:8080", api_key="123")
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_w",
            "description": "获取天气信息",
            "parameters": {
                "city":{
                    "type": "string",
                     "description": "城市名字"
                },
                "time":{
                    "type": "string",
                    "description" : "日期"
                },
                "required":["city"]
            },
        }
    }
]


response = client.chat.completions.create(
    model="qwen3-8b",
    messages=
    [{"role" : "system", "content" : ""},
     {"role": "user", "content": "乌鲁木土的天气如何?"}],
    tools=tools,
)
# print(response.choices[0].message.reasoning_content)
# print(response.choices[0].message.content)
respons = response.choices[0].message
print(respons)
# print(response.choices[0].message.model_dump_json(indent=2))
