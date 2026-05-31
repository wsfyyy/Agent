import asyncio
from dataclasses import dataclass
import json
from typing import Dict, Any, Callable, Optional
import websockets

from mcp_meta_tools import get_registered_tools


@dataclass
class ToolSchema:
    """工具元数据"""
    name: str
    description: str
    parameters: Dict[str, Any]

    def to_dict(self):
        return {
            "type":"function",
            "function":{
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

class MCPServer:
    """mcp server基类"""
    def __init__(self, name:str, host:str = "localhost", port:int = 8000):
        self.name = name
        self.host = host
        self.port = port
        self.tools:Dict[str,Callable] = {}
        self.tool_schema:Dict[str, ToolSchema] = {}

    def auto_register_tools(self):
        """获取mcp_tools注册的_TOOLS_REGISTRY"""
        registered = get_registered_tools()
        for tool_name, tool_info in registered.items():
            self.register_tool(
                name=tool_info["name"],
                description=tool_info["description"],
                func=tool_info["function"],
                parameters=tool_info["parameters"]
            )


    def register_tool(self,
                      name:str,
                      description:str,
                      func:Callable,
                      parameters:Optional[Dict] = None):
        self.tools[name] = func

        # if parameters is None:
        #     param_schema = self._generate_schema_from_func(func)

        self.tool_schema[name] = ToolSchema(
            name=name,
            description=description,
            parameters=parameters,
        )
        print(f"[Server:{self.name}] 注册工具:{name}")
        #检查tool注册信息
        # print ( inspect.getsource(func))
        # print(self.tool_schema[name].to_dict())


    # def _generate_schema_from_func(self, func:Callable) ->Dict:
    #     """自动生成json Schema"""
    #     sig = inspect.signature(func)
    #     properties = {}
    #     required = []
    #     for param_name, param in sig.parameters.items():
    #         param_type = "string"
    #
    #         if param.annotation != inspect.Parameter.empty:
    #             if param.annotation == int:
    #                 param_type = "integer"
    #             elif param.annotation == float:
    #                 param_type = "number"
    #             elif param.annotation == bool:
    #                 param_type = "boolean"
    #             elif param.annotation == list:
    #                 param_type = "array"
    #             elif param.annotation == dict:
    #                 param_type = "object"
    #         properties[param_name] = {
    #             "type": param_type,
    #             "description":f"参数: {param_name}"
    #         }
    #
    #         if param.default == inspect.Parameter.empty:
    #             required.append(param_name)
    #
    #     return {"type":"object",
    #             "properties":properties,
    #             "required":required,}

    async def handle_message(self, websocket, message:str):
        """处理Client来的信息"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            if msg_type == "tools_list":
                #返回工具列表
                tools = [schema.to_dict() for schema in self.tool_schema.values()]
                response = {
                    "type": "tools_list",
                    "server": self.name,
                    "tools": tools,
                }
                await websocket.send(json.dumps(response))

            elif msg_type == "call_tool":
                #执行工具
                tool_name = data.get("tool")
                arguments = data.get("arguments", {})
                call_id = data.get("call_id")

                if tool_name not in self.tools:
                    response = {
                        "type" : "tool_result",
                        "call_id" : call_id,
                        "status" : "error",
                        "error" : f"工具 {tool_name} 不存在"
                    }
                else:
                    try:
                        #执行工具函数
                        result = await self._execute_tool(tool_name, arguments)
                        response = {
                            "type" : "tool_result",
                            "call_id" : call_id,
                            "status" : "success",
                            "result" : result
                        }
                    except Exception as e:
                        response = {
                            "type": "tool_result",
                            "call_id": call_id,
                            "status": "error",
                            "result": str(e)
                        }

                await websocket.send(json.dumps(response))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                "type": "error",
                "error": "无效的 JSON 格式"
            }))

    async def _execute_tool(self, tool_name: str, arguments: Dict):
        """执行工具"""
        func = self.tools[tool_name]

        if asyncio.iscoroutinefunction(func):
            result = await func(**arguments)
            return  str(result)
        else:
            loop = asyncio.get_event_loop()
            result =  loop.run_in_executor(None, lambda:func(**arguments))
            return  str(result)

    async def start(self):
        """启动 WebSocket服务"""
        async def handler(websocket):
            print(f"[Server:{self.name}] Client 已连接")

            try:
                async for message in websocket:
                    await self.handle_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                print(f"[Server{self.name}] Client 断开连接")
        server = await websockets.serve(handler, self.host, self.port,ping_interval=20,ping_timeout=None)
        print(f"[Server:{self.name}] 启动于 ws://{self.host}:{self.port}")
        await server.wait_closed()


###手写工具方法
# async def add(num1:int, num2:int):
#     return num1 + num2



#主入口
import tools
async def main():

    mcpserver = MCPServer("mcp")
    mcpserver.auto_register_tools()  #自动注册

    #手动注册
    # mcpsersver.register_tool(name="add", description="加法计算器", func=add,
    #                             param_schema={
    #                                 "num1":{"type":int, "description":"一个加数"},
    #                                 "num2":{"type":int, "description":"另一个加数"}
    #                             }
    #                          )

    await mcpserver.start()



if __name__ == "__main__":

    asyncio.run(main())


