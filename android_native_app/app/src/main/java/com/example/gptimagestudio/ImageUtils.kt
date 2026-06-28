package com.example.gptimagestudio

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

object ImageUtils {
    suspend fun downloadImageAsBitmap(imageUrl: String): Result<Bitmap> = withContext(Dispatchers.IO) {
        try {
            val url = URL(imageUrl)
            val connection = url.openConnection() as HttpURLConnection
            connection.doInput = true
            connection.connect()
            val input: InputStream = connection.inputStream
            val bitmap = BitmapFactory.decodeStream(input)
            if (bitmap != null) {
                Result.success(bitmap)
            } else {
                Result.failure(Exception("Could not decode bitmap from URL"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
