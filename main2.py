import sys
import os
import time
import base64
import json
import re
import random
import requests
import urllib.request
from datetime import datetime
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QPoint, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QPlainTextEdit, QPushButton, QFileDialog,
    QGroupBox, QFormLayout, QSplitter, QCheckBox, QSpinBox, QTabWidget,
    QListWidget, QListWidgetItem, QInputDialog, QMenu, QDialog, QTextEdit,
    QMessageBox, QScrollArea, QFrame, QStackedWidget, QGridLayout
)
from PySide6.QtGui import QPixmap, QAction, QIcon, QPalette, QColor

# ==========================================
# 0. 路径与配置初始化
# ==========================================
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
TEMPLATES_FILE = os.path.join(BASE_DIR, "templates.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
IMAGE_OUT_DIR = os.path.join(BASE_DIR, "output", "images")
LOG_DIR = os.path.join(BASE_DIR, "output", "logs")

DEFAULT_MODELS = ["gpt-image-2", "gpt-image-2-pro", "flux-dev"]
DEFAULT_QUALITIES = ["low", "medium", "high"]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==========================================
# 1. 语言系统
# ==========================================
LANG = {
    "zh": {
        "title": "AI 桌面图像生成器",
        "tab_generate": "生成图像",
        "tab_history": "历史记录",
        "tab_templates": "Prompt 模板",
        "api_group": "API 连接信息（双路径）",
        "image_path": "Image 路径:",
        "chat_path": "Chat 路径:",
        "api_token": "API Token:",
        "model_group": "模型名称",
        "model_label": "选择/输入模型:",
        "prompt_group": "Prompt 提示词",
        "prompt_placeholder": "在此处输入或粘贴提示词...",
        "btn_translate": "翻译为英文",
        "size_group": "分辨率规格",
        "size_label": "分辨率规格:",
        "size_auto": "auto（自动）",
        "size_square": "1024x1024（方形）",
        "size_landscape": "1536x1024（横向）",
        "size_portrait": "1024x1536（纵向）",
        "size_2k_square": "2048x2048（2K 方形）",
        "size_2k_landscape": "2048x1152（2K 横向）",
        "size_2k_portrait": "1152x2048（2K 纵向）",
        "size_4k_landscape": "3840x2160（4K 横向）",
        "size_4k_portrait": "2160x3840（4K 纵向）",
        "quality_label": "生成质量:",
        "retry_group": "重试设置",
        "retry_enable": "启用自动重试",
        "retry_count": "重试次数:",
        "cmd_group": "生产命令台",
        "btn_select_ref": "选择参考图片",
        "btn_generate": "生成图像",
        "mode_txt2img": "[文生图]",
        "mode_img2img": "[图生图]",
        "status_ready": "状态: 待机",
        "status_blocked": "状态: 被拦截",
        "status_done": "完成",
        "status_error": "错误",
        "elapsed": "已耗时: {} 秒",
        "result_title": "生成画面结果",
        "result_waiting": "等待生成...",
        "ref_title": "参考原图（可选）",
        "ref_none": "未选择参考图（将使用文生图模式）",
        "empty_prompt": "提示词输入框为空，请输入有效词。",
        "empty_token": "API Token 为空，请配置有效的 Token。",
        "sending": "正在发送请求... (尝试 {}/{})",
        "wait_retry": "等待 2 秒后重试... ({}/{})",
        "retry_failed": "所有重试均失败",
        "ref_missing": "错误: 参考图文件丢失",
        "http_error": "接口报错 ({})",
        "net_error": "网络故障",
        "exception": "异常",
        "extract_error": "接口未能成功提取到图片",
        "processing": "正在处理生成的图片...",
        "btn_save_template": "保存当前为模板",
        "btn_delete_template": "删除选中模板",
        "btn_load_template": "加载模板",
        "btn_clear_history": "清空历史",
        "btn_theme": "切换暗色主题",
        "btn_lang": "EN/中",
        "image_count": "生成数量:",
        "history_empty": "暂无历史记录",
        "template_name": "请输入模板名称:",
        "confirm_clear": "确认清空所有历史记录？",
        "history_prompt": "Prompt",
        "history_model": "模型",
        "history_time": "时间",
        "history_status": "状态",
        "history_success": "成功",
        "history_failed": "失败",
        "history_image": "图片",
        "reuse_prompt": "复用 Prompt",
        "template_title": "保存模板",
        "confirm_title": "确认",
        "select_ref_title": "选择参考图片",
        "image_files": "图片文件 (*.png *.jpg *.jpeg *.webp)",
        "tab_prompt_adv": "Prompt 高级设置",
        "prompt_preview_group": "Prompt 预览栏（双向对比）",
        "prompt_original_label": "原文 (Original Prompt):",
        "prompt_original_placeholder": "在此处输入提示词，或切换至生成选项卡同步输入...",
        "prompt_optimized_label": "优化/翻译后的 Prompt (Optimized/Translated Prompt):",
        "prompt_optimized_placeholder": "点击下方的“AI 翻译”或“AI 优化”获取结果...",
        "btn_adv_translate": "AI 翻译为英文",
        "btn_adv_optimize": "AI 优化 Prompt",
        "btn_adv_apply": "应用到主提示词",
        "adv_status_translating": "状态: 正在通过 AI 翻译...",
        "adv_status_optimizing": "状态: 正在通过 AI 优化...",
        "proxy_label": "代理设置:",
        "proxy_placeholder": "例如: http://127.0.0.1:7890 (留空为系统默认)",
        "image_token": "Image 令牌:",
        "chat_token": "Chat 令牌:",
    },
    "en": {
        "title": "AI Desktop Image Generator",
        "tab_generate": "Generate",
        "tab_history": "History",
        "tab_templates": "Prompt Templates",
        "api_group": "API Connection (Dual Path)",
        "image_path": "Image Path:",
        "chat_path": "Chat Path:",
        "api_token": "API Token:",
        "model_group": "Model",
        "model_label": "Select/Enter Model:",
        "prompt_group": "Prompt",
        "prompt_placeholder": "Enter or paste your prompt here...",
        "btn_translate": "Translate to English",
        "size_group": "Resolution",
        "size_label": "Resolution:",
        "size_auto": "auto (Auto)",
        "size_square": "1024x1024 (Square)",
        "size_landscape": "1536x1024 (Landscape)",
        "size_portrait": "1024x1536 (Portrait)",
        "size_2k_square": "2048x2048 (2K Square)",
        "size_2k_landscape": "2048x1152 (2K Landscape)",
        "size_2k_portrait": "1152x2048 (2K Portrait)",
        "size_4k_landscape": "3840x2160 (4K Landscape)",
        "size_4k_portrait": "2160x3840 (4K Portrait)",
        "quality_label": "Quality:",
        "retry_group": "Retry Settings",
        "retry_enable": "Enable Auto Retry",
        "retry_count": "Retry Count:",
        "cmd_group": "Command",
        "btn_select_ref": "Select Reference Image",
        "btn_generate": "Generate",
        "mode_txt2img": "[Text to Image]",
        "mode_img2img": "[Image to Image]",
        "status_ready": "Status: Ready",
        "status_blocked": "Status: Blocked",
        "status_done": "Done",
        "status_error": "Error",
        "elapsed": "Elapsed: {} sec",
        "result_title": "Generated Image",
        "result_waiting": "Waiting...",
        "ref_title": "Reference Image (Optional)",
        "ref_none": "No reference selected (Text to Image mode)",
        "empty_prompt": "Prompt is empty.",
        "empty_token": "API Token is empty.",
        "sending": "Sending request... (attempt {}/{})",
        "wait_retry": "Waiting 2s to retry... ({}/{})",
        "retry_failed": "All retries failed",
        "ref_missing": "Error: Reference image file missing",
        "http_error": "API Error ({})",
        "net_error": "Network Error",
        "exception": "Exception",
        "extract_error": "Failed to extract image from response",
        "processing": "Processing image...",
        "btn_save_template": "Save as Template",
        "btn_delete_template": "Delete Template",
        "btn_load_template": "Load Template",
        "btn_clear_history": "Clear History",
        "btn_theme": "Toggle Dark Theme",
        "btn_lang": "中/EN",
        "image_count": "Count:",
        "history_empty": "No history yet",
        "template_name": "Enter template name:",
        "confirm_clear": "Clear all history?",
        "history_prompt": "Prompt",
        "history_model": "Model",
        "history_time": "Time",
        "history_status": "Status",
        "history_success": "OK",
        "history_failed": "Fail",
        "history_image": "Image",
        "reuse_prompt": "Reuse Prompt",
        "template_title": "Save Template",
        "confirm_title": "Confirm",
        "select_ref_title": "Select Reference Image",
        "image_files": "Images (*.png *.jpg *.jpeg *.webp)",
        "tab_prompt_adv": "Prompt Advanced",
        "prompt_preview_group": "Prompt Preview (Comparison)",
        "prompt_original_label": "Original Prompt:",
        "prompt_original_placeholder": "Enter prompt here, or switch to Generate tab...",
        "prompt_optimized_label": "Optimized/Translated Prompt:",
        "prompt_optimized_placeholder": "Click 'AI Translate' or 'AI Optimize' below to get results...",
        "btn_adv_translate": "AI Translate",
        "btn_adv_optimize": "AI Optimize Prompt",
        "btn_adv_apply": "Apply to Main Prompt",
        "adv_status_translating": "Status: Translating via AI...",
        "adv_status_optimizing": "Status: Optimizing via AI...",
        "proxy_label": "Proxy:",
        "proxy_placeholder": "e.g., http://127.0.0.1:7890 (leave empty for system default)",
        "image_token": "Image Token:",
        "chat_token": "Chat Token:",
    }
}

# 中文 -> 英文常用词翻译字典
TRANSLATE_DICT = {
    "女孩": "girl", "男孩": "boy", "猫": "cat", "狗": "dog", "花": "flower",
    "山": "mountain", "海": "sea", "天空": "sky", "太阳": "sun", "月亮": "moon",
    "星星": "star", "树": "tree", "森林": "forest", "河": "river", "湖": "lake",
    "城市": "city", "房子": "house", "汽车": "car", "飞机": "airplane", "船": "boat",
    "鸟": "bird", "鱼": "fish", "龙": "dragon", "机器人": "robot", "魔法": "magic",
    "城堡": "castle", "战士": "warrior", "公主": "princess", "王子": "prince",
    "天使": "angel", "恶魔": "demon", "剑": "sword", "盾牌": "shield",
    "火焰": "fire", "冰": "ice", "闪电": "lightning", "风": "wind",
    "雨": "rain", "雪": "snow", "云": "cloud", "彩虹": "rainbow",
    "夜晚": "night", "白天": "day", "日出": "sunrise", "日落": "sunset",
    "春天": "spring", "夏天": "summer", "秋天": "autumn", "冬天": "winter",
    "美丽的": "beautiful", "可爱的": "cute", "恐怖的": "scary", "神秘的": "mysterious",
    "科幻": "sci-fi", "奇幻": "fantasy", "写实": "realistic", "动漫": "anime",
    "水彩": "watercolor", "油画": "oil painting", "素描": "sketch",
    "高清": "high quality", "细节": "detailed", "光影": "lighting",
    "背景": "background", "前景": "foreground", "特写": "close-up",
    "全景": "panorama", "侧面": "side view", "正面": "front view",
    "背影": "back view", "俯视": "top view", "仰视": "bottom view",
    "微笑": "smile", "哭泣": "crying", "奔跑": "running", "飞翔": "flying",
    "坐着": "sitting", "站着": "standing", "跳舞": "dancing", "战斗": "fighting",
    "拿着": "holding", "看着": "looking at", "穿着": "wearing",
    "红色": "red", "蓝色": "blue", "绿色": "green", "黄色": "yellow",
    "紫色": "purple", "粉色": "pink", "黑色": "black", "白色": "white",
    "金色": "gold", "银色": "silver", "橙色": "orange", "灰色": "gray",
    "古风": "Chinese ancient style", "赛博朋克": "cyberpunk", "蒸汽朋克": "steampunk",
    "废土": "post-apocalyptic", "未来": "futuristic", "复古": "retro",
    "极简": "minimalist", "华丽": "gorgeous", "黑暗": "dark", "明亮": "bright",
    "柔和": "soft", "鲜艳": "vibrant", "暗淡": "dim", "温暖": "warm",
    "寒冷": "cold", "梦幻": "dreamy", "超现实": "surreal", "抽象": "abstract",
    "像素": "pixel art", "3D渲染": "3D render", "概念艺术": "concept art",
    "插画": "illustration", "海报": "poster", "壁纸": "wallpaper",
    "肖像": "portrait", "风景": "landscape", "静物": "still life",
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_json_file(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default if default is not None else []
    return default if default is not None else []


def save_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


config_data = load_config()
config_data.setdefault("IMAGE_API_URL", "https://api.openai.com/v1/images/generations")
config_data.setdefault("CHAT_API_URL", "https://api.openai.com/v1/chat/completions")
config_data.setdefault("DEFAULT_API_TOKEN", "")
config_data.setdefault("IMAGE_API_TOKEN", config_data.get("DEFAULT_API_TOKEN", ""))
config_data.setdefault("CHAT_API_TOKEN", config_data.get("DEFAULT_API_TOKEN", ""))
config_data.setdefault("PROXY_URL", "")
config_data.setdefault("API_PROFILES", [{
    "name": "默认配置 (Default)",
    "image_url": config_data.get("IMAGE_API_URL", ""),
    "chat_url": config_data.get("CHAT_API_URL", ""),
    "image_token": config_data.get("IMAGE_API_TOKEN", ""),
    "chat_token": config_data.get("CHAT_API_TOKEN", ""),
    "token": config_data.get("DEFAULT_API_TOKEN", "")
}])

# Clean up deprecated models from history
if "MODEL_HISTORY" in config_data:
    config_data["MODEL_HISTORY"] = [m for m in config_data["MODEL_HISTORY"] if m not in ["gpt-image-1", "gpt-image-1.5"]]
    for dm in DEFAULT_MODELS:
        if dm not in config_data["MODEL_HISTORY"]:
            config_data["MODEL_HISTORY"].append(dm)

config_data.setdefault("MODEL_HISTORY", DEFAULT_MODELS.copy())
if config_data.get("LAST_USED_MODEL") in ["gpt-image-1", "gpt-image-1.5"]:
    config_data["LAST_USED_MODEL"] = config_data["MODEL_HISTORY"][0]
config_data.setdefault("LAST_USED_MODEL", config_data["MODEL_HISTORY"][0])
config_data.setdefault("DEFAULT_QUALITY", "low")
config_data.setdefault("AUTO_RETRY", False)
config_data.setdefault("RETRY_COUNT", 3)
config_data.setdefault("LANGUAGE", "zh")
config_data.setdefault("DARK_THEME", False)

templates_data = load_json_file(TEMPLATES_FILE, [])
history_data = load_json_file(HISTORY_FILE, [])

os.makedirs(IMAGE_OUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


def t(key):
    lang = config_data.get("LANGUAGE", "zh")
    return LANG.get(lang, LANG["zh"]).get(key, key)


def translate_prompt(text):
    result = text
    for zh, en in sorted(TRANSLATE_DICT.items(), key=lambda x: -len(x[0])):
        result = result.replace(zh, en)
    return result


# ==========================================
# 2. 网络请求线程（带重试机制）
# ==========================================
class ImageGenerateThread(QThread):
    success = Signal(list, str, str, dict)
    error = Signal(str, str, dict)
    status = Signal(str)

    def __init__(self, mode, api_url, image_api_url, chat_api_url, token, model, prompt, size, quality, ref_image_paths=None, auto_retry=False, retry_count=3, proxy_url=None, n=1):
        super().__init__()
        self.mode = mode
        self.api_url = api_url
        self.image_api_url = image_api_url
        self.chat_api_url = chat_api_url
        self.token = token
        self.model = model
        self.prompt = prompt
        self.size = size
        self.quality = quality
        self.ref_image_paths = ref_image_paths or []
        self.auto_retry = auto_retry
        self.retry_count = retry_count
        self.proxy_url = proxy_url
        self.n = n

    def determine_api_url(self):
        if self.mode == "image":
            return self.chat_api_url
        return self.image_api_url

    def run(self):
        api_url = self.determine_api_url()
        attempt = 0
        max_attempts = self.retry_count if self.auto_retry else 1
        start_time_run = time.time()

        while attempt < max_attempts:
            attempt += 1
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            log_file_path = os.path.join(LOG_DIR, f"log_{timestamp}_{random_suffix}_attempt{attempt}.json")
            api_size = re.split(r'[(（]', self.size)[0].strip()

            url_lower = api_url.lower()
            response = None

            self.status.emit(t("sending").format(attempt, max_attempts))

            if "images/generations" in url_lower:
                payload = {
                    "model": self.model,
                    "prompt": self.prompt,
                    "size": api_size,
                    "quality": self.quality,
                    "n": self.n
                }
                if self.mode == "image" and self.ref_image_paths:
                    # Pass the first image for backward compatibility with standard DALL-E endpoints
                    first_path = self.ref_image_paths[0]
                    if os.path.exists(first_path):
                        with open(first_path, "rb") as f:
                            b64_first = base64.b64encode(f.read()).decode('utf-8')
                        payload["image"] = f"data:image/jpeg;base64,{b64_first}"
                        payload["image_url"] = f"data:image/jpeg;base64,{b64_first}"
                    
                    # Pass all images as a list for advanced custom endpoints
                    b64_list = []
                    for path in self.ref_image_paths:
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                b64 = base64.b64encode(f.read()).decode('utf-8')
                            b64_list.append(f"data:image/jpeg;base64,{b64}")
                    payload["images"] = b64_list
            else:
                messages = []
                if self.mode == "text":
                    messages.append({"role": "user", "content": f"Generate an image. Prompt: {self.prompt}"})
                else:
                    if not self.ref_image_paths:
                        self.error.emit(t("ref_missing"), "")
                        return
                    
                    # Package multiple images into user messages
                    content_list = [{"type": "text", "text": f"Modify these images. Prompt: {self.prompt}"}]
                    for path in self.ref_image_paths:
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                b64 = base64.b64encode(f.read()).decode('utf-8')
                            content_list.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                            })
                    messages.append({"role": "user", "content": content_list})
                payload = {"model": self.model, "messages": messages, "size": api_size, "n": self.n}
                
            log_data = {"timestamp": timestamp, "attempt": attempt, "request_url": api_url, "payload": payload}

            try:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                session = requests.Session()
                if self.proxy_url:
                    session.proxies = {
                        "http": self.proxy_url,
                        "https": self.proxy_url
                    }
                else:
                    sys_proxies = urllib.request.getproxies()
                    if sys_proxies:
                        session.proxies.update(sys_proxies)

                from requests.adapters import HTTPAdapter
                session.mount("http://", HTTPAdapter(max_retries=0))
                session.mount("https://", HTTPAdapter(max_retries=0))

                response = session.post(api_url, json=payload, headers=headers, timeout=(15, 300))
                log_data["response_status"] = response.status_code
                response.raise_for_status()
                res_data = response.json()
                log_data["response_body"] = res_data

                extracted_images = []
                
                # Case 1: Images API response ('data' field)
                if 'data' in res_data:
                    for data_item in res_data['data']:
                        url = data_item.get('url')
                        b64 = data_item.get('b64_json')
                        if url or b64:
                            extracted_images.append((url, b64))
                            
                # Case 2: Chat API response ('choices' field)
                if not extracted_images and 'choices' in res_data:
                    for choice in res_data['choices']:
                        content = choice.get('message', {}).get('content', '')
                        if not content:
                            continue
                            
                        # 1. Safely extract URLs from content by splitting words first (avoids ReDoS on huge strings)
                        words = content.split()
                        for word in words:
                            # Clean surrounding quotes/brackets from markdown urls
                            clean_word = word.strip('()[]{}""\'\'<>*')
                            if clean_word.startswith(("http://", "https://")):
                                if any(ext in clean_word.lower() for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]):
                                    extracted_images.append((clean_word, None))
                                    
                        # 2. Extract Base64 encoded images from content (efficiently via string operations)
                        if "data:image" in content and "base64" in content:
                            start_idx = content.find("data:image")
                            while start_idx != -1:
                                comma_idx = content.find(",", start_idx)
                                if comma_idx != -1:
                                    end_idx = comma_idx + 1
                                    while end_idx < len(content) and content[end_idx] not in (' ', ')', ']', '"', '\'', '>', '\n', '\r'):
                                        end_idx += 1
                                    b64_str = content[comma_idx+1:end_idx].strip()
                                    if len(b64_str) > 100:
                                        extracted_images.append((None, b64_str))
                                    start_idx = content.find("data:image", end_idx)
                                else:
                                    break
                        elif len(content) > 1000 and not content.strip().startswith("http"):
                            # Check if the entire content itself is a raw base64 string
                            cleaned_content = re.sub(r'\s+', '', content)
                            if "," in cleaned_content:
                                cleaned_content = cleaned_content.split(",", 1)[1]
                            try:
                                # Try decoding first 100 bytes to check if it's a valid image
                                decoded = base64.b64decode(cleaned_content[:100])
                                if decoded[:8] == b'\x89PNG\r\n\x1a\n' or decoded[:2] == b'\xff\xd8' or (decoded[:4] == b'RIFF' and decoded[8:12] == b'WEBP'):
                                    extracted_images.append((None, cleaned_content))
                            except:
                                pass

                if not extracted_images:
                    raise Exception(f"{t('extract_error')}: {json.dumps(res_data, ensure_ascii=False)}")

                self.status.emit(t("processing"))

                save_paths = []
                for idx, (img_url, img_base64) in enumerate(extracted_images):
                    if img_base64:
                        img_bytes = base64.b64decode(img_base64)
                        if img_bytes[:8] == b'\x89PNG\r\n\x1a\n': ext = 'png'
                        elif img_bytes[:2] == b'\xff\xd8': ext = 'jpg'
                        elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP': ext = 'webp'
                        else: ext = 'png'
                        filename = f"gen_{timestamp}_{random_suffix}_{idx}.{ext}"
                        save_path = os.path.join(IMAGE_OUT_DIR, filename)
                        with open(save_path, "wb") as f:
                            f.write(img_bytes)
                        save_paths.append(save_path)
                    else:
                        img_response = session.get(img_url, timeout=(10, 60))
                        img_response.raise_for_status()
                        ct = img_response.headers.get('content-type', '')
                        if 'jpeg' in ct or 'jpg' in ct: ext = 'jpg'
                        elif 'png' in ct: ext = 'png'
                        elif 'webp' in ct: ext = 'webp'
                        else: ext = 'png'
                        filename = f"gen_{timestamp}_{random_suffix}_{idx}.{ext}"
                        save_path = os.path.join(IMAGE_OUT_DIR, filename)
                        with open(save_path, "wb") as f:
                            f.write(img_response.content)
                        save_paths.append(save_path)

                duration = time.time() - start_time_run
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0
                if 'usage' in res_data:
                    usage = res_data['usage']
                    prompt_tokens = usage.get('prompt_tokens', 0)
                    completion_tokens = usage.get('completion_tokens', 0)
                    total_tokens = usage.get('total_tokens', 0)

                metadata = {
                    "api_url": api_url,
                    "duration": f"{duration:.2f}s",
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens
                }

                self.success.emit(save_paths, self.prompt, self.model, metadata)
                self.status.emit(t("status_done"))
                return
            except requests.exceptions.HTTPError as http_err:
                if response is not None:
                    log_data["response_status"] = response.status_code
                    try:
                        log_data["response_body"] = response.json()
                    except:
                        log_data["response_body"] = response.text
                else:
                    log_data["error"] = str(http_err)
                duration = time.time() - start_time_run
                metadata = {
                    "api_url": api_url or "",
                    "duration": f"{duration:.2f}s",
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
                try:
                    err_detail = response.json() if response else str(http_err)
                    self.error.emit(f"{t('http_error').format(response.status_code)}:\n{json.dumps(err_detail, ensure_ascii=False, indent=2)}", self.prompt, metadata)
                except:
                    self.error.emit(f"{t('net_error')}:\n{str(http_err)}", self.prompt, metadata)
                self.status.emit(f"{t('status_error')} ({attempt}/{max_attempts})")
            except Exception as e:
                log_data["error"] = str(e)
                duration = time.time() - start_time_run
                metadata = {
                    "api_url": api_url or "",
                    "duration": f"{duration:.2f}s",
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
                self.error.emit(f"{t('exception')}:\n{str(e)}", self.prompt, metadata)
                self.status.emit(f"{t('status_error')} ({attempt}/{max_attempts})")
            finally:
                try:
                    with open(log_file_path, "w", encoding="utf-8") as lf:
                        json.dump(log_data, lf, ensure_ascii=False, indent=2)
                except:
                    pass

            if attempt < max_attempts:
                self.status.emit(t("wait_retry").format(attempt, max_attempts))
                time.sleep(2)

        self.status.emit(t("retry_failed"))


# ==========================================
# 2.5 Prompt 处理线程 (翻译/优化)
# ==========================================
class PromptProcessThread(QThread):
    success = Signal(str)
    error = Signal(str)
    status = Signal(str)

    def __init__(self, api_url, token, model, prompt, task_type, proxy_url=None):
        super().__init__()
        self.api_url = api_url
        self.token = token
        self.model = model
        self.prompt = prompt
        self.task_type = task_type
        self.proxy_url = proxy_url

    def run(self):
        self.status.emit("Connecting to AI...")
        if self.task_type == "translate":
            system_prompt = (
                "You are a professional translator. Translate the user's input text "
                "into a clean, descriptive English prompt suitable for AI image generation. "
                "Output ONLY the translated English text. Do not include any explanations, "
                "markdown formatting, quotes, or conversational filler."
            )
        else:
            system_prompt = (
                "You are an expert AI prompt engineer. Enhance and optimize the user's input text "
                "into a detailed, vivid, and highly effective English prompt for AI image generation. "
                "Add details about style, lighting, composition, and quality to make it visually stunning "
                "while preserving the original core concept. Output ONLY the optimized English prompt. "
                "Do not include any explanations, markdown formatting, quotes, or conversational filler."
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.prompt}
            ]
        }

        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            session = requests.Session()
            if self.proxy_url:
                session.proxies = {
                    "http": self.proxy_url,
                    "https": self.proxy_url
                }
            else:
                sys_proxies = urllib.request.getproxies()
                if sys_proxies:
                    session.proxies.update(sys_proxies)
            from requests.adapters import HTTPAdapter
            session.mount("http://", HTTPAdapter(max_retries=0))
            session.mount("https://", HTTPAdapter(max_retries=0))

            response = session.post(self.api_url, json=payload, headers=headers, timeout=(10, 60))
            response.raise_for_status()
            res_data = response.json()

            if 'choices' in res_data and len(res_data['choices']) > 0:
                result = res_data['choices'][0]['message']['content'].strip()
                if result.startswith("```"):
                    lines = result.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].startswith("```"):
                        lines = lines[:-1]
                    result = "\n".join(lines).strip()
                if (result.startswith('"') and result.endswith('"')) or (result.startswith("'") and result.endswith("'")):
                    result = result[1:-1].strip()
                
                self.success.emit(result)
                self.status.emit("Success")
            else:
                raise Exception("No choices returned from the chat completion API.")
        except Exception as e:
            self.error.emit(str(e))
            self.status.emit("Error")


class ModelFetchThread(QThread):
    success = Signal(list)
    error = Signal(str)

    def __init__(self, api_url, token, proxy_url=None):
        super().__init__()
        self.api_url = api_url
        self.token = token
        self.proxy_url = proxy_url

    def run(self):
        try:
            url = self.api_url
            if url.endswith("/chat/completions"):
                url = url.replace("/chat/completions", "/models")
            elif url.endswith("/chat/completions/"):
                url = url.replace("/chat/completions/", "/models")
            elif url.endswith("/images/generations"):
                url = url.replace("/images/generations", "/models")
            elif url.endswith("/images/generations/"):
                url = url.replace("/images/generations/", "/models")
            else:
                url = url.rstrip("/") + "/models"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            session = requests.Session()
            if self.proxy_url:
                session.proxies = {
                    "http": self.proxy_url,
                    "https": self.proxy_url
                }
            else:
                sys_proxies = urllib.request.getproxies()
                if sys_proxies:
                    session.proxies.update(sys_proxies)

            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            res_data = response.json()

            model_list = []
            if 'data' in res_data:
                for item in res_data['data']:
                    if 'id' in item:
                        model_list.append(item['id'])
            
            model_list.sort()
            self.success.emit(model_list)
        except Exception as e:
            self.error.emit(str(e))


class HistoryItemWidget(QWidget):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.entry = entry
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Thumbnail
        self.lbl_thumb = QLabel()
        self.lbl_thumb.setFixedSize(80, 80)
        self.lbl_thumb.setAlignment(Qt.AlignCenter)
        
        image_path = entry.get("image", "")
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.lbl_thumb.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_thumb.setStyleSheet("border: 1px solid rgba(128,128,128,60); border-radius: 4px;")
        else:
            self.lbl_thumb.setText("已删除\n(Deleted)" if image_path else "无图片\n(No Image)")
            self.lbl_thumb.setStyleSheet("border: 1px solid rgba(128,128,128,60); border-radius: 4px; background-color: rgba(0,0,0,40); font-size: 10px; color: gray; font-weight: bold; text-align: center;")
            
        layout.addWidget(self.lbl_thumb)
        
        # Details layout
        details_layout = QVBoxLayout()
        details_layout.setSpacing(2)
        
        # Row 1: Time & Model
        row1_layout = QHBoxLayout()
        time_str = entry.get("time", "")
        lbl_time = QLabel(f"[{time_str}]")
        lbl_time.setStyleSheet("font-weight: bold; font-size: 11px;")
        
        model_str = entry.get("model", "")
        lbl_model = QLabel(model_str)
        lbl_model.setStyleSheet("font-size: 10px; background-color: rgba(128,128,128,40); padding: 1px 4px; border-radius: 3px;")
        
        row1_layout.addWidget(lbl_time)
        row1_layout.addWidget(lbl_model)
        row1_layout.addStretch()
        details_layout.addLayout(row1_layout)
        
        # Row 2: Status & Time & Tokens
        row2_layout = QHBoxLayout()
        status_raw = entry.get("status", "")
        status_text = "成功" if status_raw == "success" else "失败"
        status_color = "green" if status_raw == "success" else "red"
        
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"color: {status_color}; font-weight: bold; font-size: 11px;")
        row2_layout.addWidget(lbl_status)
        
        if status_raw == "success":
            duration = entry.get("duration", "")
            total_tokens = entry.get("total_tokens", 0)
            lbl_meta = QLabel(f"| 用时: {duration} | Token: {total_tokens}")
            lbl_meta.setStyleSheet("font-size: 10px; color: gray;")
            row2_layout.addWidget(lbl_meta)
            
        row2_layout.addStretch()
        details_layout.addLayout(row2_layout)
        
        # Row 3: Prompt preview
        prompt_preview = entry.get("prompt", "")[:70]
        if len(entry.get("prompt", "")) > 70:
            prompt_preview += "..."
        lbl_prompt = QLabel(f"Prompt: {prompt_preview}")
        lbl_prompt.setStyleSheet("font-size: 11px; color: #555;" if not config_data.get("DARK_THEME", False) else "font-size: 11px; color: #bbb;")
        lbl_prompt.setWordWrap(True)
        details_layout.addWidget(lbl_prompt)
        
        # Row 4: API URL snippet
        api_url = entry.get("api_url", "")
        if api_url:
            if len(api_url) > 60:
                api_url = api_url[:35] + "..." + api_url[-20:]
            lbl_api = QLabel(f"API: {api_url}")
            lbl_api.setStyleSheet("font-size: 9px; color: gray;")
            details_layout.addWidget(lbl_api)
            
        layout.addLayout(details_layout, stretch=1)


class HistoryDetailDialog(QDialog):
    def __init__(self, entry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setWindowTitle("历史记录详情")
        self.resize(750, 600)
        
        # Style
        if config_data.get("DARK_THEME", False):
            self.setStyleSheet("""
                QDialog { background-color: #1e1428; color: #f0e6ff; }
                QLabel { color: #f0e6ff; }
                QTextEdit { background-color: #140a1e; color: #f0e6ff; border: 1px solid #a064f0; border-radius: 6px; }
                QPushButton { background-color: #3c2d5a; color: #f0e6ff; border: 1px solid #a064f0; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #503c78; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f0f8ff; color: #003b59; }
                QLabel { color: #003b59; }
                QTextEdit { background-color: #ffffff; color: #004d40; border: 1px solid #003b59; border-radius: 6px; }
                QPushButton { background-color: #e0f0ff; color: #006064; border: 1px solid #003b59; border-radius: 6px; padding: 6px 12px; font-weight: bold; }
                QPushButton:hover { background-color: #cce6ff; }
            """)
            
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Horizontal layout for image and details
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        
        # Image preview
        self.lbl_image = QLabel()
        self.lbl_image.setFixedSize(300, 300)
        self.lbl_image.setAlignment(Qt.AlignCenter)
        
        image_paths = entry.get("images", [])
        if not image_paths and entry.get("image"):
            image_paths = [entry.get("image")]
            
        primary_image = image_paths[0] if image_paths else ""
        self.set_detail_image(primary_image)
        
        left_panel = QVBoxLayout()
        left_panel.addWidget(self.lbl_image)
        
        if len(image_paths) > 1:
            thumbs_widget = QWidget()
            thumbs_layout = QHBoxLayout(thumbs_widget)
            thumbs_layout.setContentsMargins(0, 0, 0, 0)
            thumbs_layout.setSpacing(5)
            thumbs_layout.setAlignment(Qt.AlignCenter)
            
            for path in image_paths:
                if os.path.exists(path):
                    lbl_t = QLabel()
                    lbl_t.setFixedSize(45, 45)
                    pix = QPixmap(path)
                    lbl_t.setPixmap(pix.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    lbl_t.setStyleSheet("border: 1px solid rgba(128,128,128,80); border-radius: 3px;")
                    lbl_t.setCursor(Qt.PointingHandCursor)
                    lbl_t.mousePressEvent = lambda event, p=path: self.set_detail_image(p)
                    thumbs_layout.addWidget(lbl_t)
            left_panel.addWidget(thumbs_widget)
            
        top_layout.addLayout(left_panel)
        
        # Details grid
        details_widget = QWidget()
        details_layout = QFormLayout(details_widget)
        details_layout.setSpacing(8)
        
        # Read metadata
        time_val = entry.get("time", "")
        status_val = entry.get("status", "")
        status_text = "成功 (Success)" if status_val == "success" else "失败 (Failed)"
        status_color = "green" if status_val == "success" else "red"
        
        model_val = entry.get("model", "")
        api_url = entry.get("api_url", "未知 (Unknown)")
        duration = entry.get("duration", "未知 (Unknown)")
        prompt_tokens = entry.get("prompt_tokens", 0)
        completion_tokens = entry.get("completion_tokens", 0)
        total_tokens = entry.get("total_tokens", 0)
        
        # Labels
        lbl_time = QLabel(time_val)
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        lbl_model = QLabel(model_val)
        lbl_api = QLabel(api_url)
        lbl_api.setWordWrap(True)
        lbl_duration = QLabel(duration)
        lbl_tokens = QLabel(f"输入: {prompt_tokens} | 输出: {completion_tokens} | 总计: {total_tokens}")
        
        details_layout.addRow("生成时间:", lbl_time)
        details_layout.addRow("生成状态:", lbl_status)
        details_layout.addRow("使用模型:", lbl_model)
        details_layout.addRow("API 端口:", lbl_api)
        details_layout.addRow("生成总用时:", lbl_duration)
        details_layout.addRow("Token 详情:", lbl_tokens)
        
        top_layout.addWidget(details_widget, stretch=1)
        layout.addLayout(top_layout)
        
        # Prompt text area
        layout.addWidget(QLabel("Prompt 提示词 (Prompt):"))
        self.txt_prompt = QTextEdit()
        self.txt_prompt.setPlainText(entry.get("prompt", ""))
        self.txt_prompt.setReadOnly(True)
        layout.addWidget(self.txt_prompt)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_use = QPushButton("直接使用 Prompt")
        self.btn_copy = QPushButton("复制 Prompt 到剪贴板")
        self.btn_close = QPushButton("关闭")
        
        btn_layout.addWidget(self.btn_use)
        btn_layout.addWidget(self.btn_copy)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        # Connections
        self.btn_use.clicked.connect(self.on_use_clicked)
        self.btn_copy.clicked.connect(self.on_copy_clicked)
        self.btn_close.clicked.connect(self.accept)
        
    def on_use_clicked(self):
        self.parent().txt_prompt.setPlainText(self.entry.get("prompt", ""))
        self.parent().tabs.setCurrentIndex(0)
        self.accept()
        
    def on_copy_clicked(self):
        QApplication.clipboard().setText(self.entry.get("prompt", ""))
        QMessageBox.information(self, "成功", "Prompt 已复制到剪贴板！")

    def set_detail_image(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            self.lbl_image.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_image.setStyleSheet("border: 1px solid rgba(128,128,128,100); border-radius: 6px;")
        else:
            self.lbl_image.setText("图片已从本地磁盘删除\n(Image Deleted)")
            self.lbl_image.setStyleSheet("border: 1px solid rgba(128,128,128,100); border-radius: 6px; background-color: rgba(0,0,0,50); font-weight: bold; text-align: center; color: gray;")


class ThumbnailWidget(QWidget):
    close_clicked = Signal(str)
    clicked = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedSize(110, 132) # 110x110 for image, 20 for name label
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Image container (needed to position close button absolutely)
        self.img_container = QWidget(self)
        self.img_container.setFixedSize(110, 110)
        
        # Thumbnail image label
        self.lbl_img = QLabel(self.img_container)
        pixmap = QPixmap(file_path)
        self.lbl_img.setPixmap(pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.lbl_img.setFixedSize(110, 110)
        self.lbl_img.setAlignment(Qt.AlignCenter)
        self.lbl_img.setStyleSheet("border: 1px solid rgba(255,255,255,100); border-radius: 6px; background: rgba(0,0,0,60);")
        
        # Close button (×) positioned in top-right corner
        self.btn_close = QPushButton("×", self.img_container)
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.move(88, 0) # Top-right corner of 110x110
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 50, 50, 220);
                color: white;
                border: none;
                border-radius: 11px;
                font-weight: bold;
                font-size: 15px;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 20, 20, 255);
            }
        """)
        self.btn_close.hide() # Hidden by default
        self.btn_close.clicked.connect(self.on_close_clicked)
        
        # Text label
        filename = os.path.basename(file_path)
        if len(filename) > 12:
            filename = filename[:10] + ".."
        self.lbl_name = QLabel(filename)
        self.lbl_name.setAlignment(Qt.AlignCenter)
        self.lbl_name.setStyleSheet("font-size: 10px; color: #888;")
        
        layout.addWidget(self.img_container)
        layout.addWidget(self.lbl_name)
        
    def enterEvent(self, event):
        self.btn_close.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.btn_close.hide()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if close button was clicked
            child = self.childAt(event.pos())
            if child != self.btn_close:
                self.clicked.emit(self.file_path)
        super().mousePressEvent(event)
        
    def on_close_clicked(self):
        self.close_clicked.emit(self.file_path)


# ==========================================
# 3. 主界面窗口
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("title"))
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.resize(1300, 850)
        self.ref_image_paths = []
        self.start_time = 0
        self.is_running = False
        self.worker = None

        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_timer_label)
        self.proxy_url_val = config_data.get("PROXY_URL", "")

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        content_layout = QVBoxLayout()
        self.content_layout = content_layout
        content_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.addLayout(content_layout)
        
        central = QWidget()
        self.setCentralWidget(central)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        self.btn_theme = QPushButton(t("btn_theme"))
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.btn_lang = QPushButton(t("btn_lang"))
        self.btn_lang.clicked.connect(self.toggle_language)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_theme)
        toolbar.addWidget(self.btn_lang)
        content_layout.addLayout(toolbar)

        # 主内容区
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧预览区
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.result_group = QGroupBox(t("result_title"))
        result_layout = QVBoxLayout(self.result_group)
        
        self.result_stack = QStackedWidget()
        
        # Index 0: Single Image Label / Text Placeholder (Backward compatible)
        self.lbl_result_img = QLabel(t("result_waiting"))
        self.lbl_result_img.setAlignment(Qt.AlignCenter)
        self.lbl_result_img.setWordWrap(True)
        self.lbl_result_img.setMargin(15)
        self.result_stack.addWidget(self.lbl_result_img)
        
        # Index 1: Grid for Multiple Images
        self.result_grid_widget = QWidget()
        self.result_grid_layout = QGridLayout(self.result_grid_widget)
        self.result_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.result_grid_layout.setSpacing(5)
        self.result_stack.addWidget(self.result_grid_widget)
        
        result_layout.addWidget(self.result_stack)
        left_layout.addWidget(self.result_group, stretch=2)

        self.ref_group = QGroupBox(t("ref_title"))
        ref_layout = QVBoxLayout(self.ref_group)
        
        self.ref_scroll = QScrollArea()
        self.ref_scroll.setWidgetResizable(True)
        self.ref_scroll.setFrameShape(QFrame.NoFrame)
        self.ref_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.ref_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ref_scroll.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ref_scroll.customContextMenuRequested.connect(self.ref_context_menu)
        self.ref_scroll.setStyleSheet("background: transparent; border: none;")
        
        self.ref_container = QWidget()
        self.ref_container.setStyleSheet("background: transparent;")
        self.ref_container_layout = QHBoxLayout(self.ref_container)
        self.ref_container_layout.setContentsMargins(5, 5, 5, 5)
        self.ref_container_layout.setSpacing(10)
        self.ref_container_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.lbl_ref_placeholder = QLabel(t("ref_none"))
        self.lbl_ref_placeholder.setAlignment(Qt.AlignCenter)
        self.ref_container_layout.addWidget(self.lbl_ref_placeholder)
        
        self.ref_scroll.setWidget(self.ref_container)
        ref_layout.addWidget(self.ref_scroll)
        left_layout.addWidget(self.ref_group, stretch=1)

        main_splitter.addWidget(left_widget)

        # 右侧选项卡
        self.tabs = QTabWidget()

        # --- 选项卡1: 生成 ---
        gen_tab = QWidget()
        gen_layout = QVBoxLayout(gen_tab)

        self.api_group = QGroupBox(t("api_group"))
        api_form = QFormLayout(self.api_group)
        
        self.cb_api_profile = QComboBox()
        self.btn_save_profile = QPushButton("保存配置")
        self.btn_delete_profile = QPushButton("删除配置")
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(self.cb_api_profile, stretch=1)
        profile_layout.addWidget(self.btn_save_profile)
        profile_layout.addWidget(self.btn_delete_profile)
        api_form.addRow(QLabel("API 配置预设:"), profile_layout)

        self.txt_image_api_url = QLineEdit()
        self.txt_image_api_token = QLineEdit()
        self.txt_image_api_token.setEchoMode(QLineEdit.Password)
        self.txt_chat_api_url = QLineEdit()
        self.txt_chat_api_token = QLineEdit()
        self.txt_chat_api_token.setEchoMode(QLineEdit.Password)
        self.txt_proxy = QLineEdit()
        self.txt_proxy.setText(self.proxy_url_val)
        self.txt_proxy.setPlaceholderText(t("proxy_placeholder"))
        
        self.lbl_image_path = QLabel(t("image_path"))
        self.lbl_chat_path = QLabel(t("chat_path"))
        self.lbl_image_token = QLabel(t("image_token"))
        self.lbl_chat_token = QLabel(t("chat_token"))
        self.lbl_proxy = QLabel(t("proxy_label"))
        
        api_form.addRow(self.lbl_image_path, self.txt_image_api_url)
        api_form.addRow(self.lbl_image_token, self.txt_image_api_token)
        api_form.addRow(self.lbl_chat_path, self.txt_chat_api_url)
        api_form.addRow(self.lbl_chat_token, self.txt_chat_api_token)
        api_form.addRow(self.lbl_proxy, self.txt_proxy)
        gen_layout.addWidget(self.api_group)
        
        self.update_api_profiles_ui()
        self.cb_api_profile.currentIndexChanged.connect(self.on_api_profile_changed)
        self.btn_save_profile.clicked.connect(self.on_save_api_profile)
        self.btn_delete_profile.clicked.connect(self.on_delete_api_profile)

        self.model_group = QGroupBox(t("model_group"))
        model_form = QFormLayout(self.model_group)
        self.cb_model = QComboBox()
        self.cb_model.setEditable(True)
        self.cb_model.addItems(config_data["MODEL_HISTORY"])
        self.cb_model.setCurrentText(config_data["LAST_USED_MODEL"])
        
        self.btn_fetch_models = QPushButton("🔄")
        self.btn_fetch_models.setToolTip("自动从中转站拉取可用模型")
        self.btn_fetch_models.setFixedWidth(40)
        self.btn_fetch_models.clicked.connect(self.on_fetch_models)
        
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.cb_model, stretch=1)
        model_layout.addWidget(self.btn_fetch_models)
        
        self.lbl_model_label = QLabel(t("model_label"))
        model_form.addRow(self.lbl_model_label, model_layout)
        gen_layout.addWidget(self.model_group)

        self.prompt_group = QGroupBox(t("prompt_group"))
        prompt_layout = QVBoxLayout(self.prompt_group)
        self.txt_prompt = QPlainTextEdit()
        self.txt_prompt.setPlaceholderText(t("prompt_placeholder"))
        prompt_layout.addWidget(self.txt_prompt)
        gen_layout.addWidget(self.prompt_group)

        self.size_group = QGroupBox(t("size_group"))
        size_form = QFormLayout(self.size_group)
        self.cb_size = QComboBox()
        self.cb_size.addItems([
            t("size_auto"),
            t("size_square"),
            t("size_landscape"),
            t("size_portrait"),
            t("size_2k_square"),
            t("size_2k_landscape"),
            t("size_2k_portrait"),
            t("size_4k_landscape"),
            t("size_4k_portrait")
        ])
        
        self.lbl_size_label = QLabel(t("size_label"))
        size_form.addRow(self.lbl_size_label, self.cb_size)
        self.cb_quality = QComboBox()
        self.cb_quality.addItems(DEFAULT_QUALITIES)
        self.cb_quality.setCurrentText(config_data.get("DEFAULT_QUALITY", "low"))
        
        self.lbl_quality_label = QLabel(t("quality_label"))
        size_form.addRow(self.lbl_quality_label, self.cb_quality)
        
        # Image count spinbox
        self.spin_count = QSpinBox()
        self.spin_count.setRange(1, 10)
        self.spin_count.setValue(config_data.get("DEFAULT_IMAGE_COUNT", 1))
        self.lbl_count_label = QLabel(t("image_count"))
        size_form.addRow(self.lbl_count_label, self.spin_count)
        
        gen_layout.addWidget(self.size_group)

        self.retry_group = QGroupBox(t("retry_group"))
        retry_form = QFormLayout(self.retry_group)
        self.chk_auto_retry = QCheckBox(t("retry_enable"))
        self.chk_auto_retry.setChecked(config_data.get("AUTO_RETRY", False))
        retry_form.addRow(self.chk_auto_retry)
        self.spin_retry_count = QSpinBox()
        self.spin_retry_count.setRange(1, 10)
        self.spin_retry_count.setValue(config_data.get("RETRY_COUNT", 3))
        
        self.lbl_retry_count = QLabel(t("retry_count"))
        retry_form.addRow(self.lbl_retry_count, self.spin_retry_count)
        gen_layout.addWidget(self.retry_group)

        self.op_group = QGroupBox(t("cmd_group"))
        op_layout = QVBoxLayout(self.op_group)
        self.btn_select_ref = QPushButton(t("btn_select_ref"))
        self.btn_generate = QPushButton(t("btn_generate"))
        self.btn_generate.setObjectName("btn_generate")
        self.lbl_mode = QLabel(t("mode_txt2img"))
        self.lbl_mode.setStyleSheet("color: gray; font-style: italic;")
        self.lbl_status = QLabel(t("status_ready"))
        self.lbl_status.setStyleSheet("font-weight: bold; color: green;")
        self.lbl_timer = QLabel(t("elapsed").format(0))
        self.lbl_timer.setStyleSheet("color: gray; font-style: italic;")
        op_layout.addWidget(self.btn_select_ref)
        op_layout.addWidget(self.btn_generate)
        op_layout.addWidget(self.lbl_mode)
        op_layout.addWidget(self.lbl_status)
        op_layout.addWidget(self.lbl_timer)
        gen_layout.addWidget(self.op_group)

        self.btn_select_ref.clicked.connect(self.select_reference_image)
        self.btn_generate.clicked.connect(self.execute_generation)

        self.tabs.addTab(gen_tab, t("tab_generate"))

        # --- 选项卡2: Prompt 高级设置 ---
        prompt_adv_tab = QWidget()
        prompt_adv_layout = QVBoxLayout(prompt_adv_tab)

        # Model selection widget in Prompt Advanced Tab
        self.adv_model_group = QGroupBox(t("model_group"))
        adv_model_form = QFormLayout(self.adv_model_group)
        self.cb_adv_model = QComboBox()
        self.cb_adv_model.setEditable(True)
        self.cb_adv_model.addItems(config_data["MODEL_HISTORY"])
        self.cb_adv_model.setCurrentText(config_data["LAST_USED_MODEL"])
        
        self.cb_adv_model.currentTextChanged.connect(self.sync_model_selectors_from_adv)
        self.cb_model.currentTextChanged.connect(self.sync_model_selectors_from_main)

        self.btn_adv_fetch_models = QPushButton("🔄")
        self.btn_adv_fetch_models.setToolTip("自动从中转站拉取可用模型")
        self.btn_adv_fetch_models.setFixedWidth(40)
        self.btn_adv_fetch_models.clicked.connect(self.on_fetch_models)
        
        adv_model_layout = QHBoxLayout()
        adv_model_layout.addWidget(self.cb_adv_model, stretch=1)
        adv_model_layout.addWidget(self.btn_adv_fetch_models)
        
        adv_model_form.addRow(QLabel(t("model_label")), adv_model_layout)
        prompt_adv_layout.addWidget(self.adv_model_group)

        preview_group = QGroupBox(t("prompt_preview_group"))
        preview_layout = QVBoxLayout(preview_group)

        preview_layout.addWidget(QLabel(t("prompt_original_label")))
        self.txt_adv_original = QPlainTextEdit()
        self.txt_adv_original.setPlaceholderText(t("prompt_original_placeholder"))
        preview_layout.addWidget(self.txt_adv_original)

        preview_layout.addWidget(QLabel(t("prompt_optimized_label")))
        self.txt_adv_optimized = QPlainTextEdit()
        self.txt_adv_optimized.setPlaceholderText(t("prompt_optimized_placeholder"))
        preview_layout.addWidget(self.txt_adv_optimized)

        prompt_adv_layout.addWidget(preview_group)

        btn_adv_layout = QHBoxLayout()
        self.btn_adv_translate = QPushButton(t("btn_adv_translate"))
        self.btn_adv_optimize = QPushButton(t("btn_adv_optimize"))
        self.btn_adv_apply = QPushButton(t("btn_adv_apply"))
        
        btn_adv_layout.addWidget(self.btn_adv_translate)
        btn_adv_layout.addWidget(self.btn_adv_optimize)
        btn_adv_layout.addWidget(self.btn_adv_apply)
        prompt_adv_layout.addLayout(btn_adv_layout)

        self.lbl_adv_status = QLabel(t("status_ready"))
        self.lbl_adv_status.setStyleSheet("font-weight: bold; color: green;")
        prompt_adv_layout.addWidget(self.lbl_adv_status)

        self.tabs.addTab(prompt_adv_tab, t("tab_prompt_adv"))

        self.btn_adv_translate.clicked.connect(self.run_ai_translate)
        self.btn_adv_optimize.clicked.connect(self.run_ai_optimize)
        self.btn_adv_apply.clicked.connect(self.apply_adv_prompt)

        # --- 选项卡3: 历史记录 ---
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        self.history_list = QListWidget()
        self.history_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.history_context_menu)
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        history_layout.addWidget(self.history_list)
        self.btn_clear_history = QPushButton(t("btn_clear_history"))
        self.btn_clear_history.clicked.connect(self.clear_history)
        history_layout.addWidget(self.btn_clear_history)
        self.tabs.addTab(history_tab, t("tab_history"))
        self.refresh_history()

        # --- 选项卡4: Prompt 模板 ---
        template_tab = QWidget()
        template_layout = QVBoxLayout(template_tab)
        self.template_list = QListWidget()
        self.refresh_template_list()
        template_layout.addWidget(self.template_list)
        tpl_btn_layout = QHBoxLayout()
        self.btn_save_tpl = QPushButton(t("btn_save_template"))
        self.btn_save_tpl.clicked.connect(self.save_template)
        self.btn_load_tpl = QPushButton(t("btn_load_template"))
        self.btn_load_tpl.clicked.connect(self.load_template)
        self.btn_del_tpl = QPushButton(t("btn_delete_template"))
        self.btn_del_tpl.clicked.connect(self.delete_template)
        tpl_btn_layout.addWidget(self.btn_save_tpl)
        tpl_btn_layout.addWidget(self.btn_load_tpl)
        tpl_btn_layout.addWidget(self.btn_del_tpl)
        template_layout.addLayout(tpl_btn_layout)
        self.tabs.addTab(template_tab, t("tab_templates"))

        main_splitter.addWidget(self.tabs)
        main_splitter.setSizes([500, 800])
        content_layout.addWidget(main_splitter)
        central.setLayout(main_layout)

        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Add a top native menu bar for "Prompt" options
        pass # Removed menu bar


    def set_native_titlebar_color(self, dark: bool):
        try:
            import ctypes
            hwnd = self.winId()
            # DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1 if dark else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                int(hwnd),
                20,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
        except Exception as e:
            print(f"Set dark titlebar failed: {e}")

    # ---- 主题 (Frutiger Aero + Dark Purple-Black Glass) ----
    def apply_theme(self):
        bg_path = resource_path("aero_bg.png").replace("\\", "/")
        app = QApplication.instance()
        if config_data.get("DARK_THEME", False):
            # Force Dark Palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#1e1428"))
            palette.setColor(QPalette.WindowText, QColor("#f0e6ff"))
            palette.setColor(QPalette.Base, QColor("#140a1e"))
            palette.setColor(QPalette.Text, QColor("#f0e6ff"))
            palette.setColor(QPalette.Button, QColor("#281e3c"))
            palette.setColor(QPalette.ButtonText, QColor("#f0e6ff"))
            app.setPalette(palette)
            
            app.setStyleSheet(f"""
                QMainWindow {{
                    border-image: url({bg_path}) 0 0 0 0 stretch stretch;
                }}
                QWidget {{ 
                    color: #f0e6ff; 
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                
                /* Dark Purple-Black Glass Overlay */
                QMainWindow > QWidget {{
                    background-color: rgba(15, 5, 25, 180);
                }}
                
                QGroupBox {{ 
                    border: 1px solid rgba(160, 100, 240, 60); 
                    border-radius: 8px; 
                    margin-top: 15px; 
                    padding-top: 15px; 
                    background-color: rgba(30, 15, 45, 130);
                    color: #d0b0ff; 
                    font-weight: bold;
                }}
                QGroupBox::title {{ 
                    subcontrol-origin: margin; 
                    left: 10px; 
                    padding: 0 5px; 
                    color: #bbaaff; 
                }}
                
                QLineEdit, QComboBox, QPlainTextEdit, QSpinBox, QTextEdit {{ 
                    background-color: rgba(20, 10, 35, 180); 
                    color: #f0e6ff; 
                    border: 1px solid rgba(160, 100, 240, 100); 
                    border-radius: 6px;
                    padding: 5px;
                }}
                
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: 1px solid rgba(160, 100, 240, 100);
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 20), stop:1 rgba(0, 0, 0, 40));
                }}
                
                QComboBox::drop-down:hover {{
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 40), stop:1 rgba(0, 0, 0, 20));
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: rgba(20, 10, 30, 250);
                    color: #f0e6ff;
                    border: 1px solid rgba(160, 100, 240, 120);
                    selection-background-color: rgba(120, 50, 190, 200);
                    selection-color: white;
                }}
                
                QPushButton {{ 
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(110, 45, 180, 200), stop:1 rgba(70, 20, 120, 180));
                    color: #ffffff; 
                    border: 1px solid rgba(160, 100, 240, 150); 
                    padding: 6px 12px; 
                    border-radius: 6px; 
                    font-weight: bold;
                }}
                
                QPushButton:hover {{ 
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(140, 60, 220, 220), stop:1 rgba(90, 30, 150, 200)); 
                }}
                
                QPushButton:pressed {{ 
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(70, 20, 120, 240), stop:1 rgba(110, 45, 180, 200));
                }}
                
                QPushButton:disabled {{ 
                    background-color: rgba(30, 20, 40, 150); 
                    color: #888888; 
                    border: none; 
                }}
                
                QTabWidget::pane {{ 
                    border: 1px solid rgba(160, 100, 240, 80); 
                    background: rgba(30, 15, 45, 120); 
                    border-radius: 8px; 
                }}
                
                QTabBar::tab {{ 
                    background: rgba(20, 10, 30, 160); 
                    color: #c0a0ff; 
                    padding: 8px 16px; 
                    border: 1px solid rgba(160, 100, 240, 80); 
                    border-top-left-radius: 6px; 
                    border-top-right-radius: 6px; 
                    margin-right: 2px; 
                }}
                
                QTabBar::tab:selected {{ 
                    background: rgba(100, 40, 170, 180); 
                    color: #ffffff; 
                    font-weight: bold; 
                    border: 1px solid rgba(160, 100, 240, 150); 
                    border-bottom: none; 
                }}
                
                QListWidget {{ 
                    background-color: rgba(20, 10, 35, 180); 
                    color: #f0e6ff; 
                    border: 1px solid rgba(160, 100, 240, 100); 
                    border-radius: 6px; 
                }}
                
                QListWidget::item:selected {{
                    background-color: rgba(120, 50, 190, 200);
                    color: white;
                }}
                
                QLabel {{ 
                    color: #f0e6ff; 
                }}
                
                QCheckBox {{ 
                    color: #f0e6ff; 
                }}
                
                QSplitter::handle {{ 
                    background-color: rgba(160, 100, 240, 60); 
                }}
                
                QMenu {{ 
                    background-color: rgba(20, 10, 30, 250); 
                    border: 1px solid rgba(160, 100, 240, 120); 
                    color: #f0e6ff; 
                }}
                QDialog, QMessageBox {{
                    background-color: rgb(30, 20, 40);
                    border: 1px solid rgba(160, 100, 240, 120);
                }}
                QMessageBox QLabel {{
                    color: #f0e6ff;
                    background: transparent;
                }}
                QMenu::item {{
                    padding: 6px 20px;
                    background-color: transparent;
                }}
                QMenu::item:selected {{ 
                    background-color: rgba(120, 50, 190, 200); 
                    color: #ffffff;
                }}
                QPushButton#btn_generate {{
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                }}
            """)
            self.set_native_titlebar_color(dark=True)
        else:
            # Force Light Palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#f0f8ff"))
            palette.setColor(QPalette.WindowText, QColor("#003b59"))
            palette.setColor(QPalette.Base, QColor("#ffffff"))
            palette.setColor(QPalette.Text, QColor("#004d40"))
            palette.setColor(QPalette.Button, QColor("#e0f0ff"))
            palette.setColor(QPalette.ButtonText, QColor("#006064"))
            app.setPalette(palette)
            
            app.setStyleSheet(f"""
                QMainWindow {{
                    border-image: url({bg_path}) 0 0 0 0 stretch stretch;
                }}
                QWidget {{ 
                    color: #003b59; 
                    font-family: 'Segoe UI', Arial, sans-serif;
                }}
                QMainWindow > QWidget {{
                    background: transparent;
                }}
                QGroupBox {{ 
                    border: 1px solid rgba(255, 255, 255, 150); 
                    border-radius: 10px; 
                    margin-top: 15px; 
                    padding-top: 15px; 
                    background-color: rgba(255, 255, 255, 100);
                    color: #004d40; 
                    font-weight: bold;
                }}
                QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #006064; }}
                QLineEdit, QComboBox, QPlainTextEdit, QSpinBox, QTextEdit {{ 
                    background-color: rgba(255, 255, 255, 180); 
                    color: #004d40; 
                    border: 1px solid rgba(255, 255, 255, 200); 
                    border-radius: 6px;
                    padding: 4px;
                }}
                QComboBox::drop-down {{
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 25px;
                    border-left: 1px solid rgba(255, 255, 255, 200);
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 220), stop:1 rgba(200, 240, 255, 180));
                }}
                QComboBox::drop-down:hover {{
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(150, 220, 255, 200));
                }}
                QComboBox QAbstractItemView {{
                    background-color: rgba(255, 255, 255, 240);
                    color: #004d40;
                    border: 1px solid rgba(255, 255, 255, 245);
                    selection-background-color: rgba(150, 220, 255, 200);
                    selection-color: #004d40;
                }}
                QPushButton {{ 
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 220), stop:1 rgba(200, 240, 255, 180));
                    color: #006064; 
                    border: 1px solid rgba(255, 255, 255, 255); 
                    padding: 6px 12px; 
                    border-radius: 6px; 
                    font-weight: bold;
                }}
                QPushButton:hover {{ 
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255), stop:1 rgba(150, 220, 255, 200)); 
                }}
                QPushButton:disabled {{ background-color: rgba(200, 200, 200, 100); color: #888; border: none; }}
                QTabWidget::pane {{ border: 1px solid rgba(255, 255, 255, 150); background: rgba(255, 255, 255, 60); border-radius: 8px; }}
                QTabBar::tab {{ background: rgba(255, 255, 255, 120); color: #006064; padding: 8px 16px; border: 1px solid rgba(255, 255, 255, 150); border-top-left-radius: 6px; border-top-right-radius: 6px; }}
                QTabBar::tab:selected {{ background: rgba(255, 255, 255, 220); color: #004d40; font-weight: bold; border-bottom: none; }}
                QListWidget {{ background-color: rgba(255, 255, 255, 150); color: #004d40; border: 1px solid rgba(255, 255, 255, 200); border-radius: 6px; }}
                QLabel {{ color: #003333; font-weight: 500; }}
                QCheckBox {{ color: #003333; font-weight: 500; }}
                QSplitter::handle {{ background-color: rgba(255, 255, 255, 100); }}
                QPushButton#btn_generate {{
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                }}
                QMenu {{
                    background-color: rgba(255, 255, 255, 245);
                    border: 1px solid rgba(150, 200, 220, 150);
                    color: #003b59;
                }}
                QMenu::item {{
                    padding: 6px 20px;
                    background-color: transparent;
                }}
                QMenu::item:selected {{
                    background-color: rgba(150, 220, 255, 200);
                    color: #004d40;
                }}
                QDialog, QMessageBox {{
                    background-color: #f0f8ff;
                    border: 1px solid #003b59;
                }}
                QMessageBox QLabel {{
                    color: #003b59;
                    background: transparent;
                }}
            """)
            self.set_native_titlebar_color(dark=False)

    def update_api_profiles_ui(self):
        self.cb_api_profile.blockSignals(True)
        self.cb_api_profile.clear()
        for p in config_data["API_PROFILES"]:
            self.cb_api_profile.addItem(p["name"])
        idx = config_data.get("CURRENT_PROFILE_INDEX", 0)
        if idx >= len(config_data["API_PROFILES"]):
            idx = 0
        self.cb_api_profile.setCurrentIndex(idx)
        self.cb_api_profile.blockSignals(False)
        self.on_api_profile_changed(idx)

    def on_api_profile_changed(self, idx):
        if idx >= 0 and idx < len(config_data["API_PROFILES"]):
            p = config_data["API_PROFILES"][idx]
            self.txt_image_api_url.setText(p.get("image_url", ""))
            self.txt_chat_api_url.setText(p.get("chat_url", ""))
            self.txt_image_api_token.setText(p.get("image_token", p.get("token", "")))
            self.txt_chat_api_token.setText(p.get("chat_token", p.get("token", "")))
            config_data["CURRENT_PROFILE_INDEX"] = idx

    def on_save_api_profile(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("保存 API 配置")
        dialog.setLabelText("请输入配置名称 (若同名则覆盖):")
        dialog.setTextValue(self.cb_api_profile.currentText())
        dialog.setOkButtonText("OK")
        dialog.setCancelButtonText("Cancel")
        if config_data.get("DARK_THEME", False):
            dialog.setStyleSheet("""
                QInputDialog, QDialog { background-color: #281e3c; }
                QLabel { color: #f0e6ff; }
                QLineEdit { background-color: #140a1e; color: #f0e6ff; border: 1px solid #a064f0; }
                QPushButton { background-color: #3c2d5a; color: #f0e6ff; border: 1px solid #a064f0; }
            """)
        else:
            dialog.setStyleSheet("""
                QInputDialog, QDialog { background-color: #f0f8ff; }
                QLabel { color: #003b59; }
                QLineEdit { background-color: #ffffff; color: #004d40; border: 1px solid #003b59; }
                QPushButton { background-color: #e0f0ff; color: #006064; border: 1px solid #003b59; }
            """)
        ok = dialog.exec()
        name = dialog.textValue()
        if ok and name.strip():
            name = name.strip()
            profiles = config_data["API_PROFILES"]
            existing = next((p for p in profiles if p["name"] == name), None)
            if existing:
                existing["image_url"] = self.txt_image_api_url.text().strip()
                existing["chat_url"] = self.txt_chat_api_url.text().strip()
                existing["image_token"] = self.txt_image_api_token.text().strip()
                existing["chat_token"] = self.txt_chat_api_token.text().strip()
                existing["token"] = self.txt_image_api_token.text().strip()
                config_data["CURRENT_PROFILE_INDEX"] = profiles.index(existing)
            else:
                profiles.append({
                    "name": name,
                    "image_url": self.txt_image_api_url.text().strip(),
                    "chat_url": self.txt_chat_api_url.text().strip(),
                    "image_token": self.txt_image_api_token.text().strip(),
                    "chat_token": self.txt_chat_api_token.text().strip(),
                    "token": self.txt_image_api_token.text().strip()
                })
                config_data["CURRENT_PROFILE_INDEX"] = len(profiles) - 1
            self.update_api_profiles_ui()

    def on_delete_api_profile(self):
        idx = self.cb_api_profile.currentIndex()
        if idx >= 0 and len(config_data["API_PROFILES"]) > 1:
            reply = QMessageBox.question(self, "确认", "确认删除该配置？")
            if reply == QMessageBox.Yes:
                config_data["API_PROFILES"].pop(idx)
                config_data["CURRENT_PROFILE_INDEX"] = 0
                self.update_api_profiles_ui()
    def toggle_theme(self):
        config_data["DARK_THEME"] = not config_data.get("DARK_THEME", False)
        save_config(config_data)
        self.apply_theme()

    # ---- 语言 ----
    def toggle_language(self):
        config_data["LANGUAGE"] = "en" if config_data.get("LANGUAGE", "zh") == "zh" else "zh"
        save_config(config_data)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(t("title"))
        self.btn_theme.setText(t("btn_theme"))
        self.btn_lang.setText(t("btn_lang"))
        self.tabs.setTabText(0, t("tab_generate"))
        self.tabs.setTabText(1, t("tab_history"))
        self.tabs.setTabText(2, t("tab_templates"))
        self.result_group.setTitle(t("result_title"))
        self.ref_group.setTitle(t("ref_title"))
        
        self.api_group.setTitle(t("api_group"))
        self.model_group.setTitle(t("model_group"))
        self.prompt_group.setTitle(t("prompt_group"))
        self.size_group.setTitle(t("size_group"))
        self.retry_group.setTitle(t("retry_group"))
        self.op_group.setTitle(t("cmd_group"))
        
        self.lbl_image_path.setText(t("image_path"))
        self.lbl_chat_path.setText(t("chat_path"))
        self.lbl_image_token.setText(t("image_token"))
        self.lbl_chat_token.setText(t("chat_token"))
        self.lbl_model_label.setText(t("model_label"))
        self.lbl_size_label.setText(t("size_label"))
        self.lbl_quality_label.setText(t("quality_label"))
        self.lbl_count_label.setText(t("image_count"))
        self.lbl_retry_count.setText(t("retry_count"))
        
        self.chk_auto_retry.setText(t("retry_enable"))
        self.btn_clear_history.setText(t("btn_clear_history"))
        self.btn_save_tpl.setText(t("btn_save_template"))
        self.btn_load_tpl.setText(t("btn_load_template"))
        self.btn_del_tpl.setText(t("btn_delete_template"))
        
        # Translate proxy settings label and placeholder
        if hasattr(self, "lbl_proxy"):
            self.lbl_proxy.setText(t("proxy_label"))
        if hasattr(self, "txt_proxy"):
            self.txt_proxy.setPlaceholderText(t("proxy_placeholder"))

        # Translate Prompt Advanced Settings tab
        self.btn_adv_translate.setText(t("btn_adv_translate"))
        self.btn_adv_optimize.setText(t("btn_adv_optimize"))
        self.btn_adv_apply.setText(t("btn_adv_apply"))
        self.txt_adv_original.setPlaceholderText(t("prompt_original_placeholder"))
        self.txt_adv_optimized.setPlaceholderText(t("prompt_optimized_placeholder"))
        
        current_idx = self.cb_size.currentIndex()
        self.cb_size.clear()
        self.cb_size.addItems([
            t("size_auto"),
            t("size_square"),
            t("size_landscape"),
            t("size_portrait"),
            t("size_2k_square"),
            t("size_2k_landscape"),
            t("size_2k_portrait"),
            t("size_4k_landscape"),
            t("size_4k_portrait")
        ])
        if current_idx >= 0:
            self.cb_size.setCurrentIndex(current_idx)
            
        self.txt_prompt.setPlaceholderText(t("prompt_placeholder"))
        self.refresh_history()
        
        self.update_ref_images_ui()
        if not self.is_running:
            self.lbl_result_img.setText(t("result_waiting"))
            self.lbl_status.setText(t("status_ready"))
            self.lbl_timer.setText(t("elapsed").format(0))
        else:
            elapsed = int(time.time() - self.start_time)
            self.lbl_timer.setText(t("elapsed").format(elapsed))
        self.btn_generate.setText(t("btn_generate"))
        self.btn_select_ref.setText(t("btn_select_ref"))

    # ---- Prompt 高级功能 ----
    def create_menu_bar(self):
        menubar = self.menuBar()
        self.prompt_menu = menubar.addMenu("Prompt" if config_data.get("LANGUAGE", "zh") == "en" else "提示词")
        
        self.act_adv_settings = QAction(t("tab_prompt_adv"), self)
        self.act_adv_settings.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        
        self.act_ai_translate = QAction(t("btn_adv_translate"), self)
        self.act_ai_translate.triggered.connect(lambda: [self.tabs.setCurrentIndex(1), self.run_ai_translate()])
        
        self.act_ai_optimize = QAction(t("btn_adv_optimize"), self)
        self.act_ai_optimize.triggered.connect(lambda: [self.tabs.setCurrentIndex(1), self.run_ai_optimize()])
        
        self.prompt_menu.addAction(self.act_adv_settings)
        self.prompt_menu.addSeparator()
        self.prompt_menu.addAction(self.act_ai_translate)
        self.prompt_menu.addAction(self.act_ai_optimize)

        # Settings Menu (设置菜单)
        self.settings_menu = menubar.addMenu("Settings" if config_data.get("LANGUAGE", "zh") == "en" else "设置")
        self.act_proxy_settings = QAction(t("proxy_label"), self)
        self.act_proxy_settings.triggered.connect(self.open_proxy_dialog)
        self.settings_menu.addAction(self.act_proxy_settings)

    def open_proxy_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(t("proxy_label"))
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        lbl = QLabel(t("proxy_label"))
        txt = QLineEdit(self.proxy_url_val)
        txt.setPlaceholderText(t("proxy_placeholder"))
        
        layout.addWidget(lbl)
        layout.addWidget(txt)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Save" if config_data.get("LANGUAGE", "zh") == "en" else "保存")
        btn_cancel = QPushButton("Cancel" if config_data.get("LANGUAGE", "zh") == "en" else "取消")
        
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)
        
        # Connect buttons
        btn_save.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        if dialog.exec() == QDialog.Accepted:
            self.proxy_url_val = txt.text().strip()
            # Save configuration immediately
            self.save_current_config(
                self.cb_model.currentText().strip(),
                self.txt_api_token.text().strip(),
                self.cb_quality.currentText().strip(),
                self.chk_auto_retry.isChecked(),
                self.spin_retry_count.value()
            )

    def on_tab_changed(self, index):
        if self.tabs.tabText(index) == t("tab_prompt_adv"):
            # Update the original prompt with the text from Generate prompt box
            self.txt_adv_original.setPlainText(self.txt_prompt.toPlainText().strip())

    def run_ai_translate(self):
        original_text = self.txt_adv_original.toPlainText().strip()
        if not original_text:
            return
        
        chat_token = self.txt_chat_api_token.text().strip()
        if not chat_token:
            chat_token = self.txt_image_api_token.text().strip()
        if not chat_token:
            self.lbl_adv_status.setText(t("empty_token"))
            return

        self.btn_adv_translate.setEnabled(False)
        self.btn_adv_optimize.setEnabled(False)
        self.btn_adv_apply.setEnabled(False)
        self.lbl_adv_status.setText(t("adv_status_translating"))

        self.prompt_worker = PromptProcessThread(
            api_url=self.txt_chat_api_url.text().strip(),
            token=chat_token,
            model=self.cb_model.currentText().strip(),
            prompt=original_text,
            task_type="translate",
            proxy_url=self.proxy_url_val
        )
        self.prompt_worker.success.connect(self.handle_prompt_success)
        self.prompt_worker.error.connect(self.handle_prompt_error)
        self.prompt_worker.finished.connect(self.prompt_worker_finished)
        self.prompt_worker.start()

    def run_ai_optimize(self):
        original_text = self.txt_adv_original.toPlainText().strip()
        if not original_text:
            return
        
        chat_token = self.txt_chat_api_token.text().strip()
        if not chat_token:
            chat_token = self.txt_image_api_token.text().strip()
        if not chat_token:
            self.lbl_adv_status.setText(t("empty_token"))
            return

        self.btn_adv_translate.setEnabled(False)
        self.btn_adv_optimize.setEnabled(False)
        self.btn_adv_apply.setEnabled(False)
        self.lbl_adv_status.setText(t("adv_status_optimizing"))

        self.prompt_worker = PromptProcessThread(
            api_url=self.txt_chat_api_url.text().strip(),
            token=chat_token,
            model=self.cb_model.currentText().strip(),
            prompt=original_text,
            task_type="optimize",
            proxy_url=self.proxy_url_val
        )
        self.prompt_worker.success.connect(self.handle_prompt_success)
        self.prompt_worker.error.connect(self.handle_prompt_error)
        self.prompt_worker.finished.connect(self.prompt_worker_finished)
        self.prompt_worker.start()

    def handle_prompt_success(self, result):
        self.txt_adv_optimized.setPlainText(result)
        self.lbl_adv_status.setText(t("status_done"))

    def handle_prompt_error(self, err_msg):
        self.txt_adv_optimized.setPlainText(f"Error:\n{err_msg}")
        self.lbl_adv_status.setText(t("status_error"))

    def prompt_worker_finished(self):
        self.btn_adv_translate.setEnabled(True)
        self.btn_adv_optimize.setEnabled(True)
        self.btn_adv_apply.setEnabled(True)
        self.prompt_worker = None

    def apply_adv_prompt(self):
        optimized_text = self.txt_adv_optimized.toPlainText().strip()
        if optimized_text and not optimized_text.startswith("Error:"):
            self.txt_prompt.setPlainText(optimized_text)
            self.tabs.setCurrentIndex(0)

    # ---- 参考图 ----
    def select_reference_image(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, t("select_ref_title"), "", t("image_files"))
        if file_paths:
            self.ref_image_paths = file_paths
            self.update_ref_images_ui()

    def clear_reference(self):
        self.ref_image_paths = []
        self.update_ref_images_ui()

    def ref_context_menu(self, pos):
        if not self.ref_image_paths:
            return
        menu = QMenu(self)
        if config_data.get("DARK_THEME", False):
            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(20, 10, 30, 250);
                    border: 1px solid rgba(160, 100, 240, 120);
                    color: #f0e6ff;
                }
                QMenu::item {
                    padding: 6px 20px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: rgba(120, 50, 190, 200);
                    color: #ffffff;
                }
            """)
        else:
            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(255, 255, 255, 250);
                    border: 1px solid rgba(150, 200, 220, 150);
                    color: #003b59;
                }
                QMenu::item {
                    padding: 6px 20px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: rgba(150, 220, 255, 200);
                    color: #004d40;
                }
            """)
            
        act_clear = QAction("清除所有参考图", self)
        act_clear.triggered.connect(self.clear_reference)
        menu.addAction(act_clear)
        menu.exec(self.ref_scroll.mapToGlobal(pos))

    def update_ref_images_ui(self):
        # Clear existing widgets inside the scroll area layout
        for i in reversed(range(self.ref_container_layout.count())):
            widget = self.ref_container_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
                
        if not self.ref_image_paths:
            self.lbl_ref_placeholder = QLabel(t("ref_none"))
            self.lbl_ref_placeholder.setAlignment(Qt.AlignCenter)
            self.ref_container_layout.addWidget(self.lbl_ref_placeholder)
            self.lbl_mode.setText(t("mode_txt2img"))
            self.lbl_mode.setStyleSheet("color: gray; font-style: italic;")
        else:
            self.lbl_mode.setText(t("mode_img2img"))
            self.lbl_mode.setStyleSheet("color: blue; font-style: italic;")
            
            for path in self.ref_image_paths:
                if os.path.exists(path):
                    thumb_widget = ThumbnailWidget(path, self)
                    thumb_widget.close_clicked.connect(self.remove_reference_image)
                    thumb_widget.clicked.connect(self.show_magnified_image)
                    self.ref_container_layout.addWidget(thumb_widget)

    def remove_reference_image(self, path):
        if path in self.ref_image_paths:
            self.ref_image_paths.remove(path)
            self.update_ref_images_ui()

    def show_magnified_image(self, path):
        if not os.path.exists(path):
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("查看大图")
        lay = QVBoxLayout(dialog)
        lay.setContentsMargins(10, 10, 10, 10)
        
        lbl = QLabel()
        pixmap = QPixmap(path)
        lbl.setPixmap(pixmap.scaled(700, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl)
        
        # Apply dialog style locally to avoid dark mode issues
        if config_data.get("DARK_THEME", False):
            dialog.setStyleSheet("""
                QDialog { background-color: #281e3c; }
                QLabel { border: 1px solid #a064f0; }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog { background-color: #f0f8ff; }
                QLabel { border: 1px solid #003b59; }
            """)
        dialog.exec()

    # ---- 生成 ----
    def execute_generation(self):
        if self.is_running:
            return

        current_prompt = self.txt_prompt.toPlainText().strip()
        if not current_prompt:
            self.lbl_status.setText(t("status_blocked"))
            self.lbl_result_img.setText(t("empty_prompt"))
            return

        mode = "image" if self.ref_image_paths else "text"

        image_token = self.txt_image_api_token.text().strip()
        chat_token = self.txt_chat_api_token.text().strip()

        target_token = chat_token if mode == "image" else image_token
        if not target_token:
            target_token = image_token if mode == "image" else chat_token

        if not target_token:
            self.lbl_status.setText(t("status_blocked"))
            self.lbl_result_img.setText(t("empty_token"))
            return

        self.is_running = True
        self.toggle_buttons(False)
        self.start_time = time.time()
        self.ui_timer.start(1000)

        current_model = self.cb_model.currentText().strip()
        current_quality = self.cb_quality.currentText().strip()
        auto_retry = self.chk_auto_retry.isChecked()
        retry_count = self.spin_retry_count.value()

        self.proxy_url_val = self.txt_proxy.text().strip()
        self.save_current_config(current_model, image_token, chat_token, current_quality, auto_retry, retry_count)

        self.worker = ImageGenerateThread(
            mode=mode, api_url=None,
            image_api_url=self.txt_image_api_url.text().strip(),
            chat_api_url=self.txt_chat_api_url.text().strip(),
            token=target_token, model=current_model, prompt=current_prompt,
            size=self.cb_size.currentText(), quality=current_quality,
            ref_image_paths=self.ref_image_paths if mode == "image" else [],
            auto_retry=auto_retry, retry_count=retry_count,
            proxy_url=self.proxy_url_val,
            n=self.spin_count.value()
        )
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.error.connect(self.handle_error)
        self.worker.success.connect(self.handle_success)
        self.worker.finished.connect(self.generation_finished)
        self.worker.start()

    def save_current_config(self, model, image_token, chat_token, quality, auto_retry, retry_count):
        try:
            self.proxy_url_val = self.txt_proxy.text().strip()
            history = config_data.get("MODEL_HISTORY", DEFAULT_MODELS.copy())
            if model and model not in history:
                history.append(model)
            config_data.update({
                "IMAGE_API_URL": self.txt_image_api_url.text().strip(),
                "CHAT_API_URL": self.txt_chat_api_url.text().strip(),
                "IMAGE_API_TOKEN": image_token,
                "CHAT_API_TOKEN": chat_token,
                "DEFAULT_API_TOKEN": image_token,
                "LAST_USED_MODEL": model,
                "MODEL_HISTORY": history,
                "DEFAULT_QUALITY": quality,
                "AUTO_RETRY": auto_retry,
                "RETRY_COUNT": retry_count,
                "PROXY_URL": self.proxy_url_val,
                "DEFAULT_IMAGE_COUNT": self.spin_count.value()
            })
            save_config(config_data)
            if self.cb_model.findText(model) == -1:
                self.cb_model.addItem(model)
        except:
            pass

    def toggle_buttons(self, enabled):
        self.btn_generate.setEnabled(enabled)
        self.btn_select_ref.setEnabled(enabled)

    def sync_model_selectors_from_adv(self, text):
        self.cb_model.blockSignals(True)
        self.cb_model.setCurrentText(text)
        self.cb_model.blockSignals(False)

    def sync_model_selectors_from_main(self, text):
        self.cb_adv_model.blockSignals(True)
        self.cb_adv_model.setCurrentText(text)
        self.cb_adv_model.blockSignals(False)

    def on_fetch_models(self):
        chat_url = self.txt_chat_api_url.text().strip()
        chat_token = self.txt_chat_api_token.text().strip()
        if not chat_token:
            chat_token = self.txt_image_api_token.text().strip()

        if not chat_url or not chat_token:
            QMessageBox.warning(self, t("confirm_title"), "请先配置 Chat 路径或 API Token")
            return

        self.btn_fetch_models.setEnabled(False)
        self.btn_fetch_models.setText("...")
        self.btn_adv_fetch_models.setEnabled(False)
        self.btn_adv_fetch_models.setText("...")
        self.lbl_status.setText("正在获取模型列表...")

        self.fetch_thread = ModelFetchThread(chat_url, chat_token, self.proxy_url_val)
        self.fetch_thread.success.connect(self.handle_fetch_models_success)
        self.fetch_thread.error.connect(self.handle_fetch_models_error)
        
        def on_finished():
            self.btn_fetch_models.setEnabled(True)
            self.btn_fetch_models.setText("🔄")
            self.btn_adv_fetch_models.setEnabled(True)
            self.btn_adv_fetch_models.setText("🔄")
        self.fetch_thread.finished.connect(on_finished)
        self.fetch_thread.start()

    def handle_fetch_models_success(self, models):
        self.cb_model.blockSignals(True)
        self.cb_adv_model.blockSignals(True)
        
        current = self.cb_model.currentText()
        
        self.cb_model.clear()
        self.cb_adv_model.clear()
        
        self.cb_model.addItems(models)
        self.cb_adv_model.addItems(models)
        
        if current in models:
            self.cb_model.setCurrentText(current)
            self.cb_adv_model.setCurrentText(current)
        elif models:
            self.cb_model.setCurrentIndex(0)
            self.cb_adv_model.setCurrentIndex(0)
            
        self.cb_model.blockSignals(False)
        self.cb_adv_model.blockSignals(False)
        
        # Update config history as well
        config_data["MODEL_HISTORY"] = models
        save_config(config_data)

        self.lbl_status.setText(f"成功获取 {len(models)} 个模型")
        QMessageBox.information(self, "成功", f"成功拉取到 {len(models)} 个可用模型！")

    def handle_fetch_models_error(self, err):
        self.lbl_status.setText("拉取模型失败")
        QMessageBox.critical(self, "错误", f"获取模型列表失败: {err}")

    def handle_error(self, err_msg, prompt, metadata=None):
        self.result_stack.setCurrentIndex(0)
        self.lbl_result_img.setPixmap(QPixmap())
        self.lbl_result_img.setText(err_msg)
        self.add_history(prompt, "", "failed", [], metadata)

    def handle_success(self, file_paths, prompt, model, metadata=None):
        self.add_history(prompt, model, "success", file_paths, metadata)
        if len(file_paths) == 1:
            self.result_stack.setCurrentIndex(0)
            pixmap = QPixmap(file_paths[0])
            self.lbl_result_img.setPixmap(pixmap.scaled(self.lbl_result_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.display_generated_images(file_paths)

    def display_generated_images(self, paths):
        for i in reversed(range(self.result_grid_layout.count())):
            widget = self.result_grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
                
        num_images = len(paths)
        if num_images <= 2:
            rows, cols = 1, 2
        elif num_images <= 4:
            rows, cols = 2, 2
        elif num_images <= 6:
            rows, cols = 2, 3
        else:
            rows, cols = 3, 3
            
        for idx, path in enumerate(paths[:9]):
            if os.path.exists(path):
                r = idx // cols
                c = idx % cols
                
                lbl = QLabel()
                pixmap = QPixmap(path)
                lbl.setPixmap(pixmap.scaled(QSize(280, 280), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setCursor(Qt.PointingHandCursor)
                lbl.setStyleSheet("border: 1px solid rgba(128,128,128,100); border-radius: 6px; background-color: rgba(0,0,0,40);")
                lbl.mousePressEvent = lambda event, p=path: self.show_magnified_image(p)
                
                self.result_grid_layout.addWidget(lbl, r, c)
        
        self.result_stack.setCurrentIndex(1)

    @Slot()
    def update_timer_label(self):
        elapsed = int(time.time() - self.start_time)
        self.lbl_timer.setText(t("elapsed").format(elapsed))

    def generation_finished(self):
        self.ui_timer.stop()
        self.is_running = False
        self.toggle_buttons(True)
        self.worker = None

    # ---- 历史记录 ----
    def add_history(self, prompt, model, status, image_paths, metadata=None):
        metadata = metadata or {}
        # Ensure image_paths is a list
        if isinstance(image_paths, str):
            image_paths = [image_paths] if image_paths else []
        entry = {
            "prompt": prompt,
            "model": model,
            "status": status,
            "images": image_paths,
            "image": image_paths[0] if image_paths else "",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "api_url": metadata.get("api_url", ""),
            "duration": metadata.get("duration", ""),
            "prompt_tokens": metadata.get("prompt_tokens", 0),
            "completion_tokens": metadata.get("completion_tokens", 0),
            "total_tokens": metadata.get("total_tokens", 0)
        }
        history_data.insert(0, entry)
        if len(history_data) > 200:
            history_data.pop()
        save_json_file(HISTORY_FILE, history_data)
        self.refresh_history()

    def refresh_history(self):
        self.history_list.clear()
        if not history_data:
            self.history_list.addItem(t("history_empty"))
            return
        for entry in history_data:
            item = QListWidgetItem()
            item.setSizeHint(QSize(400, 100))
            item.setData(Qt.UserRole, entry)
            self.history_list.addItem(item)
            
            widget = HistoryItemWidget(entry, self)
            self.history_list.setItemWidget(item, widget)

    def history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item:
            return
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        menu = QMenu(self)
        if config_data.get("DARK_THEME", False):
            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(20, 10, 30, 250);
                    border: 1px solid rgba(160, 100, 240, 120);
                    color: #f0e6ff;
                }
                QMenu::item {
                    padding: 6px 20px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: rgba(120, 50, 190, 200);
                    color: #ffffff;
                }
            """)
        else:
            menu.setStyleSheet("""
                QMenu {
                    background-color: rgba(255, 255, 255, 250);
                    border: 1px solid rgba(150, 200, 220, 150);
                    color: #003b59;
                }
                QMenu::item {
                    padding: 6px 20px;
                    background-color: transparent;
                }
                QMenu::item:selected {
                    background-color: rgba(150, 220, 255, 200);
                    color: #004d40;
                }
            """)
        
        act_details = QAction("查看详情", self)
        act_details.triggered.connect(lambda: self.on_history_item_clicked(item))
        menu.addAction(act_details)
        
        act_reuse = QAction(t("reuse_prompt"), self)
        act_reuse.triggered.connect(lambda: self.txt_prompt.setPlainText(entry.get("prompt", "")))
        menu.addAction(act_reuse)
        
        act_delete = QAction("删除此条记录", self)
        act_delete.triggered.connect(lambda: self.delete_history_item(item))
        menu.addAction(act_delete)
        
        menu.exec_(self.history_list.mapToGlobal(pos))

    def on_history_item_clicked(self, item):
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        dialog = HistoryDetailDialog(entry, self)
        dialog.exec()

    def delete_history_item(self, item):
        entry = item.data(Qt.UserRole)
        if entry in history_data:
            history_data.remove(entry)
            save_json_file(HISTORY_FILE, history_data)
            self.refresh_history()

    def open_history_image(self, path):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            self.lbl_result_img.setPixmap(pixmap.scaled(self.lbl_result_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def clear_history(self):
        reply = QMessageBox.question(
            self, t("confirm_title"), t("confirm_clear"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history_data.clear()
            save_json_file(HISTORY_FILE, history_data)
            self.refresh_history()

    # ---- 模板 ----
    def refresh_template_list(self):
        self.template_list.clear()
        for tpl in templates_data:
            self.template_list.addItem(f"{tpl['name']}: {tpl['prompt'][:60]}")

    def save_template(self):
        text = self.txt_prompt.toPlainText().strip()
        if not text:
            return
        dialog = QInputDialog(self)
        dialog.setWindowTitle(t("template_title"))
        dialog.setLabelText(t("template_name"))
        dialog.setOkButtonText("OK")
        dialog.setCancelButtonText("Cancel")
        if config_data.get("DARK_THEME", False):
            dialog.setStyleSheet("""
                QInputDialog, QDialog { background-color: #281e3c; }
                QLabel { color: #f0e6ff; }
                QLineEdit { background-color: #140a1e; color: #f0e6ff; border: 1px solid #a064f0; }
                QPushButton { background-color: #3c2d5a; color: #f0e6ff; border: 1px solid #a064f0; }
            """)
        else:
            dialog.setStyleSheet("""
                QInputDialog, QDialog { background-color: #f0f8ff; }
                QLabel { color: #003b59; }
                QLineEdit { background-color: #ffffff; color: #004d40; border: 1px solid #003b59; }
                QPushButton { background-color: #e0f0ff; color: #006064; border: 1px solid #003b59; }
            """)
        ok = dialog.exec()
        name = dialog.textValue()
        if ok and name:
            templates_data.append({"name": name, "prompt": text})
            save_json_file(TEMPLATES_FILE, templates_data)
            self.refresh_template_list()

    def load_template(self):
        row = self.template_list.currentRow()
        if 0 <= row < len(templates_data):
            self.txt_prompt.setPlainText(templates_data[row]["prompt"])
            self.tabs.setCurrentIndex(0)

    def delete_template(self):
        row = self.template_list.currentRow()
        if 0 <= row < len(templates_data):
            templates_data.pop(row)
            save_json_file(TEMPLATES_FILE, templates_data)
            self.refresh_template_list()

    # ---- 关闭 ----
    def closeEvent(self, event):
        try:
            self.save_current_config(
                self.cb_model.currentText().strip(),
                self.txt_api_token.text().strip(),
                self.cb_quality.currentText().strip(),
                self.chk_auto_retry.isChecked(),
                self.spin_retry_count.value()
            )
        except:
            pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
