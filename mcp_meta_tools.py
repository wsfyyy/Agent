import re
import inspect
_TOOLS_REGISTRY = {}

def tool(name:str=None, description:str=None):
    """
    工具装饰器
    用法:
        @tool(name="add", description="加法计算器")
        async def add(num1: int, num2: int):
        ""
        加法计算器
        :num1: 一个加速
        :num2:另一个加数:
        ""
            return num1 + num2
    """
    def decorator(func):
        parameters = {}
        required = []
        tool_name = name or func.__name__
        tool_description = description


        sig = inspect.signature(func)

        #添加param_type和默认des
        for param_name, param in sig.parameters.items():
            param_type = "string"

            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
                elif param.annotation == dict:
                    param_type = "object"
            # parameters[param_name]["type"] = param_type
            parameters[param_name] = {"type": param_type,
                                      "description": f"参数:{param_name}"}

            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        parameters["required"] = required

        # 获取def注释修改tool_description、param、param_description

        doc = func.__doc__
        lines = doc.strip().split('\n')
        for line_id in range(len(lines) - 1):
            if line_id == 0:
                tool_description = tool_description or lines[line_id]
                continue
            name_and_des = lines[line_id].strip()[7:].split(":")
            # print(name_and_des)
            parameters[name_and_des[0]]["description"] = name_and_des[1]



        _TOOLS_REGISTRY[tool_name] = {
            "name": tool_name,
            "description": tool_description,
            "parameters": parameters,
            "function": func

        }
        return func
    return decorator

def get_registered_tools():
    """获取所有已注册的工具"""
    return _TOOLS_REGISTRY.copy()


# def clear_registry():
#     """清空注册表（测试用）"""
#     _TOOLS_REGISTRY.clear()
