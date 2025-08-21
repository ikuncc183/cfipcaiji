import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Selenium WebDriver 配置 ---
# 在GitHub Actions环境中，浏览器和驱动由workflow文件安装
# Selenium会自动在系统路径中找到驱动，所以不需要Service对象
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不打开浏览器界面
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'")

# 初始化WebDriver
# 在配置好的CI环境中，这样写就足够了
driver = webdriver.Chrome(options=chrome_options)

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 使用集合存储IP地址实现自动去重
unique_ips = set()

for url in urls:
    try:
        # Selenium 打开网页
        driver.get(url)
        
        # --- 关键步骤 ---
        # 等待10秒，让页面上的JavaScript有足够的时间加载和渲染真实数据
        print(f'正在访问 {url}，等待10秒让数据加载...')
        time.sleep(10)
        
        # 获取加载完成后的网页源代码
        html_content = driver.page_source
        
        # 使用正则表达式查找IP地址
        ip_matches = re.findall(ip_pattern, html_content, re.IGNORECASE)
        
        # 将找到的IP添加到集合中（自动去重）
        unique_ips.update(ip_matches)
        print(f'在 {url} 找到 {len(ip_matches)} 个IP地址。')

    except Exception as e:
        print(f'处理 {url} 时发生错误: {e}')
        continue

# 关闭浏览器
driver.quit()

# 将去重后的IP地址按数字顺序排序后写入文件
if unique_ips:
    # 按IP地址的数字顺序排序（非字符串顺序）
    sorted_ips = sorted(unique_ips, key=lambda ip: [int(part) for part in ip.split('.')])
    
    with open('ip.txt', 'w') as file:
        for ip in sorted_ips:
            file.write(ip + '\n')
    print(f'任务完成！已保存 {len(sorted_ips)} 个唯一IP地址到 ip.txt 文件。')
else:
    print('未找到有效的IP地址。')
