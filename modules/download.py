import os
import requests

def download_upstream_rules():
    os.makedirs('./local', exist_ok=True)
    if not os.path.exists('./input/urls.conf'):
        print("请创建 ./input/urls.conf 配置文件")
        return
    with open('./input/urls.conf', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            name, url = line.split(':', 1)
            try:
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                path = f'./local/{name}.txt'
                with open(path, 'w', encoding='utf-8') as fw:
                    fw.write(r.text)
                print(f"[download] {name} 下载完成")
            except Exception as e:
                print(f"[download] {name} 下载失败: {e}")
