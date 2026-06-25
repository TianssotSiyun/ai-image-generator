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
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QComboBox, QPlainTextEdit, QPushButton, QFileDialog,
    QGroupBox, QFormLayout, QSplitter, QCheckBox, QSpinBox, QTabWidget,
    QListWidget, QListWidgetItem, QInputDialog, QMenu, QDialog, QTextEdit,
    QMessageBox
)
from PySide6.QtGui import QPixmap, QAction

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
config_data.setdefault("PROXY_URL", "")

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
    success = Signal(str, str, str)
    error = Signal(str, str)
    status = Signal(str)

    def __init__(self, mode, api_url, image_api_url, chat_api_url, token, model, prompt, size, quality, ref_image_path=None, auto_retry=False, retry_count=3, proxy_url=None):
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
        self.ref_image_path = ref_image_path
        self.auto_retry = auto_retry
        self.retry_count = retry_count
        self.proxy_url = proxy_url

    def determine_api_url(self):
        if self.mode == "image" and self.ref_image_path and os.path.exists(self.ref_image_path):
            return self.image_api_url
        return self.chat_api_url

    def run(self):
        api_url = self.determine_api_url()
        attempt = 0
        max_attempts = self.retry_count if self.auto_retry else 1

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
                    "n": 1
                }
                if self.mode == "image" and self.ref_image_path and os.path.exists(self.ref_image_path):
                    with open(self.ref_image_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                    payload["image"] = f"data:image/jpeg;base64,{b64}"
                    payload["image_url"] = f"data:image/jpeg;base64,{b64}"
            else:
                messages = []
                if self.mode == "text":
                    messages.append({"role": "user", "content": f"Generate an image. Prompt: {self.prompt}"})
                else:
                    if not self.ref_image_path or not os.path.exists(self.ref_image_path):
                        self.error.emit(t("ref_missing"), "")
                        return
                    with open(self.ref_image_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                    messages.append({"role": "user", "content": [
                        {"type": "text", "text": f"Modify this image. Prompt: {self.prompt}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]})
                payload = {"model": self.model, "messages": messages, "size": api_size}

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
                response.raise_for_status()
                res_data = response.json()

                img_url = None
                img_base64 = None

                if 'data' in res_data and len(res_data['data']) > 0:
                    data_item = res_data['data'][0]
                    img_url = data_item.get('url')
                    if not img_url and 'b64_json' in data_item:
                        img_base64 = data_item['b64_json']

                if not img_url and not img_base64 and 'choices' in res_data:
                    content = res_data['choices'][0]['message']['content']
                    urls = re.findall(r'https?://[^\s()<>"]+\.(?:png|jpg|jpeg|webp|gif)', content, re.IGNORECASE)
                    if urls:
                        img_url = urls[0]

                if not img_url and not img_base64:
                    raise Exception(f"{t('extract_error')}: {json.dumps(res_data, ensure_ascii=False)}")

                self.status.emit(t("processing"))

                if img_base64:
                    img_bytes = base64.b64decode(img_base64)
                    if img_bytes[:8] == b'\x89PNG\r\n\x1a\n': ext = 'png'
                    elif img_bytes[:2] == b'\xff\xd8': ext = 'jpg'
                    elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP': ext = 'webp'
                    else: ext = 'png'
                    filename = f"gen_{timestamp}_{random_suffix}.{ext}"
                    save_path = os.path.join(IMAGE_OUT_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(img_bytes)
                else:
                    img_response = session.get(img_url, timeout=(10, 60))
                    img_response.raise_for_status()
                    ct = img_response.headers.get('content-type', '')
                    if 'jpeg' in ct or 'jpg' in ct: ext = 'jpg'
                    elif 'png' in ct: ext = 'png'
                    elif 'webp' in ct: ext = 'webp'
                    else: ext = 'png'
                    filename = f"gen_{timestamp}_{random_suffix}.{ext}"
                    save_path = os.path.join(IMAGE_OUT_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(img_response.content)

                self.success.emit(save_path, self.prompt, self.model)
                self.status.emit(t("status_done"))
                return

            except requests.exceptions.HTTPError as http_err:
                try:
                    err_detail = response.json() if response else str(http_err)
                    self.error.emit(f"{t('http_error').format(response.status_code)}:\n{json.dumps(err_detail, ensure_ascii=False, indent=2)}", self.prompt)
                except:
                    self.error.emit(f"{t('net_error')}:\n{str(http_err)}", self.prompt)
                self.status.emit(f"{t('status_error')} ({attempt}/{max_attempts})")
            except Exception as e:
                self.error.emit(f"{t('exception')}:\n{str(e)}", self.prompt)
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


# ==========================================
# 3. 主界面窗口
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("title"))
        self.resize(1300, 850)
        self.ref_image_path = ""
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
        main_layout.addLayout(toolbar)

        # 主内容区
        main_splitter = QSplitter(Qt.Horizontal)

        # 左侧预览区
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.result_group = QGroupBox(t("result_title"))
        result_layout = QVBoxLayout(self.result_group)
        self.lbl_result_img = QLabel(t("result_waiting"))
        self.lbl_result_img.setAlignment(Qt.AlignCenter)
        self.lbl_result_img.setWordWrap(True)
        self.lbl_result_img.setMargin(15)
        result_layout.addWidget(self.lbl_result_img)
        left_layout.addWidget(self.result_group, stretch=2)

        self.ref_group = QGroupBox(t("ref_title"))
        ref_layout = QVBoxLayout(self.ref_group)
        self.lbl_ref_img = QLabel(t("ref_none"))
        self.lbl_ref_img.setAlignment(Qt.AlignCenter)
        ref_layout.addWidget(self.lbl_ref_img)
        left_layout.addWidget(self.ref_group, stretch=1)

        main_splitter.addWidget(left_widget)

        # 右侧选项卡
        self.tabs = QTabWidget()

        # --- 选项卡1: 生成 ---
        gen_tab = QWidget()
        gen_layout = QVBoxLayout(gen_tab)

        self.api_group = QGroupBox(t("api_group"))
        api_form = QFormLayout(self.api_group)
        self.txt_image_api_url = QLineEdit(config_data.get("IMAGE_API_URL"))
        self.txt_chat_api_url = QLineEdit(config_data.get("CHAT_API_URL"))
        self.txt_api_token = QLineEdit(config_data.get("DEFAULT_API_TOKEN"))
        self.txt_api_token.setEchoMode(QLineEdit.Password)
        
        self.lbl_image_path = QLabel(t("image_path"))
        self.lbl_chat_path = QLabel(t("chat_path"))
        self.lbl_api_token = QLabel(t("api_token"))
        
        api_form.addRow(self.lbl_image_path, self.txt_image_api_url)
        api_form.addRow(self.lbl_chat_path, self.txt_chat_api_url)
        api_form.addRow(self.lbl_api_token, self.txt_api_token)
        gen_layout.addWidget(self.api_group)

        self.model_group = QGroupBox(t("model_group"))
        model_form = QFormLayout(self.model_group)
        self.cb_model = QComboBox()
        self.cb_model.setEditable(True)
        self.cb_model.addItems(config_data["MODEL_HISTORY"])
        self.cb_model.setCurrentText(config_data["LAST_USED_MODEL"])
        
        self.lbl_model_label = QLabel(t("model_label"))
        model_form.addRow(self.lbl_model_label, self.cb_model)
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
        self.btn_generate.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
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
        main_layout.addWidget(main_splitter)
        central.setLayout(main_layout)

        # Connect tab change signal
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Add a top native menu bar for "Prompt" options
        self.create_menu_bar()

    # ---- 主题 ----
    def apply_theme(self):
        if config_data.get("DARK_THEME", False):
            self.setStyleSheet("""
                QMainWindow, QWidget { background-color: #2b2b2b; color: #e0e0e0; }
                QGroupBox { border: 1px solid #555; border-radius: 5px; margin-top: 10px; padding-top: 15px; color: #e0e0e0; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
                QLineEdit, QComboBox, QPlainTextEdit, QSpinBox { background-color: #3c3c3c; color: #e0e0e0; border: 1px solid #555; }
                QPushButton { background-color: #4a4a4a; color: #e0e0e0; border: 1px solid #555; padding: 6px 12px; border-radius: 4px; }
                QPushButton:hover { background-color: #5a5a5a; }
                QPushButton:disabled { background-color: #333; color: #666; }
                QTabWidget::pane { border: 1px solid #555; }
                QTabBar::tab { background: #3c3c3c; color: #e0e0e0; padding: 8px 16px; border: 1px solid #555; }
                QTabBar::tab:selected { background: #4a4a4a; }
                QListWidget { background-color: #3c3c3c; color: #e0e0e0; border: 1px solid #555; }
                QLabel { color: #e0e0e0; }
                QCheckBox { color: #e0e0e0; }
            """)
        else:
            self.setStyleSheet("")

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
        self.lbl_api_token.setText(t("api_token"))
        self.lbl_model_label.setText(t("model_label"))
        self.lbl_size_label.setText(t("size_label"))
        self.lbl_quality_label.setText(t("quality_label"))
        self.lbl_retry_count.setText(t("retry_count"))
        
        self.chk_auto_retry.setText(t("retry_enable"))
        self.btn_clear_history.setText(t("btn_clear_history"))
        self.btn_save_tpl.setText(t("btn_save_template"))
        self.btn_load_tpl.setText(t("btn_load_template"))
        self.btn_del_tpl.setText(t("btn_delete_template"))
        
        # Translate menu bar items if defined
        if hasattr(self, "prompt_menu"):
            self.prompt_menu.setTitle("Prompt" if config_data.get("LANGUAGE", "zh") == "en" else "提示词")
            self.act_adv_settings.setText(t("tab_prompt_adv"))
            self.act_ai_translate.setText(t("btn_adv_translate"))
            self.act_ai_optimize.setText(t("btn_adv_optimize"))
            
        if hasattr(self, "settings_menu"):
            self.settings_menu.setTitle("Settings" if config_data.get("LANGUAGE", "zh") == "en" else "设置")
            self.act_proxy_settings.setText(t("proxy_label"))

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
        
        if not self.ref_image_path:
            self.lbl_ref_img.setText(t("ref_none"))
            self.lbl_mode.setText(t("mode_txt2img"))
        else:
            self.lbl_mode.setText(t("mode_img2img"))
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
        
        api_token = self.txt_api_token.text().strip()
        if not api_token:
            self.lbl_adv_status.setText(t("empty_token"))
            return

        self.btn_adv_translate.setEnabled(False)
        self.btn_adv_optimize.setEnabled(False)
        self.btn_adv_apply.setEnabled(False)
        self.lbl_adv_status.setText(t("adv_status_translating"))

        self.prompt_worker = PromptProcessThread(
            api_url=self.txt_chat_api_url.text().strip(),
            token=api_token,
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
        
        api_token = self.txt_api_token.text().strip()
        if not api_token:
            self.lbl_adv_status.setText(t("empty_token"))
            return

        self.btn_adv_translate.setEnabled(False)
        self.btn_adv_optimize.setEnabled(False)
        self.btn_adv_apply.setEnabled(False)
        self.lbl_adv_status.setText(t("adv_status_optimizing"))

        self.prompt_worker = PromptProcessThread(
            api_url=self.txt_chat_api_url.text().strip(),
            token=api_token,
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
        file_path, _ = QFileDialog.getOpenFileName(self, t("select_ref_title"), "", t("image_files"))
        if file_path:
            self.ref_image_path = file_path
            pixmap = QPixmap(file_path)
            self.lbl_ref_img.setPixmap(pixmap.scaled(self.lbl_ref_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.lbl_mode.setText(t("mode_img2img"))
            self.lbl_mode.setStyleSheet("color: blue; font-style: italic;")

    def clear_reference(self):
        self.ref_image_path = ""
        self.lbl_ref_img.clear()
        self.lbl_ref_img.setText(t("ref_none"))
        self.lbl_mode.setText(t("mode_txt2img"))
        self.lbl_mode.setStyleSheet("color: gray; font-style: italic;")

    # ---- 生成 ----
    def execute_generation(self):
        if self.is_running:
            return

        current_prompt = self.txt_prompt.toPlainText().strip()
        if not current_prompt:
            self.lbl_status.setText(t("status_blocked"))
            self.lbl_result_img.setText(t("empty_prompt"))
            return

        mode = "image" if self.ref_image_path else "text"

        api_token = self.txt_api_token.text().strip()
        if not api_token:
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

        self.save_current_config(current_model, api_token, current_quality, auto_retry, retry_count)

        self.worker = ImageGenerateThread(
            mode=mode, api_url=None,
            image_api_url=self.txt_image_api_url.text().strip(),
            chat_api_url=self.txt_chat_api_url.text().strip(),
            token=api_token, model=current_model, prompt=current_prompt,
            size=self.cb_size.currentText(), quality=current_quality,
            ref_image_path=self.ref_image_path if mode == "image" else None,
            auto_retry=auto_retry, retry_count=retry_count,
            proxy_url=self.proxy_url_val
        )
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.error.connect(self.handle_error)
        self.worker.success.connect(self.handle_success)
        self.worker.finished.connect(self.generation_finished)
        self.worker.start()

    def save_current_config(self, model, token, quality, auto_retry, retry_count):
        try:
            history = config_data.get("MODEL_HISTORY", DEFAULT_MODELS.copy())
            if model and model not in history:
                history.append(model)
            config_data.update({
                "IMAGE_API_URL": self.txt_image_api_url.text().strip(),
                "CHAT_API_URL": self.txt_chat_api_url.text().strip(),
                "DEFAULT_API_TOKEN": token,
                "LAST_USED_MODEL": model,
                "MODEL_HISTORY": history,
                "DEFAULT_QUALITY": quality,
                "AUTO_RETRY": auto_retry,
                "RETRY_COUNT": retry_count,
                "PROXY_URL": self.proxy_url_val
            })
            save_config(config_data)
            if self.cb_model.findText(model) == -1:
                self.cb_model.addItem(model)
        except:
            pass

    def toggle_buttons(self, enabled):
        self.btn_generate.setEnabled(enabled)
        self.btn_select_ref.setEnabled(enabled)

    def handle_error(self, err_msg, prompt):
        self.lbl_result_img.setPixmap(QPixmap())
        self.lbl_result_img.setText(err_msg)
        self.add_history(prompt, "", "failed", "")

    def handle_success(self, file_path, prompt, model):
        pixmap = QPixmap(file_path)
        self.lbl_result_img.setPixmap(pixmap.scaled(self.lbl_result_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.add_history(prompt, model, "success", file_path)

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
    def add_history(self, prompt, model, status, image_path):
        entry = {
            "prompt": prompt,
            "model": model,
            "status": status,
            "image": image_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            time_str = entry.get("time", "")
            prompt = entry.get("prompt", "")[:50]
            model = entry.get("model", "")
            status_raw = entry.get("status", "")
            if status_raw == "success":
                status = t("history_success")
            elif status_raw == "failed":
                status = t("history_failed")
            else:
                status = status_raw
            display = f"[{time_str}] {status} | {model} | {prompt}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, entry)
            self.history_list.addItem(item)

    def history_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item:
            return
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        menu = QMenu(self)
        if entry.get("image"):
            act_open = QAction(t("history_image"), self)
            act_open.triggered.connect(lambda: self.open_history_image(entry["image"]))
            menu.addAction(act_open)
        act_reuse = QAction(t("reuse_prompt"), self)
        act_reuse.triggered.connect(lambda: self.txt_prompt.setPlainText(entry.get("prompt", "")))
        menu.addAction(act_reuse)
        menu.exec_(self.history_list.mapToGlobal(pos))

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
        name, ok = QInputDialog.getText(self, t("template_title"), t("template_name"))
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
