package com.example.gptimagestudio

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("gpt_image_prefs", Context.MODE_PRIVATE)

    var imageApiUrl: String
        get() = prefs.getString("image_api_url", "https://api.openai.com/v1/images/generations") ?: ""
        set(value) = prefs.edit().putString("image_api_url", value).apply()

    var chatApiUrl: String
        get() = prefs.getString("chat_api_url", "https://api.openai.com/v1/chat/completions") ?: ""
        set(value) = prefs.edit().putString("chat_api_url", value).apply()

    var imageApiToken: String
        get() = prefs.getString("image_api_token", "") ?: prefs.getString("api_token", "") ?: ""
        set(value) = prefs.edit().putString("image_api_token", value).apply()

    var chatApiToken: String
        get() = prefs.getString("chat_api_token", "") ?: prefs.getString("api_token", "") ?: ""
        set(value) = prefs.edit().putString("chat_api_token", value).apply()

    var apiToken: String
        get() = prefs.getString("api_token", "") ?: ""
        set(value) = prefs.edit().putString("api_token", value).apply()

    var selectedModel: String
        get() = prefs.getString("selected_model", "gpt-4o") ?: ""
        set(value) = prefs.edit().putString("selected_model", value).apply()
        
    var promptQuality: String
        get() = prefs.getString("prompt_quality", "standard") ?: "standard"
        set(value) = prefs.edit().putString("prompt_quality", value).apply()
        
    var promptSize: String
        get() = prefs.getString("prompt_size", "1024x1024") ?: "1024x1024"
        set(value) = prefs.edit().putString("prompt_size", value).apply()
    var templatesJson: String
        get() = prefs.getString("prompt_templates", "[]") ?: "[]"
        set(value) = prefs.edit().putString("prompt_templates", value).apply()
        
    var apiProfilesJson: String
        get() = prefs.getString("api_profiles", "[]") ?: "[]"
        set(value) = prefs.edit().putString("api_profiles", value).apply()
        
    var currentApiProfileIndex: Int
        get() = prefs.getInt("current_api_profile_index", 0)
        set(value) = prefs.edit().putInt("current_api_profile_index", value).apply()
}
