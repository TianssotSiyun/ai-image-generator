package com.example.gptimagestudio

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.util.concurrent.TimeUnit

data class GenerationResult(
    val images: List<String>,
    val promptTokens: Int = 0,
    val completionTokens: Int = 0,
    val totalTokens: Int = 0,
    val duration: String = "",
    val apiUrl: String = ""
)

object NetworkManager {

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(300, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .build()

    suspend fun generateImage(
        apiUrl: String,
        token: String,
        model: String,
        prompt: String,
        size: String,
        quality: String,
        refImageBase64s: List<String> = emptyList(),
        n: Int = 1
    ): Result<GenerationResult> = withContext(Dispatchers.IO) {
        val startTime = System.currentTimeMillis()
        try {
            val jsonObject = JSONObject()
            jsonObject.put("model", model)
            jsonObject.put("size", size.split("(")[0].trim()) // clean up size "1024x1024 (Square)" -> "1024x1024"
            
            val isImageApi = apiUrl.lowercase().contains("images/generations")
            
            if (isImageApi) {
                jsonObject.put("prompt", prompt)
                jsonObject.put("quality", quality)
                jsonObject.put("n", n)
                if (refImageBase64s.isNotEmpty()) {
                    val firstB64 = refImageBase64s[0]
                    val dataUrl = "data:image/jpeg;base64,$firstB64"
                    jsonObject.put("image", dataUrl)
                    jsonObject.put("image_url", dataUrl)
                }
                // Custom endpoints list support
                if (refImageBase64s.isNotEmpty()) {
                    val imagesArr = JSONArray()
                    refImageBase64s.forEach { b64 ->
                        imagesArr.put("data:image/jpeg;base64,$b64")
                    }
                    jsonObject.put("images", imagesArr)
                }
            } else {
                val messages = JSONArray()
                if (refImageBase64s.isNotEmpty()) {
                    val userMsg = JSONObject()
                    userMsg.put("role", "user")
                    val contentArr = JSONArray()
                    
                    val textContent = JSONObject()
                    textContent.put("type", "text")
                    textContent.put("text", "Modify these images. Prompt: $prompt")
                    contentArr.put(textContent)
                    
                    refImageBase64s.forEach { b64 ->
                        val imageContent = JSONObject()
                        imageContent.put("type", "image_url")
                        val urlObj = JSONObject()
                        urlObj.put("url", "data:image/jpeg;base64,$b64")
                        imageContent.put("image_url", urlObj)
                        contentArr.put(imageContent)
                    }
                    
                    userMsg.put("content", contentArr)
                    messages.put(userMsg)
                } else {
                    val userMsg = JSONObject()
                    userMsg.put("role", "user")
                    userMsg.put("content", "Generate an image. Prompt: $prompt")
                    messages.put(userMsg)
                }
                jsonObject.put("messages", messages)
                jsonObject.put("n", n)
            }

            val requestBody = jsonObject.toString().toRequestBody("application/json".toMediaTypeOrNull())
            
            val request = Request.Builder()
                .url(apiUrl)
                .addHeader("Authorization", "Bearer $token")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val durationMs = System.currentTimeMillis() - startTime
            val durationStr = String.format("%.2fs", durationMs / 1000.0)

            if (!response.isSuccessful) {
                val err = response.body?.string() ?: "Unknown error"
                return@withContext Result.failure(Exception("HTTP Error ${response.code}: $err"))
            }

            val bodyStr = response.body?.string() ?: ""
            val resObj = JSONObject(bodyStr)
            
            val extractedList = mutableListOf<String>()
            var promptTokens = 0
            var completionTokens = 0
            var totalTokens = 0

            // Parse token usage
            if (resObj.has("usage")) {
                val usageObj = resObj.getJSONObject("usage")
                promptTokens = usageObj.optInt("prompt_tokens", 0)
                completionTokens = usageObj.optInt("completion_tokens", 0)
                totalTokens = usageObj.optInt("total_tokens", 0)
            }

            // Case 1: Images API response ('data' field)
            if (resObj.has("data")) {
                val dataArr = resObj.getJSONArray("data")
                for (i in 0 until dataArr.length()) {
                    val dataItem = dataArr.getJSONObject(i)
                    var imgUrl: String? = null
                    var imgBase64: String? = null
                    if (dataItem.has("url")) imgUrl = dataItem.getString("url")
                    if (imgUrl.isNullOrEmpty() && dataItem.has("b64_json")) {
                        imgBase64 = dataItem.getString("b64_json")
                    }
                    if (!imgBase64.isNullOrEmpty()) {
                        extractedList.add("base64:$imgBase64")
                    } else if (!imgUrl.isNullOrEmpty()) {
                        extractedList.add("url:$imgUrl")
                    }
                }
            }
            
            // Case 2: Chat API response ('choices' field)
            if (extractedList.isEmpty() && resObj.has("choices")) {
                val choices = resObj.getJSONArray("choices")
                for (i in 0 until choices.length()) {
                    val choiceObj = choices.getJSONObject(i)
                    if (choiceObj.has("message")) {
                        val content = choiceObj.getJSONObject("message").getString("content")
                        if (content.isNotEmpty()) {
                            // 1. Safe URL extraction: split words first to prevent ReDoS on huge base64 strings
                            val words = content.split(Regex("\\s+"))
                            var foundUrl: String? = null
                            for (word in words) {
                                val cleanWord = word.trim('(', ')', '[', ']', '{', '}', '"', '\'', '<', '>', '*')
                                if (cleanWord.startsWith("http://", ignoreCase = true) || cleanWord.startsWith("https://", ignoreCase = true)) {
                                    val cleanLower = cleanWord.lowercase()
                                    if (cleanLower.endsWith(".png") || cleanLower.endsWith(".jpg") || cleanLower.endsWith(".jpeg") || cleanLower.endsWith(".webp") || cleanLower.endsWith(".gif")) {
                                        foundUrl = cleanWord
                                        break
                                    }
                                }
                            }
                            if (!foundUrl.isNullOrEmpty()) {
                                extractedList.add("url:$foundUrl")
                            } else {
                                // 2. Base64 extraction from content using fast index-based string operations
                                var foundB64: String? = null
                                if (content.contains("data:image") && content.contains("base64")) {
                                    var startIdx = content.indexOf("data:image")
                                    while (startIdx != -1) {
                                        val commaIdx = content.indexOf(",", startIdx)
                                        if (commaIdx != -1) {
                                            var endIdx = commaIdx + 1
                                            val terminators = setOf(' ', ')', ']', '"', '\'', '>', '\n', '\r')
                                            while (endIdx < content.length && content[endIdx] !in terminators) {
                                                endIdx++
                                            }
                                            val b64Str = content.substring(commaIdx + 1, endIdx).trim()
                                            if (b64Str.length > 100) {
                                                foundB64 = b64Str
                                                break
                                            }
                                            startIdx = content.indexOf("data:image", endIdx)
                                        } else {
                                            break
                                        }
                                    }
                                } else if (content.length > 1000 && !content.trim().lowercase().startsWith("http")) {
                                    // Raw base64 check
                                    val cleanedContent = content.replace(Regex("\\s+"), "")
                                    val rawB64 = if (cleanedContent.contains(",")) cleanedContent.split(",")[1] else cleanedContent
                                    try {
                                        val decodedBytes = Base64.decode(rawB64.take(100), Base64.DEFAULT)
                                        if (decodedBytes.size >= 2) {
                                            val isPng = decodedBytes.size >= 8 && decodedBytes[0] == 0x89.toByte() && decodedBytes[1] == 0x50.toByte()
                                            val isJpg = decodedBytes[0] == 0xFF.toByte() && decodedBytes[1] == 0xD8.toByte()
                                            val isWebp = decodedBytes.size >= 12 && 
                                                         decodedBytes[0] == 'R'.toByte() && decodedBytes[1] == 'I'.toByte() && 
                                                         decodedBytes[2] == 'F'.toByte() && decodedBytes[3] == 'F'.toByte()
                                            if (isPng || isJpg || isWebp) {
                                                foundB64 = rawB64
                                            }
                                        }
                                    } catch (e: Exception) {}
                                }
                                if (!foundB64.isNullOrEmpty()) {
                                    extractedList.add("base64:$foundB64")
                                }
                            }
                        }
                    }
                }
            }

            if (extractedList.isNotEmpty()) {
                Result.success(GenerationResult(
                    images = extractedList,
                    promptTokens = promptTokens,
                    completionTokens = completionTokens,
                    totalTokens = totalTokens,
                    duration = durationStr,
                    apiUrl = apiUrl
                ))
            } else {
                Result.failure(Exception("Failed to extract image from response: $bodyStr"))
            }

        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun translatePrompt(apiUrl: String, token: String, model: String, prompt: String): Result<String> = withContext(Dispatchers.IO) {
        try {
            val jsonObject = JSONObject()
            jsonObject.put("model", model)
            val messages = JSONArray()
            val userMsg = JSONObject()
            userMsg.put("role", "user")
            userMsg.put("content", "Translate the following prompt into English. Only return the translated text, without any explanations or quotes: $prompt")
            messages.put(userMsg)
            jsonObject.put("messages", messages)

            val requestBody = jsonObject.toString().toRequestBody("application/json".toMediaTypeOrNull())
            val request = Request.Builder()
                .url(apiUrl)
                .addHeader("Authorization", "Bearer $token")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            if (!response.isSuccessful) {
                val err = response.body?.string() ?: "Unknown error"
                return@withContext Result.failure(Exception("HTTP Error ${response.code}: $err"))
            }

            val bodyStr = response.body?.string() ?: ""
            val resObj = JSONObject(bodyStr)
            var translated = ""

            if (resObj.has("choices")) {
                val choices = resObj.getJSONArray("choices")
                if (choices.length() > 0) {
                    translated = choices.getJSONObject(0).getJSONObject("message").getString("content").trim()
                }
            }

            if (translated.isNotEmpty()) {
                Result.success(translated)
            } else {
                Result.failure(Exception("Could not extract translation"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
