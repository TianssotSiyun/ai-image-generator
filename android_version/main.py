import os
import sys
import time
import base64
import json
import re
import random
import requests
import urllib.request
from datetime import datetime
import threading

# Set window size for local testing to simulate a mobile device
from kivy.utils import platform
if platform != 'android':
    from kivy.config import Config
    Config.set('graphics', 'width', '390')
    Config.set('graphics', 'height', '844')
    Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.cache import Cache
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line

# ==========================================
# 0. Translations & Globals
# ==========================================
DEFAULT_MODELS = ["gpt-image-2", "gpt-image-2-pro", "flux-dev"]
DEFAULT_QUALITIES = ["low", "medium", "high"]

LANG = {
    "zh": {
        "title": "AI 图像生成器",
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
        "prompt_optimized_label": "优化/翻译后的 Prompt:",
        "prompt_optimized_placeholder": "点击下方的“AI 翻译”或“AI 优化”获取结果...",
        "btn_adv_translate": "AI 翻译为英文",
        "btn_adv_optimize": "AI 优化 Prompt",
        "btn_adv_apply": "应用到主提示词",
        "adv_status_translating": "状态: 正在通过 AI 翻译...",
        "adv_status_optimizing": "状态: 正在通过 AI 优化...",
        "proxy_label": "代理设置:",
        "proxy_placeholder": "例如: http://127.0.0.1:7890 (留空为系统默认)",
        "settings_title": "系统设置",
        "clear_ref": "清除参考图",
        "nav_generate": "生成",
        "nav_prompt_adv": "高级",
        "nav_history": "历史",
        "nav_templates": "模板",
        "nav_settings": "设置",
        "add_model_title": "添加新模型",
        "add_model_prompt": "请输入模型名称:",
        "add_model_btn": "添加模型",
    },
    "en": {
        "title": "AI Image Generator",
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
        "settings_title": "System Settings",
        "clear_ref": "Clear Ref Image",
        "nav_generate": "Gen",
        "nav_prompt_adv": "Adv",
        "nav_history": "History",
        "nav_templates": "Templates",
        "nav_settings": "Settings",
        "add_model_title": "Add Model",
        "add_model_prompt": "Enter model name:",
        "add_model_btn": "Add Model",
    }
}

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

# ==========================================
# 1. Kivy Style Definition (KV)
# ==========================================
KV_STYLE = """
<StyledButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0.15, 0.35, 0.9, 1) if self.state == 'normal' else (0.1, 0.25, 0.7, 1)
    color: (1, 1, 1, 1)
    font_size: '14sp'
    bold: True
    size_hint_y: None
    height: '45dp'
    canvas.before:
        Color:
            rgba: (0.15, 0.35, 0.9, 1) if self.state == 'normal' else (0.1, 0.25, 0.7, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]

<SecondaryButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0.22, 0.22, 0.22, 1) if self.state == 'normal' else (0.18, 0.18, 0.18, 1)
    color: (0.9, 0.9, 0.9, 1)
    font_size: '13sp'
    size_hint_y: None
    height: '40dp'
    canvas.before:
        Color:
            rgba: (0.22, 0.22, 0.22, 1) if self.state == 'normal' else (0.18, 0.18, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]

<DangerButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: (0.75, 0.15, 0.15, 1) if self.state == 'normal' else (0.6, 0.12, 0.12, 1)
    color: (1, 1, 1, 1)
    font_size: '13sp'
    bold: True
    size_hint_y: None
    height: '40dp'
    canvas.before:
        Color:
            rgba: (0.75, 0.15, 0.15, 1) if self.state == 'normal' else (0.6, 0.12, 0.12, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]

<StyledTextInput@TextInput>:
    background_normal: ''
    background_active: ''
    background_color: (0.15, 0.15, 0.15, 1)
    foreground_color: (0.95, 0.95, 0.95, 1)
    cursor_color: (0.15, 0.35, 0.9, 1)
    hint_text_color: (0.5, 0.5, 0.5, 1)
    font_size: '14sp'
    padding: [10, 10, 10, 10]
    canvas.before:
        Color:
            rgba: (0.15, 0.35, 0.9, 1) if self.focus else (0.25, 0.25, 0.25, 1)
        Line:
            width: 1.1
            rounded_rectangle: (self.x, self.y, self.width, self.height, 6)

<StyledSpinner@Spinner>:
    background_normal: ''
    background_down: ''
    background_color: (0.2, 0.2, 0.2, 1) if self.state == 'normal' else (0.15, 0.15, 0.15, 1)
    color: (0.95, 0.95, 0.95, 1)
    font_size: '14sp'
    size_hint_y: None
    height: '42dp'
    canvas.before:
        Color:
            rgba: (0.2, 0.2, 0.2, 1) if self.state == 'normal' else (0.15, 0.15, 0.15, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [6]

<CardLayout@BoxLayout>:
    orientation: 'vertical'
    spacing: '8dp'
    padding: '12dp'
    size_hint_y: None
    height: self.minimum_height
    canvas.before:
        Color:
            rgba: (0.18, 0.18, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]

<NavBar@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '65dp'
    padding: ['4dp', '4dp', '4dp', '4dp']
    spacing: '4dp'
    canvas.before:
        Color:
            rgba: (0.1, 0.1, 0.1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: (0.2, 0.2, 0.2, 1)
        Line:
            points: [self.x, self.y + self.height, self.x + self.width, self.y + self.height]
            width: 1

<NavButton>:
    orientation: 'vertical'
    spacing: '2dp'
    padding: ['2dp', '6dp', '2dp', '4dp']
    canvas.before:
        Color:
            rgba: (0.15, 0.35, 0.9, 0.15) if self.active else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    Label:
        text: root.icon
        font_name: 'Roboto' if platform != 'android' else ''
        font_size: '20sp'
        size_hint_y: 0.6
        halign: 'center'
        color: (0.15, 0.35, 0.9, 1) if root.active else (0.65, 0.65, 0.65, 1)
    Label:
        text: root.text
        font_size: '11sp'
        size_hint_y: 0.4
        halign: 'center'
        color: (0.15, 0.35, 0.9, 1) if root.active else (0.65, 0.65, 0.65, 1)

<HistoryItem>:
    orientation: 'vertical'
    spacing: '5dp'
    padding: '8dp'
    size_hint_y: None
    height: '110dp'
    canvas.before:
        Color:
            rgba: self.status_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    BoxLayout:
        orientation: 'horizontal'
        spacing: '8dp'
        Image:
            id: img_thumb
            size_hint_x: None
            width: '60dp'
            allow_stretch: True
            keep_ratio: True
        BoxLayout:
            orientation: 'vertical'
            spacing: '2dp'
            Label:
                id: lbl_time_status
                text: ''
                font_size: '11sp'
                color: (0.7, 0.7, 0.7, 1)
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            Label:
                id: lbl_model
                text: ''
                font_size: '12sp'
                bold: True
                color: (0.9, 0.9, 0.9, 1)
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            Label:
                id: lbl_prompt
                text: ''
                font_size: '12sp'
                color: (0.8, 0.8, 0.8, 1)
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                shorten: True
                shorten_from: 'right'
        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: '70dp'
            spacing: '4dp'
            SecondaryButton:
                id: btn_view
                text: 'View'
                font_size: '11sp'
                height: '34dp'
            SecondaryButton:
                id: btn_reuse
                text: 'Reuse'
                font_size: '11sp'
                height: '34dp'

<TemplateItem>:
    orientation: 'horizontal'
    spacing: '8dp'
    padding: '8dp'
    size_hint_y: None
    height: '70dp'
    canvas.before:
        Color:
            rgba: (0.18, 0.18, 0.18, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [8]
    BoxLayout:
        orientation: 'vertical'
        spacing: '2dp'
        Label:
            id: lbl_name
            text: ''
            font_size: '13sp'
            bold: True
            color: (0.95, 0.95, 0.95, 1)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        Label:
            id: lbl_prompt
            text: ''
            font_size: '12sp'
            color: (0.7, 0.7, 0.7, 1)
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            shorten: True
            shorten_from: 'right'
    BoxLayout:
        orientation: 'horizontal'
        size_hint_x: None
        width: '120dp'
        spacing: '6dp'
        SecondaryButton:
            id: btn_load
            text: 'Load'
            font_size: '12sp'
            height: '36dp'
            size_hint_y: None
            pos_hint: {'center_y': 0.5}
        DangerButton:
            id: btn_delete
            text: 'Del'
            font_size: '12sp'
            height: '36dp'
            size_hint_y: None
            pos_hint: {'center_y': 0.5}
"""

# ==========================================
# 2. Asynchronous Thread Runners
# ==========================================
class ImageGenerateRunner:
    def __init__(self, mode, image_api_url, chat_api_url, token, model, prompt, size, quality, ref_image_path, auto_retry, retry_count, proxy_url, log_dir, image_out_dir, on_status, on_error, on_success, on_finished, translate_func):
        self.mode = mode
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
        self.log_dir = log_dir
        self.image_out_dir = image_out_dir
        
        self.on_status = on_status
        self.on_error = on_error
        self.on_success = on_success
        self.on_finished = on_finished
        self.t = translate_func

    def start(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()

    def run(self):
        # Determine API
        if self.mode == "image" and self.ref_image_path and os.path.exists(self.ref_image_path):
            api_url = self.image_api_url
        else:
            api_url = self.chat_api_url

        attempt = 0
        max_attempts = self.retry_count if self.auto_retry else 1

        while attempt < max_attempts:
            attempt += 1
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            log_file_path = os.path.join(self.log_dir, f"log_{timestamp}_{random_suffix}_attempt{attempt}.json")
            api_size = re.split(r'[(（]', self.size)[0].strip()

            url_lower = api_url.lower()
            response = None

            status_msg = self.t("sending").format(attempt, max_attempts)
            Clock.schedule_once(lambda dt: self.on_status(status_msg), 0)

            if "images/generations" in url_lower:
                payload = {
                    "model": self.model,
                    "prompt": self.prompt,
                    "size": api_size,
                    "quality": self.quality,
                    "n": 1
                }
                if self.mode == "image" and self.ref_image_path and os.path.exists(self.ref_image_path):
                    try:
                        with open(self.ref_image_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode('utf-8')
                        payload["image"] = f"data:image/jpeg;base64,{b64}"
                        payload["image_url"] = f"data:image/jpeg;base64,{b64}"
                    except Exception as ref_err:
                        Clock.schedule_once(lambda dt: self.on_error(f"{self.t('ref_missing')}: {str(ref_err)}", self.prompt), 0)
                        Clock.schedule_once(lambda dt: self.on_finished(), 0)
                        return
            else:
                messages = []
                if self.mode == "text":
                    messages.append({"role": "user", "content": f"Generate an image. Prompt: {self.prompt}"})
                else:
                    if not self.ref_image_path or not os.path.exists(self.ref_image_path):
                        err_msg = self.t("ref_missing")
                        Clock.schedule_once(lambda dt: self.on_error(err_msg, self.prompt), 0)
                        Clock.schedule_once(lambda dt: self.on_finished(), 0)
                        return
                    try:
                        with open(self.ref_image_path, "rb") as f:
                            b64 = base64.b64encode(f.read()).decode('utf-8')
                        messages.append({"role": "user", "content": [
                            {"type": "text", "text": f"Modify this image. Prompt: {self.prompt}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]})
                    except Exception as ref_err:
                        Clock.schedule_once(lambda dt: self.on_error(f"{self.t('ref_missing')}: {str(ref_err)}", self.prompt), 0)
                        Clock.schedule_once(lambda dt: self.on_finished(), 0)
                        return
                payload = {"model": self.model, "messages": messages, "size": api_size}

            log_data = {"timestamp": timestamp, "attempt": attempt, "request_url": api_url, "payload": payload}

            try:
                headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
                session = requests.Session()
                if self.proxy_url:
                    session.proxies = {"http": self.proxy_url, "https": self.proxy_url}
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
                    raise Exception(f"{self.t('extract_error')}: {json.dumps(res_data, ensure_ascii=False)}")

                Clock.schedule_once(lambda dt: self.on_status(self.t("processing")), 0)

                if img_base64:
                    img_bytes = base64.b64decode(img_base64)
                    if img_bytes[:8] == b'\x89PNG\r\n\x1a\n': ext = 'png'
                    elif img_bytes[:2] == b'\xff\xd8': ext = 'jpg'
                    elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP': ext = 'webp'
                    else: ext = 'png'
                    filename = f"gen_{timestamp}_{random_suffix}.{ext}"
                    save_path = os.path.join(self.image_out_dir, filename)
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
                    save_path = os.path.join(self.image_out_dir, filename)
                    with open(save_path, "wb") as f:
                        f.write(img_response.content)

                # Success
                Clock.schedule_once(lambda dt: self.on_success(save_path, self.prompt, self.model), 0)
                Clock.schedule_once(lambda dt: self.on_status(self.t("status_done")), 0)
                Clock.schedule_once(lambda dt: self.on_finished(), 0)
                return

            except requests.exceptions.HTTPError as http_err:
                try:
                    err_detail = response.json() if response else str(http_err)
                    err_msg = f"{self.t('http_error').format(response.status_code)}:\n{json.dumps(err_detail, ensure_ascii=False, indent=2)}"
                except:
                    err_msg = f"{self.t('net_error')}:\n{str(http_err)}"
                Clock.schedule_once(lambda dt: self.on_error(err_msg, self.prompt), 0)
                status_err = f"{self.t('status_error')} ({attempt}/{max_attempts})"
                Clock.schedule_once(lambda dt: self.on_status(status_err), 0)
            except Exception as e:
                err_msg = f"{self.t('exception')}:\n{str(e)}"
                Clock.schedule_once(lambda dt: self.on_error(err_msg, self.prompt), 0)
                status_err = f"{self.t('status_error')} ({attempt}/{max_attempts})"
                Clock.schedule_once(lambda dt: self.on_status(status_err), 0)
            finally:
                try:
                    with open(log_file_path, "w", encoding="utf-8") as lf:
                        json.dump(log_data, lf, ensure_ascii=False, indent=2)
                except:
                    pass

            if attempt < max_attempts:
                wait_msg = self.t("wait_retry").format(attempt, max_attempts)
                Clock.schedule_once(lambda dt: self.on_status(wait_msg), 0)
                time.sleep(2)

        Clock.schedule_once(lambda dt: self.on_status(self.t("retry_failed")), 0)
        Clock.schedule_once(lambda dt: self.on_finished(), 0)


class PromptProcessRunner:
    def __init__(self, api_url, token, model, prompt, task_type, proxy_url, on_status, on_error, on_success, on_finished):
        self.api_url = api_url
        self.token = token
        self.model = model
        self.prompt = prompt
        self.task_type = task_type
        self.proxy_url = proxy_url
        
        self.on_status = on_status
        self.on_error = on_error
        self.on_success = on_success
        self.on_finished = on_finished

    def start(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()

    def run(self):
        Clock.schedule_once(lambda dt: self.on_status("Connecting to AI..."), 0)
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
                session.proxies = {"http": self.proxy_url, "https": self.proxy_url}
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
                
                Clock.schedule_once(lambda dt: self.on_success(result), 0)
                Clock.schedule_once(lambda dt: self.on_status("Success"), 0)
            else:
                raise Exception("No choices returned from the chat completion API.")
        except Exception as e:
            Clock.schedule_once(lambda dt: self.on_error(str(e)), 0)
            Clock.schedule_once(lambda dt: self.on_status("Error"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.on_finished(), 0)

# ==========================================
# 3. Kivy Custom Widgets
# ==========================================
class NavButton(ButtonBehavior, BoxLayout):
    active = BooleanProperty(False)
    icon = StringProperty('')
    text = StringProperty('')

class HistoryItem(BoxLayout):
    status_color = ListProperty([0.18, 0.18, 0.18, 1])

class TemplateItem(BoxLayout):
    pass

class FileChooserPopup(Popup):
    def __init__(self, callback, title_text="Select File", **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = title_text
        self.size_hint = (0.95, 0.9)
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Starting directory
        if platform == 'android':
            start_path = '/storage/emulated/0'
            if not os.path.exists(start_path):
                start_path = '/sdcard'
        else:
            start_path = os.path.expanduser('~')
            
        if not os.path.exists(start_path):
            start_path = '.'
            
        self.filechooser = FileChooserIconView(
            path=start_path,
            filters=['*.png', '*.jpg', '*.jpeg', '*.webp', '*.PNG', '*.JPG', '*.JPEG', '*.WEBP']
        )
        layout.addWidget(self.filechooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height='45dp', spacing=10)
        btn_select = Button(text="Select", size_hint_x=0.5, background_color=(0.15, 0.35, 0.9, 1))
        btn_select.bind(on_release=self.select_file)
        btn_cancel = Button(text="Cancel", size_hint_x=0.5, background_color=(0.3, 0.3, 0.3, 1))
        btn_cancel.bind(on_release=self.dismiss)
        
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_cancel)
        layout.addWidget(btn_layout)
        
        self.content = layout
        
    def select_file(self, instance):
        if self.filechooser.selection:
            self.callback(self.filechooser.selection[0])
            self.dismiss()

class AddModelPopup(Popup):
    def __init__(self, callback, title_text="Add Model", prompt_text="Enter model name:", btn_text="Add", **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = title_text
        self.size_hint = (0.85, None)
        self.height = '180dp'
        
        layout = BoxLayout(orientation='vertical', spacing=8, padding=10)
        
        lbl = Label(text=prompt_text, size_hint_y=None, height='25dp', font_size='14sp', halign='left')
        self.txt_model = TextInput(multiline=False, size_hint_y=None, height='38dp', font_size='14sp', padding=[8, 8])
        
        btn_layout = BoxLayout(size_hint_y=None, height='40dp', spacing=10)
        btn_add = Button(text=btn_text, size_hint_x=0.5, background_color=(0.15, 0.35, 0.9, 1))
        btn_add.bind(on_release=self.submit_model)
        btn_cancel = Button(text="Cancel", size_hint_x=0.5, background_color=(0.3, 0.3, 0.3, 1))
        btn_cancel.bind(on_release=self.dismiss)
        
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_cancel)
        
        layout.addWidget(lbl)
        layout.addWidget(self.txt_model)
        layout.addWidget(btn_layout)
        
        self.content = layout
        
    def submit_model(self, instance):
        name = self.txt_model.text.strip()
        if name:
            self.callback(name)
            self.dismiss()

# ==========================================
# 4. App Screens
# ==========================================
class GenerateScreen(Screen):
    pass

class PromptAdvScreen(Screen):
    pass

class HistoryScreen(Screen):
    pass

class TemplatesScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

# ==========================================
# 5. Main Application Layout
# ==========================================
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Load active app instance
        self.app = App.get_running_app()
        
        # 1. Header Bar
        self.header = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp', padding=['10dp', '0dp', '10dp', '0dp'], spacing='10dp')
        with self.header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            Rectangle(pos=self.header.pos, size=self.header.size)
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[self.header.x, self.header.y, self.header.x + self.header.width, self.header.y], width=1)
            
        self.lbl_title = Label(text=self.app.t("title"), font_size='18sp', bold=True, color=(0.95, 0.95, 0.95, 1), size_hint_x=0.5, halign='left')
        self.lbl_title.bind(size=self.lbl_title.setter('text_size'))
        
        self.btn_lang = Button(text=self.app.t("btn_lang"), size_hint=(None, None), size=('65dp', '34dp'), pos_hint={'center_y': 0.5}, background_color=(0.25, 0.25, 0.25, 1))
        self.btn_lang.bind(on_release=self.app.toggle_language)
        
        self.header.addWidget(self.lbl_title)
        self.header.addWidget(self.btn_lang)
        self.add_widget(self.header)
        
        # Update title position
        self.header.bind(pos=self.update_header_canvas, size=self.update_header_canvas)
        
        # 2. Screen Manager
        self.screen_manager = ScreenManager()
        self.setup_screens()
        self.add_widget(self.screen_manager)
        
        # 3. Bottom Nav Bar
        self.navbar = BoxLayout(orientation='horizontal', size_hint_y=None, height='65dp', padding=['4dp', '4dp', '4dp', '4dp'], spacing='4dp')
        with self.navbar.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=self.navbar.pos, size=self.navbar.size)
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[self.navbar.x, self.navbar.y + self.navbar.height, self.navbar.x + self.navbar.width, self.navbar.y + self.navbar.height], width=1)
            
        self.navbar.bind(pos=self.update_navbar_canvas, size=self.update_navbar_canvas)
        
        self.btn_gen = NavButton(icon="🎨", text=self.app.t("nav_generate"), active=True)
        self.btn_gen.bind(on_release=lambda x: self.switch_screen('generate'))
        
        self.btn_adv = NavButton(icon="📝", text=self.app.t("nav_prompt_adv"))
        self.btn_adv.bind(on_release=lambda x: self.switch_screen('prompt_adv'))
        
        self.btn_hist = NavButton(icon="📜", text=self.app.t("nav_history"))
        self.btn_hist.bind(on_release=lambda x: self.switch_screen('history'))
        
        self.btn_tmpl = NavButton(icon="📁", text=self.app.t("nav_templates"))
        self.btn_tmpl.bind(on_release=lambda x: self.switch_screen('templates'))
        
        self.btn_sett = NavButton(icon="⚙️", text=self.app.t("nav_settings"))
        self.btn_sett.bind(on_release=lambda x: self.switch_screen('settings'))
        
        self.navbar.addWidget(self.btn_gen)
        self.navbar.addWidget(self.btn_adv)
        self.navbar.addWidget(self.btn_hist)
        self.navbar.addWidget(self.btn_tmpl)
        self.navbar.addWidget(self.btn_sett)
        self.add_widget(self.navbar)

    def update_header_canvas(self, *args):
        self.header.canvas.before.clear()
        with self.header.canvas.before:
            Color(0.12, 0.12, 0.12, 1)
            Rectangle(pos=self.header.pos, size=self.header.size)
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[self.header.x, self.header.y, self.header.x + self.header.width, self.header.y], width=1)

    def update_navbar_canvas(self, *args):
        self.navbar.canvas.before.clear()
        with self.navbar.canvas.before:
            Color(0.08, 0.08, 0.08, 1)
            Rectangle(pos=self.navbar.pos, size=self.navbar.size)
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[self.navbar.x, self.navbar.y + self.navbar.height, self.navbar.x + self.navbar.width, self.navbar.y + self.navbar.height], width=1)

    def setup_screens(self):
        # 1. Generate Screen
        self.gen_screen = GenerateScreen(name='generate')
        self.build_generate_screen()
        self.screen_manager.add_widget(self.gen_screen)
        
        # 2. Prompt Adv Screen
        self.adv_screen = PromptAdvScreen(name='prompt_adv')
        self.build_prompt_adv_screen()
        self.screen_manager.add_widget(self.adv_screen)
        
        # 3. History Screen
        self.hist_screen = HistoryScreen(name='history')
        self.build_history_screen()
        self.screen_manager.add_widget(self.hist_screen)
        
        # 4. Templates Screen
        self.tmpl_screen = TemplatesScreen(name='templates')
        self.build_templates_screen()
        self.screen_manager.add_widget(self.tmpl_screen)
        
        # 5. Settings Screen
        self.sett_screen = SettingsScreen(name='settings')
        self.build_settings_screen()
        self.screen_manager.add_widget(self.sett_screen)

    def switch_screen(self, screen_name):
        # Sync prompts if switching to Advanced
        if screen_name == 'prompt_adv':
            self.txt_adv_original.text = self.txt_prompt.text.strip()
            
        self.screen_manager.current = screen_name
        self.btn_gen.active = (screen_name == 'generate')
        self.btn_adv.active = (screen_name == 'prompt_adv')
        self.btn_hist.active = (screen_name == 'history')
        self.btn_tmpl.active = (screen_name == 'templates')
        self.btn_sett.active = (screen_name == 'settings')

    def update_retranslated_texts(self):
        self.lbl_title.text = self.app.t("title")
        self.btn_lang.text = self.app.t("btn_lang")
        
        # Navbar
        self.btn_gen.text = self.app.t("nav_generate")
        self.btn_adv.text = self.app.t("nav_prompt_adv")
        self.btn_hist.text = self.app.t("nav_history")
        self.btn_tmpl.text = self.app.t("nav_templates")
        self.btn_sett.text = self.app.t("nav_settings")
        
        # Generate Screen
        self.lbl_result_title.text = self.app.t("result_title")
        if not self.app.current_result_image:
            self.lbl_result_placeholder.text = self.app.t("result_waiting")
        self.lbl_ref_title.text = self.app.t("ref_title")
        if not self.app.ref_image_path:
            self.lbl_ref_placeholder.text = self.app.t("ref_none")
            self.lbl_mode.text = self.app.t("mode_txt2img")
        else:
            self.lbl_mode.text = self.app.t("mode_img2img")
        self.btn_select_ref.text = self.app.t("btn_select_ref")
        self.btn_clear_ref.text = self.app.t("clear_ref")
        
        self.lbl_model_lbl.text = self.app.t("model_label")
        self.btn_add_model.text = self.app.t("add_model_btn")
        self.lbl_prompt_lbl.text = self.app.t("prompt_group")
        self.txt_prompt.hint_text = self.app.t("prompt_placeholder")
        self.btn_trans.text = self.app.t("btn_translate")
        
        self.lbl_size_lbl.text = self.app.t("size_label")
        self.lbl_quality_lbl.text = self.app.t("quality_label")
        
        self.btn_generate.text = self.app.t("btn_generate")
        if not self.app.is_generating:
            self.lbl_status.text = self.app.t("status_ready")
            self.lbl_timer.text = self.app.t("elapsed").format(0)
            
        # Advanced Screen
        self.lbl_adv_original_lbl.text = self.app.t("prompt_original_label")
        self.txt_adv_original.hint_text = self.app.t("prompt_original_placeholder")
        self.lbl_adv_optimized_lbl.text = self.app.t("prompt_optimized_label")
        self.txt_adv_optimized.hint_text = self.app.t("prompt_optimized_placeholder")
        self.btn_adv_trans.text = self.app.t("btn_adv_translate")
        self.btn_adv_opt.text = self.app.t("btn_adv_optimize")
        self.btn_adv_apply.text = self.app.t("btn_adv_apply")
        if not self.app.is_prompt_processing:
            self.lbl_adv_status.text = self.app.t("status_ready")
            
        # History Screen
        self.btn_clear_hist.text = self.app.t("btn_clear_history")
        self.refresh_history_ui()
        
        # Templates Screen
        self.btn_save_tpl.text = self.app.t("btn_save_template")
        self.refresh_templates_ui()
        
        # Settings Screen
        self.lbl_api_group.text = self.app.t("api_group")
        self.lbl_sett_img_path.text = self.app.t("image_path")
        self.lbl_sett_chat_path.text = self.app.t("chat_path")
        self.lbl_sett_token.text = self.app.t("api_token")
        
        self.lbl_app_group.text = self.app.t("settings_title")
        self.lbl_sett_proxy.text = self.app.t("proxy_label")
        self.txt_sett_proxy.placeholder_text = self.app.t("proxy_placeholder")
        self.lbl_sett_retry.text = self.app.t("retry_group")
        self.chk_retry_lbl.text = self.app.t("retry_enable")
        self.lbl_retry_count_lbl.text = self.app.t("retry_count")

    # ==========================================
    # Tab 1: Generate UI
    # ==========================================
    def build_generate_screen(self):
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', spacing='12dp', padding='12dp', size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        # 1. Result Image Card
        res_card = BoxLayout(orientation='vertical', size_hint_y=None, height='280dp', padding='6dp', spacing='4dp')
        with res_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=res_card.pos, size=res_card.size, radius=[10])
        res_card.bind(pos=self.app.create_canvas_callback(res_card, 0.16, 10), size=self.app.create_canvas_callback(res_card, 0.16, 10))
        
        self.lbl_result_title = Label(text=self.app.t("result_title"), size_hint_y=None, height='20dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_result_title.bind(size=self.lbl_result_title.setter('text_size'))
        
        self.img_result = Image(allow_stretch=True, keep_ratio=True, size_hint_y=0.001)
        self.lbl_result_placeholder = Label(text=self.app.t("result_waiting"), font_size='14sp', color=(0.5, 0.5, 0.5, 1), halign='center', valign='middle')
        self.lbl_result_placeholder.bind(size=self.lbl_result_placeholder.setter('text_size'))
        
        res_card.addWidget(self.lbl_result_title)
        res_card.addWidget(self.img_result)
        res_card.addWidget(self.lbl_result_placeholder)
        container.addWidget(res_card)
        
        # 2. Reference Image Card
        ref_card = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', padding='8dp', spacing='6dp')
        with ref_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=ref_card.pos, size=ref_card.size, radius=[10])
        ref_card.bind(pos=self.app.create_canvas_callback(ref_card, 0.16, 10), size=self.app.create_canvas_callback(ref_card, 0.16, 10))
        
        self.lbl_ref_title = Label(text=self.app.t("ref_title"), size_hint_y=None, height='18dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_ref_title.bind(size=self.lbl_ref_title.setter('text_size'))
        
        ref_body = BoxLayout(orientation='horizontal', spacing='10dp')
        self.img_ref = Image(allow_stretch=True, keep_ratio=True, size_hint_x=None, width='80dp')
        self.lbl_ref_placeholder = Label(text=self.app.t("ref_none"), font_size='12sp', color=(0.5, 0.5, 0.5, 1), halign='left', valign='middle')
        self.lbl_ref_placeholder.bind(size=self.lbl_ref_placeholder.setter('text_size'))
        
        ref_btns = BoxLayout(orientation='vertical', spacing='5dp', size_hint_x=None, width='120dp')
        self.btn_select_ref = Button(text=self.app.t("btn_select_ref"), size_hint_y=0.5, font_size='12sp', background_color=(0.25, 0.25, 0.25, 1))
        self.btn_select_ref.bind(on_release=self.select_reference_image)
        self.btn_clear_ref = Button(text=self.app.t("clear_ref"), size_hint_y=0.5, font_size='12sp', background_color=(0.4, 0.15, 0.15, 1))
        self.btn_clear_ref.bind(on_release=self.clear_reference_image)
        ref_btns.addWidget(self.btn_select_ref)
        ref_btns.addWidget(self.btn_clear_ref)
        
        ref_body.addWidget(self.img_ref)
        ref_body.addWidget(self.lbl_ref_placeholder)
        ref_body.addWidget(ref_btns)
        
        ref_card.addWidget(self.lbl_ref_title)
        ref_card.addWidget(ref_body)
        container.addWidget(ref_card)
        
        # 3. Model Selector Card
        model_card = BoxLayout(orientation='vertical', size_hint_y=None, height='85dp', padding='10dp', spacing='6dp')
        with model_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=model_card.pos, size=model_card.size, radius=[10])
        model_card.bind(pos=self.app.create_canvas_callback(model_card, 0.16, 10), size=self.app.create_canvas_callback(model_card, 0.16, 10))
        
        self.lbl_model_lbl = Label(text=self.app.t("model_label"), size_hint_y=None, height='18dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_model_lbl.bind(size=self.lbl_model_lbl.setter('text_size'))
        
        model_row = BoxLayout(orientation='horizontal', spacing='8dp', size_hint_y=None, height='42dp')
        self.sp_model = Spinner(text=self.app.config_data["LAST_USED_MODEL"], values=self.app.config_data["MODEL_HISTORY"], font_size='14sp')
        with self.sp_model.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            RoundedRectangle(pos=self.sp_model.pos, size=self.sp_model.size, radius=[6])
        self.sp_model.bind(pos=self.app.create_canvas_callback(self.sp_model, 0.2, 6), size=self.app.create_canvas_callback(self.sp_model, 0.2, 6))
        
        self.btn_add_model = Button(text=self.app.t("add_model_btn"), size_hint_x=None, width='90dp', font_size='12sp', background_color=(0.15, 0.35, 0.9, 1))
        self.btn_add_model.bind(on_release=self.show_add_model_popup)
        
        model_row.addWidget(self.sp_model)
        model_row.addWidget(self.btn_add_model)
        model_card.addWidget(self.lbl_model_lbl)
        model_card.addWidget(model_row)
        container.addWidget(model_card)
        
        # 4. Prompt Input Card
        prompt_card = BoxLayout(orientation='vertical', size_hint_y=None, height='175dp', padding='10dp', spacing='6dp')
        with prompt_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=prompt_card.pos, size=prompt_card.size, radius=[10])
        prompt_card.bind(pos=self.app.create_canvas_callback(prompt_card, 0.16, 10), size=self.app.create_canvas_callback(prompt_card, 0.16, 10))
        
        self.lbl_prompt_lbl = Label(text=self.app.t("prompt_group"), size_hint_y=None, height='18dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_prompt_lbl.bind(size=self.lbl_prompt_lbl.setter('text_size'))
        
        self.txt_prompt = Factory.StyledTextInput(multiline=True, size_hint_y=None, height='95dp', hint_text=self.app.t("prompt_placeholder"))
        
        self.btn_trans = Button(text=self.app.t("btn_translate"), size_hint_y=None, height='32dp', font_size='12sp', background_color=(0.25, 0.25, 0.25, 1))
        self.btn_trans.bind(on_release=self.local_translate_prompt)
        
        prompt_card.addWidget(self.lbl_prompt_lbl)
        prompt_card.addWidget(self.txt_prompt)
        prompt_card.addWidget(self.btn_trans)
        container.addWidget(prompt_card)
        
        # 5. Parameters Card
        param_card = BoxLayout(orientation='vertical', size_hint_y=None, height='115dp', padding='10dp', spacing='6dp')
        with param_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=param_card.pos, size=param_card.size, radius=[10])
        param_card.bind(pos=self.app.create_canvas_callback(param_card, 0.16, 10), size=self.app.create_canvas_callback(param_card, 0.16, 10))
        
        grid = GridLayout(cols=2, spacing='10dp')
        self.lbl_size_lbl = Label(text=self.app.t("size_label"), font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign='left')
        self.lbl_size_lbl.bind(size=self.lbl_size_lbl.setter('text_size'))
        
        size_choices = [
            self.app.t("size_auto"),
            self.app.t("size_square"),
            self.app.t("size_landscape"),
            self.app.t("size_portrait"),
            self.app.t("size_2k_square"),
            self.app.t("size_2k_landscape"),
            self.app.t("size_2k_portrait"),
            self.app.t("size_4k_landscape"),
            self.app.t("size_4k_portrait")
        ]
        self.sp_size = Spinner(text=size_choices[0], values=size_choices, font_size='13sp')
        with self.sp_size.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            RoundedRectangle(pos=self.sp_size.pos, size=self.sp_size.size, radius=[6])
        self.sp_size.bind(pos=self.app.create_canvas_callback(self.sp_size, 0.2, 6), size=self.app.create_canvas_callback(self.sp_size, 0.2, 6))
        
        self.lbl_quality_lbl = Label(text=self.app.t("quality_label"), font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign='left')
        self.lbl_quality_lbl.bind(size=self.lbl_quality_lbl.setter('text_size'))
        
        self.sp_quality = Spinner(text=self.app.config_data.get("DEFAULT_QUALITY", "low"), values=DEFAULT_QUALITIES, font_size='13sp')
        with self.sp_quality.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            RoundedRectangle(pos=self.sp_quality.pos, size=self.sp_quality.size, radius=[6])
        self.sp_quality.bind(pos=self.app.create_canvas_callback(self.sp_quality, 0.2, 6), size=self.app.create_canvas_callback(self.sp_quality, 0.2, 6))
        
        grid.addWidget(self.lbl_size_lbl)
        grid.addWidget(self.sp_size)
        grid.addWidget(self.lbl_quality_lbl)
        grid.addWidget(self.sp_quality)
        
        param_card.addWidget(grid)
        container.addWidget(param_card)
        
        # 6. Run Card
        run_card = BoxLayout(orientation='vertical', size_hint_y=None, height='150dp', padding='10dp', spacing='8dp')
        with run_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=run_card.pos, size=run_card.size, radius=[10])
        run_card.bind(pos=self.app.create_canvas_callback(run_card, 0.16, 10), size=self.app.create_canvas_callback(run_card, 0.16, 10))
        
        self.btn_generate = Factory.StyledButton(text=self.app.t("btn_generate"))
        self.btn_generate.bind(on_release=self.start_generation)
        
        self.lbl_mode = Label(text=self.app.t("mode_txt2img"), font_size='12sp', color=(0.5, 0.5, 0.5, 1), italic=True)
        self.lbl_status = Label(text=self.app.t("status_ready"), font_size='14sp', bold=True, color=(0.1, 0.8, 0.1, 1))
        self.lbl_timer = Label(text=self.app.t("elapsed").format(0), font_size='12sp', color=(0.6, 0.6, 0.6, 1), italic=True)
        
        run_card.addWidget(self.btn_generate)
        run_card.addWidget(self.lbl_mode)
        run_card.addWidget(self.lbl_status)
        run_card.addWidget(self.lbl_timer)
        container.addWidget(run_card)
        
        scroll.add_widget(container)
        self.gen_screen.add_widget(scroll)

    def show_add_model_popup(self, instance):
        popup = AddModelPopup(
            callback=self.add_model_to_history,
            title_text=self.app.t("add_model_title"),
            prompt_text=self.app.t("add_model_prompt"),
            btn_text=self.app.t("add_model_btn")
        )
        popup.open()

    def add_model_to_history(self, name):
        if name not in self.app.config_data["MODEL_HISTORY"]:
            self.app.config_data["MODEL_HISTORY"].append(name)
            self.sp_model.values = self.app.config_data["MODEL_HISTORY"]
        self.sp_model.text = name
        self.app.config_data["LAST_USED_MODEL"] = name
        self.app.save_config()

    def select_reference_image(self, instance):
        popup = FileChooserPopup(callback=self.set_reference_image, title_text=self.app.t("select_ref_title"))
        popup.open()

    def set_reference_image(self, path):
        if path and os.path.exists(path):
            self.app.ref_image_path = path
            self.img_ref.source = path
            self.lbl_ref_placeholder.text = os.path.basename(path)
            self.lbl_mode.text = self.app.t("mode_img2img")
            self.lbl_mode.color = (0.2, 0.5, 0.9, 1)

    def clear_reference_image(self, instance):
        self.app.ref_image_path = ""
        self.img_ref.source = ""
        self.lbl_ref_placeholder.text = self.app.t("ref_none")
        self.lbl_mode.text = self.app.t("mode_txt2img")
        self.lbl_mode.color = (0.5, 0.5, 0.5, 1)

    def local_translate_prompt(self, instance):
        text = self.txt_prompt.text.strip()
        if not text:
            return
        result = text
        for zh, en in sorted(TRANSLATE_DICT.items(), key=lambda x: -len(x[0])):
            result = result.replace(zh, en)
        self.txt_prompt.text = result

    def start_generation(self, instance):
        if self.app.is_generating:
            return
            
        prompt = self.txt_prompt.text.strip()
        if not prompt:
            self.lbl_status.text = self.app.t("status_blocked")
            self.lbl_result_placeholder.text = self.app.t("empty_prompt")
            return
            
        token = self.app.config_data.get("DEFAULT_API_TOKEN", "").strip()
        if not token:
            self.lbl_status.text = self.app.t("status_blocked")
            self.lbl_result_placeholder.text = self.app.t("empty_token")
            return
            
        self.app.is_generating = True
        self.btn_generate.disabled = True
        self.btn_select_ref.disabled = True
        self.btn_clear_ref.disabled = True
        
        self.app.generation_start_time = time.time()
        self.lbl_status.text = self.app.t("sending").format(1, 1)
        self.lbl_timer.text = self.app.t("elapsed").format(0)
        
        self.app.timer_trigger = Clock.schedule_interval(self.update_timer, 1.0)
        
        # Save config values
        model = self.sp_model.text
        quality = self.sp_quality.text
        self.app.config_data["LAST_USED_MODEL"] = model
        self.app.config_data["DEFAULT_QUALITY"] = quality
        self.app.save_config()
        
        mode = "image" if self.app.ref_image_path else "text"
        size = self.sp_size.text
        
        # Start Runner
        runner = ImageGenerateRunner(
            mode=mode,
            image_api_url=self.app.config_data["IMAGE_API_URL"],
            chat_api_url=self.app.config_data["CHAT_API_URL"],
            token=token,
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            ref_image_path=self.app.ref_image_path if mode == "image" else None,
            auto_retry=self.app.config_data["AUTO_RETRY"],
            retry_count=self.app.config_data["RETRY_COUNT"],
            proxy_url=self.app.config_data["PROXY_URL"],
            log_dir=self.app.log_dir,
            image_out_dir=self.app.image_out_dir,
            on_status=self.set_generation_status,
            on_error=self.handle_generation_error,
            on_success=self.handle_generation_success,
            on_finished=self.generation_finished,
            translate_func=self.app.t
        )
        runner.start()

    def set_generation_status(self, text):
        self.lbl_status.text = text

    def handle_generation_error(self, err, prompt):
        self.img_result.source = ""
        self.img_result.size_hint_y = 0.001
        self.lbl_result_placeholder.text = err
        self.lbl_result_placeholder.size_hint_y = 1
        self.app.add_history_entry(prompt, self.sp_model.text, "failed", "")

    def handle_generation_success(self, path, prompt, model):
        self.app.current_result_image = path
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        self.img_result.source = path
        self.img_result.size_hint_y = 1
        self.lbl_result_placeholder.text = ""
        self.lbl_result_placeholder.size_hint_y = 0.001
        self.app.add_history_entry(prompt, model, "success", path)

    def update_timer(self, dt):
        elapsed = int(time.time() - self.app.generation_start_time)
        self.lbl_timer.text = self.app.t("elapsed").format(elapsed)

    def generation_finished(self):
        if self.app.timer_trigger:
            self.app.timer_trigger.cancel()
            self.app.timer_trigger = None
        self.app.is_generating = False
        self.btn_generate.disabled = False
        self.btn_select_ref.disabled = False
        self.btn_clear_ref.disabled = False

    def load_result_image(self, path):
        self.app.current_result_image = path
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        self.img_result.source = path
        self.img_result.size_hint_y = 1
        self.lbl_result_placeholder.text = ""
        self.lbl_result_placeholder.size_hint_y = 0.001

    def set_main_prompt(self, text):
        self.txt_prompt.text = text

    # ==========================================
    # Tab 2: Prompt Advanced UI
    # ==========================================
    def build_prompt_adv_screen(self):
        container = BoxLayout(orientation='vertical', spacing='12dp', padding='12dp')
        
        # 1. Original Prompt Card
        orig_card = BoxLayout(orientation='vertical', spacing='6dp', size_hint_y=0.45, padding='10dp')
        with orig_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=orig_card.pos, size=orig_card.size, radius=[10])
        orig_card.bind(pos=self.app.create_canvas_callback(orig_card, 0.16, 10), size=self.app.create_canvas_callback(orig_card, 0.16, 10))
        
        self.lbl_adv_original_lbl = Label(text=self.app.t("prompt_original_label"), size_hint_y=None, height='18dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_adv_original_lbl.bind(size=self.lbl_adv_original_lbl.setter('text_size'))
        
        self.txt_adv_original = Factory.StyledTextInput(multiline=True, hint_text=self.app.t("prompt_original_placeholder"))
        
        orig_card.addWidget(self.lbl_adv_original_lbl)
        orig_card.addWidget(self.txt_adv_original)
        container.addWidget(orig_card)
        
        # 2. Optimized Prompt Card
        opt_card = BoxLayout(orientation='vertical', spacing='6dp', size_hint_y=0.45, padding='10dp')
        with opt_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=opt_card.pos, size=opt_card.size, radius=[10])
        opt_card.bind(pos=self.app.create_canvas_callback(opt_card, 0.16, 10), size=self.app.create_canvas_callback(opt_card, 0.16, 10))
        
        self.lbl_adv_optimized_lbl = Label(text=self.app.t("prompt_optimized_label"), size_hint_y=None, height='18dp', font_size='13sp', color=(0.7, 0.7, 0.7, 1), halign='left')
        self.lbl_adv_optimized_lbl.bind(size=self.lbl_adv_optimized_lbl.setter('text_size'))
        
        self.txt_adv_optimized = Factory.StyledTextInput(multiline=True, hint_text=self.app.t("prompt_optimized_placeholder"))
        
        opt_card.addWidget(self.lbl_adv_optimized_lbl)
        opt_card.addWidget(self.txt_adv_optimized)
        container.addWidget(opt_card)
        
        # 3. Actions Row
        actions_card = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', spacing='8dp', padding='6dp')
        with actions_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=actions_card.pos, size=actions_card.size, radius=[10])
        actions_card.bind(pos=self.app.create_canvas_callback(actions_card, 0.16, 10), size=self.app.create_canvas_callback(actions_card, 0.16, 10))
        
        row1 = BoxLayout(orientation='horizontal', spacing='8dp', size_hint_y=None, height='40dp')
        self.btn_adv_trans = Button(text=self.app.t("btn_adv_translate"), size_hint_x=0.5, font_size='12sp', background_color=(0.25, 0.25, 0.25, 1))
        self.btn_adv_trans.bind(on_release=self.run_ai_translate)
        
        self.btn_adv_opt = Button(text=self.app.t("btn_adv_optimize"), size_hint_x=0.5, font_size='12sp', background_color=(0.25, 0.25, 0.25, 1))
        self.btn_adv_opt.bind(on_release=self.run_ai_optimize)
        row1.addWidget(self.btn_adv_trans)
        row1.addWidget(self.btn_adv_opt)
        
        self.btn_adv_apply = Factory.StyledButton(text=self.app.t("btn_adv_apply"), size_hint_y=None, height='40dp')
        self.btn_adv_apply.bind(on_release=self.apply_adv_prompt)
        
        self.lbl_adv_status = Label(text=self.app.t("status_ready"), font_size='13sp', bold=True, color=(0.1, 0.8, 0.1, 1), size_hint_y=None, height='20dp')
        
        actions_card.addWidget(row1)
        actions_card.addWidget(self.btn_adv_apply)
        actions_card.addWidget(self.lbl_adv_status)
        container.addWidget(actions_card)
        
        self.adv_screen.add_widget(container)

    def run_ai_translate(self, instance):
        self.run_ai_prompt_task("translate")

    def run_ai_optimize(self, instance):
        self.run_ai_prompt_task("optimize")

    def run_ai_prompt_task(self, task_type):
        if self.app.is_prompt_processing:
            return
            
        original = self.txt_adv_original.text.strip()
        if not original:
            return
            
        token = self.app.config_data.get("DEFAULT_API_TOKEN", "").strip()
        if not token:
            self.lbl_adv_status.text = self.app.t("empty_token")
            self.lbl_adv_status.color = (0.9, 0.1, 0.1, 1)
            return
            
        self.app.is_prompt_processing = True
        self.btn_adv_trans.disabled = True
        self.btn_adv_opt.disabled = True
        self.btn_adv_apply.disabled = True
        
        if task_type == "translate":
            self.lbl_adv_status.text = self.app.t("adv_status_translating")
        else:
            self.lbl_adv_status.text = self.app.t("adv_status_optimizing")
        self.lbl_adv_status.color = (0.9, 0.6, 0.1, 1)
        
        model = self.sp_model.text
        
        runner = PromptProcessRunner(
            api_url=self.app.config_data["CHAT_API_URL"],
            token=token,
            model=model,
            prompt=original,
            task_type=task_type,
            proxy_url=self.app.config_data["PROXY_URL"],
            on_status=self.set_adv_status_text,
            on_error=self.handle_adv_error,
            on_success=self.handle_adv_success,
            on_finished=self.adv_task_finished
        )
        runner.start()

    def set_adv_status_text(self, text):
        self.lbl_adv_status.text = text

    def handle_adv_error(self, err):
        self.txt_adv_optimized.text = f"Error:\n{err}"
        self.lbl_adv_status.text = self.app.t("status_error")
        self.lbl_adv_status.color = (0.9, 0.1, 0.1, 1)

    def handle_adv_success(self, result):
        self.txt_adv_optimized.text = result
        self.lbl_adv_status.text = self.app.t("status_done")
        self.lbl_adv_status.color = (0.1, 0.8, 0.1, 1)

    def adv_task_finished(self):
        self.app.is_prompt_processing = False
        self.btn_adv_trans.disabled = False
        self.btn_adv_opt.disabled = False
        self.btn_adv_apply.disabled = False

    def apply_adv_prompt(self, instance):
        optimized = self.txt_adv_optimized.text.strip()
        if optimized and not optimized.startswith("Error:"):
            self.set_main_prompt(optimized)
            self.switch_screen('generate')

    # ==========================================
    # Tab 3: History UI
    # ==========================================
    def build_history_screen(self):
        layout = BoxLayout(orientation='vertical', spacing='10dp', padding='12dp')
        
        self.history_scroll = ScrollView()
        self.history_container = BoxLayout(orientation='vertical', spacing='8dp', size_hint_y=None)
        self.history_container.bind(minimum_height=self.history_container.setter('height'))
        
        self.history_scroll.add_widget(self.history_container)
        
        self.btn_clear_hist = Factory.DangerButton(text=self.app.t("btn_clear_history"))
        self.btn_clear_hist.bind(on_release=self.confirm_clear_history)
        
        layout.addWidget(self.history_scroll)
        layout.addWidget(self.btn_clear_hist)
        self.hist_screen.add_widget(layout)
        
        self.refresh_history_ui()

    def refresh_history_ui(self):
        self.history_container.clear_widgets()
        if not self.app.history_data:
            lbl = Label(text=self.app.t("history_empty"), font_size='14sp', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height='50dp')
            self.history_container.add_widget(lbl)
            return
            
        for entry in self.app.history_data:
            item = HistoryItem()
            
            status_text = self.app.t("history_success") if entry.get("status") == "success" else self.app.t("history_failed")
            item.ids.lbl_time_status.text = f"[{entry.get('time', '')}] {status_text}"
            item.ids.lbl_model.text = entry.get('model', '')
            item.ids.lbl_prompt.text = entry.get('prompt', '')
            
            img_path = entry.get('image', '')
            if entry.get("status") == "success" and img_path and os.path.exists(img_path):
                item.ids.img_thumb.source = img_path
                item.ids.img_thumb.size_hint_x = None
                item.ids.img_thumb.width = '60dp'
                item.status_color = [0.15, 0.25, 0.15, 1]
                item.ids.btn_view.bind(on_release=lambda x, p=img_path: [self.load_result_image(p), self.switch_screen('generate')])
            else:
                item.ids.img_thumb.size_hint_x = None
                item.ids.img_thumb.width = '0.001dp'
                item.ids.img_thumb.opacity = 0
                item.status_color = [0.25, 0.15, 0.15, 1]
                item.ids.btn_view.disabled = True
                
            item.ids.btn_reuse.bind(on_release=lambda x, pr=entry.get('prompt', ''): [self.set_main_prompt(pr), self.switch_screen('generate')])
            
            self.history_container.add_widget(item)

    def confirm_clear_history(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        lbl = Label(text=self.app.t("confirm_clear"), font_size='14sp')
        btns = BoxLayout(spacing=10, size_hint_y=None, height='40dp')
        
        popup = Popup(title=self.app.t("confirm_title"), content=content, size_hint=(0.8, None), height='150dp')
        
        btn_yes = Button(text="Yes", size_hint_x=0.5, background_color=(0.75, 0.15, 0.15, 1))
        btn_yes.bind(on_release=lambda x: [self.clear_history_data(), popup.dismiss()])
        btn_no = Button(text="No", size_hint_x=0.5, background_color=(0.3, 0.3, 0.3, 1))
        btn_no.bind(on_release=popup.dismiss)
        
        btns.addWidget(btn_yes)
        btns.addWidget(btn_no)
        content.addWidget(lbl)
        content.addWidget(btns)
        popup.open()

    def clear_history_data(self):
        self.app.history_data.clear()
        self.app.save_json_file(self.app.history_file, self.app.history_data)
        self.refresh_history_ui()

    # ==========================================
    # Tab 4: Templates UI
    # ==========================================
    def build_templates_screen(self):
        layout = BoxLayout(orientation='vertical', spacing='10dp', padding='12dp')
        
        self.tmpl_scroll = ScrollView()
        self.tmpl_container = BoxLayout(orientation='vertical', spacing='8dp', size_hint_y=None)
        self.tmpl_container.bind(minimum_height=self.tmpl_container.setter('height'))
        
        self.tmpl_scroll.add_widget(self.tmpl_container)
        
        self.btn_save_tpl = Factory.StyledButton(text=self.app.t("btn_save_template"))
        self.btn_save_tpl.bind(on_release=self.show_save_template_popup)
        
        layout.addWidget(self.tmpl_scroll)
        layout.addWidget(self.btn_save_tpl)
        self.tmpl_screen.add_widget(layout)
        
        self.refresh_templates_ui()

    def refresh_templates_ui(self):
        self.tmpl_container.clear_widgets()
        if not self.app.templates_data:
            lbl = Label(text=self.app.t("history_empty"), font_size='14sp', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height='50dp')
            self.tmpl_container.add_widget(lbl)
            return
            
        for index, entry in enumerate(self.app.templates_data):
            item = TemplateItem()
            item.ids.lbl_name.text = entry.get('name', '')
            item.ids.lbl_prompt.text = entry.get('prompt', '')
            
            item.ids.btn_load.bind(on_release=lambda x, p=entry.get('prompt', ''): [self.set_main_prompt(p), self.switch_screen('generate')])
            item.ids.btn_delete.bind(on_release=lambda x, idx=index: self.delete_template_entry(idx))
            
            self.tmpl_container.add_widget(item)

    def show_save_template_popup(self, instance):
        prompt_text = self.txt_prompt.text.strip()
        if not prompt_text:
            return
            
        popup = AddModelPopup(
            callback=self.save_template_entry,
            title_text=self.app.t("template_title"),
            prompt_text=self.app.t("template_name"),
            btn_text="Save"
        )
        popup.open()

    def save_template_entry(self, name):
        prompt_text = self.txt_prompt.text.strip()
        if prompt_text and name:
            self.app.templates_data.append({"name": name, "prompt": prompt_text})
            self.app.save_json_file(self.app.templates_file, self.app.templates_data)
            self.refresh_templates_ui()

    def delete_template_entry(self, index):
        if 0 <= index < len(self.app.templates_data):
            self.app.templates_data.pop(index)
            self.app.save_json_file(self.app.templates_file, self.app.templates_data)
            self.refresh_templates_ui()

    # ==========================================
    # Tab 5: Settings UI
    # ==========================================
    def build_settings_screen(self):
        scroll = ScrollView()
        container = BoxLayout(orientation='vertical', spacing='12dp', padding='12dp', size_hint_y=None)
        container.bind(minimum_height=container.setter('height'))
        
        # 1. API Configuration Group
        api_card = BoxLayout(orientation='vertical', spacing='8dp', padding='12dp', size_hint_y=None)
        with api_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=api_card.pos, size=api_card.size, radius=[10])
        api_card.bind(pos=self.app.create_canvas_callback(api_card, 0.16, 10), size=self.app.create_canvas_callback(api_card, 0.16, 10))
        
        self.lbl_api_group = Label(text=self.app.t("api_group"), font_size='14sp', bold=True, size_hint_y=None, height='20dp', color=(0.95, 0.95, 0.95, 1))
        
        self.lbl_sett_img_path = Label(text=self.app.t("image_path"), font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height='18dp', halign='left')
        self.lbl_sett_img_path.bind(size=self.lbl_sett_img_path.setter('text_size'))
        self.txt_sett_img_path = Factory.StyledTextInput(text=self.app.config_data["IMAGE_API_URL"], multiline=False, size_hint_y=None, height='40dp')
        self.txt_sett_img_path.bind(text=self.save_api_settings)
        
        self.lbl_sett_chat_path = Label(text=self.app.t("chat_path"), font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height='18dp', halign='left')
        self.lbl_sett_chat_path.bind(size=self.lbl_sett_chat_path.setter('text_size'))
        self.txt_sett_chat_path = Factory.StyledTextInput(text=self.app.config_data["CHAT_API_URL"], multiline=False, size_hint_y=None, height='40dp')
        self.txt_sett_chat_path.bind(text=self.save_api_settings)
        
        self.lbl_sett_token = Label(text=self.app.t("api_token"), font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height='18dp', halign='left')
        self.lbl_sett_token.bind(size=self.lbl_sett_token.setter('text_size'))
        self.txt_sett_token = Factory.StyledTextInput(text=self.app.config_data["DEFAULT_API_TOKEN"], password=True, multiline=False, size_hint_y=None, height='40dp')
        self.txt_sett_token.bind(text=self.save_api_settings)
        
        api_card.add_widget(self.lbl_api_group)
        api_card.add_widget(self.lbl_sett_img_path)
        api_card.add_widget(self.txt_sett_img_path)
        api_card.add_widget(self.lbl_sett_chat_path)
        api_card.add_widget(self.txt_sett_chat_path)
        api_card.add_widget(self.lbl_sett_token)
        api_card.add_widget(self.txt_sett_token)
        
        api_card.height = '280dp'
        container.addWidget(api_card)
        
        # 2. General Settings Group
        app_card = BoxLayout(orientation='vertical', spacing='8dp', padding='12dp', size_hint_y=None)
        with app_card.canvas.before:
            Color(0.16, 0.16, 0.16, 1)
            RoundedRectangle(pos=app_card.pos, size=app_card.size, radius=[10])
        app_card.bind(pos=self.app.create_canvas_callback(app_card, 0.16, 10), size=self.app.create_canvas_callback(app_card, 0.16, 10))
        
        self.lbl_app_group = Label(text=self.app.t("settings_title"), font_size='14sp', bold=True, size_hint_y=None, height='20dp', color=(0.95, 0.95, 0.95, 1))
        
        self.lbl_sett_proxy = Label(text=self.app.t("proxy_label"), font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height='18dp', halign='left')
        self.lbl_sett_proxy.bind(size=self.lbl_sett_proxy.setter('text_size'))
        self.txt_sett_proxy = Factory.StyledTextInput(text=self.app.config_data["PROXY_URL"], multiline=False, size_hint_y=None, height='40dp', placeholder_text=self.app.t("proxy_placeholder"))
        self.txt_sett_proxy.bind(text=self.save_general_settings)
        
        self.lbl_sett_retry = Label(text=self.app.t("retry_group"), font_size='13sp', color=(0.8, 0.8, 0.8, 1), size_hint_y=None, height='18dp', halign='left')
        self.lbl_sett_retry.bind(size=self.lbl_sett_retry.setter('text_size'))
        
        retry_row = BoxLayout(orientation='horizontal', size_hint_y=None, height='40dp', spacing='10dp')
        self.chk_retry = CheckBox(active=self.app.config_data.get("AUTO_RETRY", False), size_hint_x=None, width='40dp')
        self.chk_retry.bind(active=self.save_general_settings)
        self.chk_retry_lbl = Label(text=self.app.t("retry_enable"), font_size='13sp', color=(0.9, 0.9, 0.9, 1), halign='left')
        self.chk_retry_lbl.bind(size=self.chk_retry_lbl.setter('text_size'))
        
        self.lbl_retry_count_lbl = Label(text=self.app.t("retry_count"), font_size='13sp', color=(0.9, 0.9, 0.9, 1), size_hint_x=None, width='70dp')
        self.txt_retry_count = Factory.StyledTextInput(text=str(self.app.config_data.get("RETRY_COUNT", 3)), input_filter='int', multiline=False, size_hint_x=None, width='55dp')
        self.txt_retry_count.bind(text=self.save_general_settings)
        
        retry_row.addWidget(self.chk_retry)
        retry_row.addWidget(self.chk_retry_lbl)
        retry_row.addWidget(self.lbl_retry_count_lbl)
        retry_row.addWidget(self.txt_retry_count)
        
        app_card.add_widget(self.lbl_app_group)
        app_card.add_widget(self.lbl_sett_proxy)
        app_card.add_widget(self.txt_sett_proxy)
        app_card.add_widget(self.lbl_sett_retry)
        app_card.add_widget(retry_row)
        
        app_card.height = '210dp'
        container.addWidget(app_card)
        
        scroll.add_widget(container)
        self.sett_screen.add_widget(scroll)

    def save_api_settings(self, instance, value):
        self.app.config_data["IMAGE_API_URL"] = self.txt_sett_img_path.text.strip()
        self.app.config_data["CHAT_API_URL"] = self.txt_sett_chat_path.text.strip()
        self.app.config_data["DEFAULT_API_TOKEN"] = self.txt_sett_token.text.strip()
        self.app.save_config()

    def save_general_settings(self, *args):
        self.app.config_data["PROXY_URL"] = self.txt_sett_proxy.text.strip()
        self.app.config_data["AUTO_RETRY"] = self.chk_retry.active
        try:
            self.app.config_data["RETRY_COUNT"] = int(self.txt_retry_count.text.strip())
        except:
            self.app.config_data["RETRY_COUNT"] = 3
        self.app.save_config()

# ==========================================
# 6. Main Application Class
# ==========================================
class AIImageGeneratorApp(App):
    def build(self):
        self.title = "AI Image Generator"
        
        self.user_dir = self.user_data_dir
        self.config_file = os.path.join(self.user_dir, "config.json")
        self.templates_file = os.path.join(self.user_dir, "templates.json")
        self.history_file = os.path.join(self.user_dir, "history.json")
        self.image_out_dir = os.path.join(self.user_dir, "output", "images")
        self.log_dir = os.path.join(self.user_dir, "output", "logs")
        
        os.makedirs(self.image_out_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.config_data = self.load_config()
        self.templates_data = self.load_json_file(self.templates_file, [])
        self.history_data = self.load_json_file(self.history_file, [])
        
        self.ref_image_path = ""
        self.current_result_image = ""
        self.is_generating = False
        self.is_prompt_processing = False
        self.generation_start_time = 0
        self.timer_trigger = None
        
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        Builder.load_string(KV_STYLE)
        
        self.main_layout = MainLayout()
        return self.main_layout

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r", encoding="utf-8") as f:
                try:
                    cfg = json.load(f)
                except:
                    cfg = {}
        else:
            cfg = {}
            
        cfg.setdefault("IMAGE_API_URL", "https://api.openai.com/v1/images/generations")
        cfg.setdefault("CHAT_API_URL", "https://api.openai.com/v1/chat/completions")
        cfg.setdefault("DEFAULT_API_TOKEN", "")
        cfg.setdefault("PROXY_URL", "")
        
        if "MODEL_HISTORY" in cfg:
            cfg["MODEL_HISTORY"] = [m for m in cfg["MODEL_HISTORY"] if m not in ["gpt-image-1", "gpt-image-1.5"]]
            for dm in DEFAULT_MODELS:
                if dm not in cfg["MODEL_HISTORY"]:
                    cfg["MODEL_HISTORY"].append(dm)
        else:
            cfg["MODEL_HISTORY"] = DEFAULT_MODELS.copy()
            
        if cfg.get("LAST_USED_MODEL") in ["gpt-image-1", "gpt-image-1.5"]:
            cfg["LAST_USED_MODEL"] = cfg["MODEL_HISTORY"][0]
            
        cfg.setdefault("LAST_USED_MODEL", cfg["MODEL_HISTORY"][0])
        cfg.setdefault("DEFAULT_QUALITY", "low")
        cfg.setdefault("AUTO_RETRY", False)
        cfg.setdefault("RETRY_COUNT", 3)
        cfg.setdefault("LANGUAGE", "zh")
        cfg.setdefault("DARK_THEME", True)
        
        return cfg

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=2)

    def load_json_file(self, path, default=None):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                try:
                    return json.load(f)
                except:
                    return default if default is not None else []
        return default if default is not None else []

    def save_json_file(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def t(self, key):
        lang = self.config_data.get("LANGUAGE", "zh")
        return LANG.get(lang, LANG["zh"]).get(key, key)

    def toggle_language(self, instance):
        lang = "en" if self.config_data.get("LANGUAGE", "zh") == "zh" else "zh"
        self.config_data["LANGUAGE"] = lang
        self.save_config()
        self.main_layout.update_retranslated_texts()

    def add_history_entry(self, prompt, model, status, image_path):
        entry = {
            "prompt": prompt,
            "model": model,
            "status": status,
            "image": image_path,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history_data.insert(0, entry)
        if len(self.history_data) > 200:
            self.history_data.pop()
        self.save_json_file(self.history_file, self.history_data)
        self.main_layout.refresh_history_ui()

    def create_canvas_callback(self, widget, color_val, radius_val):
        def callback(*args):
            widget.canvas.before.clear()
            with widget.canvas.before:
                Color(color_val, color_val, color_val, 1)
                RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius_val])
        return callback

if __name__ == "__main__":
    from kivy.factory import Factory
    # Register dynamically composed classes
    Factory.register('HistoryItem', cls=HistoryItem)
    Factory.register('TemplateItem', cls=TemplateItem)
    Factory.register('NavButton', cls=NavButton)
    
    app = AIImageGeneratorApp()
    app.run()
