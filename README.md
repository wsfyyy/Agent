gpu：RTX4060 laptop


编译原始模型文件:
python llama.cpp\convert_hf_to_gguf.py . --outfile qwen3-8b-f16.gguf --outtype f16  (解压llama.zip后使用)
量化：
python  llama-b9221-bin-win-cuda-12.4-x64\llama-quantize.exe qwen3-8b-f16.gguf qwen3-8b-q4_k_m.gguf Q4_K_M
启动模型服务:
llama-b9221-bin-win-cuda-12.4-x64\llama-server.exe -m D:\Project\Python\langchain\Qwen3-8B\qwen3-8b-q4_k_m.gguf  -ngl 33 --host 127.0.0.1 --port 8080

启动mcp_server:
python mcp_server.py

启动host:
python host.py

tool.py可以自行添加方法，但方法注释需要按照固定格式。

ai_dir目录：ai存储文件的地方，可以修改host.py的提示词改变



