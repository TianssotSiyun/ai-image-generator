# AI Image Generator Aero (PC & Android)

A premium, glassmorphic AI Image Generator supporting text-to-image (文生图) and image-to-image (图生图) workflows. Features a synchronized experience across Desktop (Windows) and Mobile (Android v1.1) platforms.

---

## 🎨 Core Features | 核心功能

*   **Multi-Image Reference (图生图多选)**: Feed multiple reference images into the model for highly controlled generation. Includes intuitive red close buttons to manage references.
*   **Batch Image Generation (多图并发)**: Set a target count from 1 to 10 to generate grid results and browse through them with a carousel switcher.
*   **Token & Efficiency Logging (计费与效率审计)**: Real-time logging of prompt tokens, completion tokens, duration, and the target API URL.
*   **Robust History & Recovery (防丢失历史记录)**: Physically deleted photos on disk are automatically marked as "Deleted" (已删除) in your gallery. Prompts remain fully copyable and reusable.
*   **Premium Aero Aesthetics (极客紫黑皮肤)**: Built on glassmorphic card designs with cyberpunk violet neon colors, matching perfectly between PC and Mobile.

---

## ⚠️ Important Precautions | 使用注意事项 [极重要]

Before installing and setting up the app, please read these critical usage rules:

1.  **API Token Security (API 密钥安全)**
    *   **Warning**: The software **does not** come with any built-in keys. You must supply your own API Token.
    *   Never share your `config.json` file, and avoid uploading screenshots containing your token.

2.  **Image-to-Image Routing Mechanism (图生图端点分流机制)**
    *   Standard DALL-E endpoints (e.g., `/v1/images/generations`) do not accept image inputs. 
    *   **Therefore**, whenever reference images are selected, the software **automatically routes the request to your Chat API Url** (e.g., `/v1/chat/completions`).
    *   **Requirement**: You must ensure your **Chat API** is configured, and the selected **Model** must support vision/multimodal input (e.g., `gpt-4o`, `claude-3-5-sonnet`, `gemini-1.5-flash`). Using a non-vision model for Image-to-Image will cause the request to fail.

3.  **Batch Generation Limits (批量生图额度限制)**
    *   While the UI allows requesting up to 10 images at once, your API provider might have concurrency limits (Rate Limits) or strict timeout bounds. If you experience timeouts when generating 5+ images, reduce the count or upgrade your API tier.

4.  **Android Storage Permissions (手机存储写入权限)**
    *   To successfully use "Save to Gallery" (保存到手机相册), you must grant storage/media permissions when prompted by your Android device.

---

## 🚀 Quick Start | 快速上手

### Desktop Version (Windows)
1.  Download the latest executable from the [GitHub Releases](https://github.com/TianssotSiyun/ai-image-generator/releases) page.
2.  Run `AI_Image_Generator.exe`.
3.  Navigate to **Settings** (设置) to configure your API URL and Token.
4.  Write your prompt, select reference images if needed, and click **Generate** (生成).

### Mobile Version (Android)
1.  Download `AI_Image_Generator_Aero.apk` from the [GitHub Releases](https://github.com/TianssotSiyun/ai-image-generator/releases) page.
2.  Install it on your Android device (allow installations from unknown sources if prompted).
3.  Open the App, tap **Settings** in the top right to configure your API profiles.
4.  Enjoy generating images on-the-go!

---

## 🛠️ Project Structure | 源码结构

*   `/main2.py`: Python PySide6 source code for the Windows application.
*   `/android_native_app/`: Android Studio native project source code built using Kotlin & Jetpack Compose.
