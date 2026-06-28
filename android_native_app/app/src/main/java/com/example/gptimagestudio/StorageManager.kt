package com.example.gptimagestudio

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.io.OutputStream

import org.json.JSONArray
import org.json.JSONObject

data class HistoryItem(
    val id: String,
    val imageFiles: List<File>,
    val prompt: String,
    val model: String,
    val size: String,
    val quality: String,
    val timestamp: Long,
    val apiUrl: String = "",
    val duration: String = "",
    val promptTokens: Int = 0,
    val completionTokens: Int = 0,
    val totalTokens: Int = 0
) {
    val isImageDeleted: Boolean get() = imageFiles.isEmpty() || imageFiles.all { !it.exists() }
}

object StorageManager {

    // Save multiple bitmaps to internal app storage (Gallery)
    suspend fun saveImageToInternalStorage(
        context: Context, 
        bitmaps: List<Bitmap>,
        prompt: String = "",
        model: String = "",
        size: String = "",
        quality: String = "",
        apiUrl: String = "",
        duration: String = "",
        promptTokens: Int = 0,
        completionTokens: Int = 0,
        totalTokens: Int = 0
    ): Result<List<String>> = withContext(Dispatchers.IO) {
        try {
            val directory = File(context.filesDir, "gpt_images")
            if (!directory.exists()) {
                directory.mkdirs()
            }
            val timestamp = System.currentTimeMillis()
            val savedPaths = mutableListOf<String>()
            val fileNames = JSONArray()

            bitmaps.forEachIndexed { index, bitmap ->
                val fileName = "img_${timestamp}_$index.jpg"
                val file = File(directory, fileName)
                FileOutputStream(file).use { out ->
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out)
                }
                savedPaths.add(file.absolutePath)
                fileNames.put(fileName)
            }

            // Save Metadata
            val metaFile = File(directory, "img_$timestamp.json")
            val metaJson = JSONObject()
            metaJson.put("id", "img_$timestamp")
            metaJson.put("filenames", fileNames)
            metaJson.put("prompt", prompt)
            metaJson.put("model", model)
            metaJson.put("size", size)
            metaJson.put("quality", quality)
            metaJson.put("timestamp", timestamp)
            metaJson.put("api_url", apiUrl)
            metaJson.put("duration", duration)
            metaJson.put("prompt_tokens", promptTokens)
            metaJson.put("completion_tokens", completionTokens)
            metaJson.put("total_tokens", totalTokens)
            metaFile.writeText(metaJson.toString())

            Result.success(savedPaths)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // List all internally saved images
    fun getInternalImages(context: Context): List<File> {
        val directory = File(context.filesDir, "gpt_images")
        if (!directory.exists()) return emptyList()
        return directory.listFiles()?.sortedByDescending { it.lastModified() } ?: emptyList()
    }

    // List all internally saved images with metadata
    fun getInternalHistory(context: Context): List<HistoryItem> {
        val directory = File(context.filesDir, "gpt_images")
        if (!directory.exists()) return emptyList()
        val metaFiles = directory.listFiles { file -> file.name.endsWith(".json") } ?: return emptyList()
        
        return metaFiles.map { metaFile ->
            var id = metaFile.name.replace(".json", "")
            var prompt = ""
            var model = ""
            var size = ""
            var quality = ""
            var ts = metaFile.lastModified()
            var apiUrl = ""
            var duration = ""
            var promptTokens = 0
            var completionTokens = 0
            var totalTokens = 0
            val imageFiles = mutableListOf<File>()

            try {
                val json = JSONObject(metaFile.readText())
                id = json.optString("id", id)
                prompt = json.optString("prompt", "")
                model = json.optString("model", "")
                size = json.optString("size", "")
                quality = json.optString("quality", "")
                ts = json.optLong("timestamp", metaFile.lastModified())
                apiUrl = json.optString("api_url", "")
                duration = json.optString("duration", "")
                promptTokens = json.optInt("prompt_tokens", 0)
                completionTokens = json.optInt("completion_tokens", 0)
                totalTokens = json.optInt("total_tokens", 0)

                if (json.has("filenames")) {
                    val arr = json.getJSONArray("filenames")
                    for (i in 0 until arr.length()) {
                        imageFiles.add(File(directory, arr.getString(i)))
                    }
                } else {
                    // Fallback for older items that only had a single image file named "img_$timestamp.jpg"
                    val legacyImg = File(directory, "${metaFile.nameWithoutExtension}.jpg")
                    imageFiles.add(legacyImg)
                }
            } catch (e: Exception) {
                // Fallback in case of parsing error
                val legacyImg = File(directory, "${metaFile.nameWithoutExtension}.jpg")
                imageFiles.add(legacyImg)
            }
            
            HistoryItem(
                id = id,
                imageFiles = imageFiles,
                prompt = prompt,
                model = model,
                size = size,
                quality = quality,
                timestamp = ts,
                apiUrl = apiUrl,
                duration = duration,
                promptTokens = promptTokens,
                completionTokens = completionTokens,
                totalTokens = totalTokens
            )
        }.sortedByDescending { it.timestamp }
    }

    // Save an internal file to the public MediaStore (Phone Album)
    suspend fun saveImageToMediaStore(context: Context, imageFile: File): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val bitmap = BitmapFactory.decodeFile(imageFile.absolutePath)
            if (bitmap != null) {
                saveBitmapToMediaStore(context, bitmap, imageFile.name)
            } else {
                Result.failure(Exception("Failed to decode image file"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private suspend fun saveBitmapToMediaStore(context: Context, bitmap: Bitmap, fileName: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val contentValues = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, fileName)
                put(MediaStore.MediaColumns.MIME_TYPE, "image/jpeg")
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_PICTURES + "/GPTImageStudio")
                    put(MediaStore.MediaColumns.IS_PENDING, 1)
                }
            }

            val resolver = context.contentResolver
            val uri = resolver.insert(MediaStore.Images.Media.EXTERNAL_CONTENT_URI, contentValues)
            
            if (uri != null) {
                resolver.openOutputStream(uri).use { out ->
                    if (out != null) {
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 100, out)
                    }
                }
                
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    contentValues.clear()
                    contentValues.put(MediaStore.MediaColumns.IS_PENDING, 0)
                    resolver.update(uri, contentValues, null, null)
                }
                Result.success(true)
            } else {
                Result.failure(Exception("Failed to create MediaStore entry"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    // Delete an internal image
    fun deleteInternalImage(file: File): Boolean {
        return try {
            file.delete()
        } catch (e: Exception) {
            false
        }
    }
}
