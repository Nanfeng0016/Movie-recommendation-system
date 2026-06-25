# 删除辅助脚本
import os
script = "create_dirs.py"
if os.path.exists(script):
    os.remove(script)
    print(f"已删除 {script}")
else:
    print(f"{script} 不存在")
