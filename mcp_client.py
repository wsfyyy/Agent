# import websockets
# import json
# import asyncio
# message = {
#     # "type": "list_tools"
#     "type": "call_tool",
#     "tool": "get_weather",
#     "arguments":{"area":"肇庆", "time":"12月2日"},
#     "call_id": 123
#
# }
#
# async def main():
#     websocket = await websockets.connect("ws://127.0.0.1:8000")
#     await websocket.send(json.dumps(message))
#
#     response = await websocket.recv()
#     print(json.loads(response))
#
#     await websocket.close()
#
# asyncio.run(main())


import asyncio
import json

from typing import Dict, List
import websockets


class ServerConnection:
    """单个 Server 的连接管理"""

    def __init__(self, name: str, uri: str):
        self.name = name
        self.uri = uri
        self.websocket = None
        self.tools: List[Dict] = []
        self.connected = False

    async def connect(self):
        """连接 Server"""
        try:
            self.websocket = await websockets.connect(self.uri,ping_interval=20,ping_timeout=None)
            self.connected = True
            print(f"[Client] 已连接到 Server: {self.name}")

            # 获取工具列表
            await self.websocket.send(json.dumps({"type": "tools_list"}))
            response = await self.websocket.recv()
            data = json.loads(response)
            # print(data)

            if data.get("type") == "tools_list":
                self.tools = data.get("tools", [])
                print(f"[Client] Server '{self.name}' 提供工具: {[t['function']['name'] for t in self.tools]}")

        except Exception as e:
            print(f"[Client] 连接 Server '{self.name}' 失败: {e}")
            self.connected = False


    async def get_tool_list(self):
        return self.tools


    async def call_tool(self, tool_name: str, arguments: Dict, id: str) -> Dict:
        """调用指定工具"""
        if not self.connected:
            return {"status": "error", "error": "Server 未连接"}

        message = {
            "type": "call_tool",
            "tool": tool_name,
            "arguments": arguments,
            "call_id": id
        }

        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        response = json.loads(response)
        return response

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.connected = False

# async def main(tool_name, arguments, name="mcp", uri="ws://localhost:8000"):
#     connection = ServerConnection(name=name, uri=uri)
#     await connection.connect()
#     response = await connection.call_tool(tool_name=tool_name, arguments=arguments)
#     await connection.disconnect()
#     return response
#
# async def main1():
#     connection = ServerConnection(name="mcp", uri="ws://localhost:8000")
#     await connection.connect()
#     response = await connection.call_tool(tool_name="save_file", arguments={"path":"123", "text":"123", "postfix":".py"})
#     await connection.disconnect()
#     return response
#
#
# if __name__ == "__main__":
#     res = asyncio.run(main(tool_name="save_file", arguments={"path":"123", "text":"123", "postfix":".py"}))
#
#     # res = asyncio.run(main1())
#
#     print(res)








