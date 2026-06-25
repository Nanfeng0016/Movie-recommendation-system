import os

dirs = [
    "backend",
    "frontend/src/router",
    "frontend/src/api",
    "frontend/src/views",
    "frontend/src/components",
    "frontend/public",
]
for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"Created: {d}")
