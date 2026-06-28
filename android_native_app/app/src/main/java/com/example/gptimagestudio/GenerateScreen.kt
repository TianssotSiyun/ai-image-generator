package com.example.gptimagestudio

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.util.Base64
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.gptimagestudio.ui.components.glassmorphism
import kotlinx.coroutines.launch
import java.io.ByteArrayOutputStream
import org.json.JSONArray
import org.json.JSONObject
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.draw.clip
import androidx.compose.foundation.lazy.LazyRow


@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GenerateScreen(
    prefs: PreferencesManager,
    referenceImageInternal: String?,
    templatePrompt: String?,
    onClearReference: () -> Unit,
    onClearTemplate: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    // API Profiles Logic
    var apiProfiles by remember { 
        mutableStateOf<List<Map<String, String>>>(
            try {
                val arr = JSONArray(prefs.apiProfilesJson)
                List(arr.length()) { i ->
                    val obj = arr.getJSONObject(i)
                    mapOf(
                        "name" to obj.optString("name", "默认配置"),
                        "image_url" to obj.optString("image_url", ""),
                        "chat_url" to obj.optString("chat_url", ""),
                        "image_token" to obj.optString("image_token", obj.optString("token", "")),
                        "chat_token" to obj.optString("chat_token", obj.optString("token", ""))
                    )
                }
            } catch (e: Exception) { emptyList() }
        )
    }

    LaunchedEffect(Unit) {
        if (apiProfiles.isEmpty()) {
            val defaultProfile = mapOf(
                "name" to "默认配置 (Default)",
                "image_url" to prefs.imageApiUrl,
                "chat_url" to prefs.chatApiUrl,
                "image_token" to prefs.imageApiToken,
                "chat_token" to prefs.chatApiToken
            )
            apiProfiles = listOf(defaultProfile)
            val arr = JSONArray()
            arr.put(JSONObject(defaultProfile))
            prefs.apiProfilesJson = arr.toString()
            prefs.currentApiProfileIndex = 0
        }
    }

    var expandedProfile by remember { mutableStateOf(false) }
    var currentProfileIndex by remember { mutableStateOf(prefs.currentApiProfileIndex.coerceIn(0, (apiProfiles.size - 1).coerceAtLeast(0))) }

    var apiUrl by remember { mutableStateOf(prefs.imageApiUrl) }
    var chatUrl by remember { mutableStateOf(prefs.chatApiUrl) }
    var imageToken by remember { mutableStateOf(prefs.imageApiToken) }
    var chatToken by remember { mutableStateOf(prefs.chatApiToken) }
    var model by remember { mutableStateOf(prefs.selectedModel) }

    // Dynamic Models dropdown list
    var fetchedModels by remember { mutableStateOf<List<String>>(emptyList()) }
    var expandedModelDropdown by remember { mutableStateOf(false) }
    var isFetchingModels by remember { mutableStateOf(false) }
    
    // Sync current profile to inputs
    LaunchedEffect(currentProfileIndex, apiProfiles) {
        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
            val p = apiProfiles[currentProfileIndex]
            apiUrl = p["image_url"] ?: ""
            chatUrl = p["chat_url"] ?: ""
            imageToken = p["image_token"] ?: p["token"] ?: ""
            chatToken = p["chat_token"] ?: p["token"] ?: ""
        }
    }

    var prompt by remember { mutableStateOf("") }
    
    // Auto-fill template prompt if passed
    LaunchedEffect(templatePrompt) {
        if (templatePrompt != null) {
            prompt = templatePrompt
            onClearTemplate()
        }
    }

    val sizes = listOf("1024x1024", "1536x1024", "1024x1536", "2048x2048")
    var size by remember { mutableStateOf(prefs.promptSize) }
    var expandedSize by remember { mutableStateOf(false) }

    val qualities = listOf("standard", "hd")
    var quality by remember { mutableStateOf(prefs.promptQuality) }
    var expandedQuality by remember { mutableStateOf(false) }
    
    var isGenerating by remember { mutableStateOf(false) }
    var isTranslating by remember { mutableStateOf(false) }
    var isOptimizing by remember { mutableStateOf(false) }
    
    var resultBitmaps by remember { mutableStateOf<List<Bitmap>>(emptyList()) }
    var selectedOutputIndex by remember { mutableStateOf(0) }
    var statusText by remember { mutableStateOf("状态: 待机") }

    var refImageUris by remember { mutableStateOf<List<Uri>>(emptyList()) }
    var imageCount by remember { mutableStateOf(1) }
    
    val galleryLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetMultipleContents()
    ) { uris: List<Uri> ->
        refImageUris = uris
        if (uris.isNotEmpty()) onClearReference()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("AI 桌面图像生成器", fontSize = 28.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)

        // API Settings Card
        var showSaveProfileDialog by remember { mutableStateOf(false) }
        var newProfileName by remember { mutableStateOf("") }
        
        if (showSaveProfileDialog) {
            AlertDialog(
                onDismissRequest = { showSaveProfileDialog = false },
                title = { Text("保存 API 配置") },
                text = {
                    OutlinedTextField(
                        value = newProfileName,
                        onValueChange = { newProfileName = it },
                        label = { Text("配置名称 (同名将覆盖)") }
                    )
                },
                confirmButton = {
                    TextButton(onClick = {
                        val name = newProfileName.trim()
                        if (name.isNotEmpty()) {
                            val newList = apiProfiles.toMutableList()
                            val existingIdx = newList.indexOfFirst { it["name"] == name }
                            val newProf = mapOf(
                                "name" to name,
                                "image_url" to apiUrl,
                                "chat_url" to chatUrl,
                                "image_token" to imageToken,
                                "chat_token" to chatToken
                            )
                            if (existingIdx != -1) {
                                newList[existingIdx] = newProf
                                currentProfileIndex = existingIdx
                            } else {
                                newList.add(newProf)
                                currentProfileIndex = newList.size - 1
                            }
                            apiProfiles = newList
                            val arr = JSONArray()
                            newList.forEach { arr.put(JSONObject(it)) }
                            prefs.apiProfilesJson = arr.toString()
                            prefs.currentApiProfileIndex = currentProfileIndex
                        }
                        showSaveProfileDialog = false
                    }) { Text("保存") }
                },
                dismissButton = {
                    TextButton(onClick = { showSaveProfileDialog = false }) { Text("取消") }
                }
            )
        }

        Card(
            modifier = Modifier.fillMaxWidth().glassmorphism(),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("API 连接配置与存档", fontWeight = FontWeight.SemiBold)
                
                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    ExposedDropdownMenuBox(
                        expanded = expandedProfile,
                        onExpandedChange = { expandedProfile = !expandedProfile },
                        modifier = Modifier.weight(1f)
                    ) {
                        OutlinedTextField(
                            value = if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) apiProfiles[currentProfileIndex]["name"] ?: "" else "",
                            onValueChange = {}, readOnly = true,
                            label = { Text("选择 API 预设") }, modifier = Modifier.menuAnchor()
                        )
                        ExposedDropdownMenu(expanded = expandedProfile, onDismissRequest = { expandedProfile = false }) {
                            apiProfiles.forEachIndexed { idx, p ->
                                DropdownMenuItem(
                                    text = { Text(p["name"] ?: "") },
                                    onClick = {
                                        currentProfileIndex = idx
                                        prefs.currentApiProfileIndex = idx
                                        expandedProfile = false
                                    }
                                )
                            }
                        }
                    }
                    IconButton(onClick = { 
                        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
                            newProfileName = apiProfiles[currentProfileIndex]["name"] ?: ""
                        }
                        showSaveProfileDialog = true 
                    }) {
                        Text("➕")
                    }
                    IconButton(onClick = {
                        if (apiProfiles.size > 1 && currentProfileIndex in apiProfiles.indices) {
                            val newList = apiProfiles.toMutableList()
                            newList.removeAt(currentProfileIndex)
                            apiProfiles = newList
                            currentProfileIndex = 0
                            val arr = JSONArray()
                            newList.forEach { arr.put(JSONObject(it)) }
                            prefs.apiProfilesJson = arr.toString()
                            prefs.currentApiProfileIndex = 0
                        } else {
                            Toast.makeText(context, "必须保留至少一个配置", Toast.LENGTH_SHORT).show()
                        }
                    }) {
                        Text("🗑️")
                    }
                }

                // Image API Configuration
                OutlinedTextField(
                    value = apiUrl, onValueChange = { 
                        apiUrl = it; prefs.imageApiUrl = it 
                        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
                            val newList = apiProfiles.toMutableList()
                            val map = newList[currentProfileIndex].toMutableMap()
                            map["image_url"] = it
                            newList[currentProfileIndex] = map
                            apiProfiles = newList
                            val arr = JSONArray()
                            newList.forEach { p -> arr.put(JSONObject(p)) }
                            prefs.apiProfilesJson = arr.toString()
                        }
                    },
                    label = { Text("Image 路径 (生图端点)") }, modifier = Modifier.fillMaxWidth(), singleLine = true
                )
                OutlinedTextField(
                    value = imageToken, onValueChange = { 
                        imageToken = it; prefs.imageApiToken = it 
                        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
                            val newList = apiProfiles.toMutableList()
                            val map = newList[currentProfileIndex].toMutableMap()
                            map["image_token"] = it
                            newList[currentProfileIndex] = map
                            apiProfiles = newList
                            val arr = JSONArray()
                            newList.forEach { p -> arr.put(JSONObject(p)) }
                            prefs.apiProfilesJson = arr.toString()
                        }
                    },
                    label = { Text("Image API Token (生图令牌)") }, modifier = Modifier.fillMaxWidth(), singleLine = true
                )

                Spacer(modifier = Modifier.height(4.dp))

                // Chat API Configuration
                OutlinedTextField(
                    value = chatUrl, onValueChange = { 
                        chatUrl = it; prefs.chatApiUrl = it
                        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
                            val newList = apiProfiles.toMutableList()
                            val map = newList[currentProfileIndex].toMutableMap()
                            map["chat_url"] = it
                            newList[currentProfileIndex] = map
                            apiProfiles = newList
                            val arr = JSONArray()
                            newList.forEach { p -> arr.put(JSONObject(p)) }
                            prefs.apiProfilesJson = arr.toString()
                        }
                    },
                    label = { Text("Chat 路径 (对话端点/用于翻译优化)") }, modifier = Modifier.fillMaxWidth(), singleLine = true
                )
                OutlinedTextField(
                    value = chatToken, onValueChange = { 
                        chatToken = it; prefs.chatApiToken = it 
                        if (apiProfiles.isNotEmpty() && currentProfileIndex in apiProfiles.indices) {
                            val newList = apiProfiles.toMutableList()
                            val map = newList[currentProfileIndex].toMutableMap()
                            map["chat_token"] = it
                            newList[currentProfileIndex] = map
                            apiProfiles = newList
                            val arr = JSONArray()
                            newList.forEach { p -> arr.put(JSONObject(p)) }
                            prefs.apiProfilesJson = arr.toString()
                        }
                    },
                    label = { Text("Chat API Token (对话令牌)") }, modifier = Modifier.fillMaxWidth(), singleLine = true
                )

                Spacer(modifier = Modifier.height(4.dp))

                // Dynamic Model Dropdown selector
                Box(modifier = Modifier.fillMaxWidth()) {
                    ExposedDropdownMenuBox(
                        expanded = expandedModelDropdown && fetchedModels.isNotEmpty(),
                        onExpandedChange = { expandedModelDropdown = !expandedModelDropdown }
                    ) {
                        OutlinedTextField(
                            value = model,
                            onValueChange = { model = it; prefs.selectedModel = it },
                            label = { Text("选择/输入模型") },
                            modifier = Modifier.fillMaxWidth().menuAnchor(),
                            singleLine = true,
                            trailingIcon = {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    if (isFetchingModels) {
                                        CircularProgressIndicator(modifier = Modifier.size(20.dp))
                                    } else {
                                        IconButton(onClick = {
                                            var targetToken = chatToken
                                            if (targetToken.isBlank()) targetToken = imageToken
                                            if (chatUrl.isBlank() || targetToken.isBlank()) {
                                                Toast.makeText(context, "请先填入对话 API 路径或 Token", Toast.LENGTH_SHORT).show()
                                                return@IconButton
                                            }
                                            isFetchingModels = true
                                            scope.launch {
                                                val res = NetworkManager.fetchModels(chatUrl, targetToken)
                                                isFetchingModels = false
                                                if (res.isSuccess) {
                                                    fetchedModels = res.getOrNull() ?: emptyList()
                                                    expandedModelDropdown = true
                                                    Toast.makeText(context, "成功获取 ${fetchedModels.size} 个模型", Toast.LENGTH_SHORT).show()
                                                } else {
                                                    Toast.makeText(context, "获取模型失败: ${res.exceptionOrNull()?.message}", Toast.LENGTH_LONG).show()
                                                }
                                            }
                                        }) {
                                            Text("🔄", fontSize = 16.sp)
                                        }
                                    }
                                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = expandedModelDropdown)
                                }
                            }
                        )

                        if (fetchedModels.isNotEmpty()) {
                            ExposedDropdownMenu(
                                expanded = expandedModelDropdown,
                                onDismissRequest = { expandedModelDropdown = false }
                            ) {
                                fetchedModels.forEach { m ->
                                    DropdownMenuItem(
                                        text = { Text(m) },
                                        onClick = {
                                            model = m
                                            prefs.selectedModel = m
                                            expandedModelDropdown = false
                                        }
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // Settings (Size, Quality)
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            // Size Dropdown
            ExposedDropdownMenuBox(
                expanded = expandedSize,
                onExpandedChange = { expandedSize = !expandedSize },
                modifier = Modifier.weight(1f)
            ) {
                OutlinedTextField(
                    value = size, onValueChange = {}, readOnly = true,
                    label = { Text("分辨率规格") }, modifier = Modifier.menuAnchor()
                )
                ExposedDropdownMenu(expanded = expandedSize, onDismissRequest = { expandedSize = false }) {
                    sizes.forEach { s ->
                        DropdownMenuItem(text = { Text(s) }, onClick = { size = s; prefs.promptSize = s; expandedSize = false })
                    }
                }
            }

            // Quality Dropdown
            ExposedDropdownMenuBox(
                expanded = expandedQuality,
                onExpandedChange = { expandedQuality = !expandedQuality },
                modifier = Modifier.weight(1f)
            ) {
                OutlinedTextField(
                    value = quality, onValueChange = {}, readOnly = true,
                    label = { Text("生成质量") }, modifier = Modifier.menuAnchor()
                )
                ExposedDropdownMenu(expanded = expandedQuality, onDismissRequest = { expandedQuality = false }) {
                    qualities.forEach { q ->
                        DropdownMenuItem(text = { Text(q) }, onClick = { quality = q; prefs.promptQuality = q; expandedQuality = false })
                    }
                }
            }
        }

        // Prompt Input & Translate & Optimize
        Card(
            modifier = Modifier.fillMaxWidth().glassmorphism(),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Prompt 提示词高级设置", fontWeight = FontWeight.SemiBold)
                
                OutlinedTextField(
                    value = prompt, onValueChange = { prompt = it },
                    placeholder = { Text("在此处输入或粘贴提示词...") },
                    modifier = Modifier.fillMaxWidth().height(100.dp),
                    maxLines = 4
                )

                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = {
                        var targetToken = chatToken
                        if (targetToken.isBlank()) targetToken = imageToken
                        if (prompt.isBlank() || targetToken.isBlank()) {
                            Toast.makeText(context, "提示词与 API Token 不能为空", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        isTranslating = true
                        scope.launch {
                            val res = NetworkManager.translatePrompt(chatUrl, targetToken, if (model.isNotBlank()) model else "gpt-4o", prompt)
                            isTranslating = false
                            if (res.isSuccess) prompt = res.getOrNull() ?: prompt
                            else Toast.makeText(context, "翻译失败", Toast.LENGTH_SHORT).show()
                        }
                    }, enabled = !isTranslating, modifier = Modifier.weight(1f)) {
                        Text(if (isTranslating) "翻译中..." else "AI 翻译为英文")
                    }

                    Button(onClick = {
                        var targetToken = chatToken
                        if (targetToken.isBlank()) targetToken = imageToken
                        if (prompt.isBlank() || targetToken.isBlank()) {
                            Toast.makeText(context, "提示词与 API Token 不能为空", Toast.LENGTH_SHORT).show()
                            return@Button
                        }
                        isOptimizing = true
                        scope.launch {
                            val optimizePrompt = "You are a midjourney prompt engineer. Optimize the following prompt to be highly detailed and visually descriptive in English. Do not add conversational text, just the optimized prompt: $prompt"
                            val res = NetworkManager.translatePrompt(chatUrl, targetToken, if (model.isNotBlank()) model else "gpt-4o", optimizePrompt)
                            isOptimizing = false
                            if (res.isSuccess) prompt = res.getOrNull() ?: prompt
                            else Toast.makeText(context, "优化失败", Toast.LENGTH_SHORT).show()
                        }
                    }, enabled = !isOptimizing, modifier = Modifier.weight(1f)) {
                        Text(if (isOptimizing) "优化中..." else "AI 优化 Prompt")
                    }
                }
            }
        }

        // Reference Image
        Card(
            modifier = Modifier.fillMaxWidth().glassmorphism(),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent)
        ) {
            Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("参考原图 (支持多图选定图生图)", fontWeight = FontWeight.SemiBold)
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = { galleryLauncher.launch("image/*") }, modifier = Modifier.weight(1f)) {
                        Text("选择手机相册")
                    }
                    if (refImageUris.isNotEmpty() || referenceImageInternal != null) {
                        OutlinedButton(onClick = {
                            refImageUris = emptyList()
                            onClearReference()
                        }, modifier = Modifier.weight(1f)) {
                            Text("清除参考图")
                        }
                    }
                }
                
                // Show thumbnail row for selected reference images
                val refBitmaps = remember(refImageUris, referenceImageInternal) {
                    val list = mutableListOf<Bitmap>()
                    if (referenceImageInternal != null) {
                        try {
                            val bmp = BitmapFactory.decodeFile(referenceImageInternal)
                            if (bmp != null) list.add(bmp)
                        } catch (e: Exception) {}
                    }
                    refImageUris.forEach { uri ->
                        try {
                            val input = context.contentResolver.openInputStream(uri)
                            val bmp = BitmapFactory.decodeStream(input)
                            input?.close()
                            if (bmp != null) list.add(bmp)
                        } catch (e: Exception) {}
                    }
                    list
                }
                
                if (refBitmaps.isNotEmpty()) {
                    LazyRow(
                        modifier = Modifier.fillMaxWidth().height(90.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        items(refBitmaps.size) { idx ->
                            val bmp = refBitmaps[idx]
                            Box(modifier = Modifier.size(80.dp)) {
                                Image(
                                    bitmap = bmp.asImageBitmap(),
                                    contentDescription = "Ref Thumbnail",
                                    contentScale = ContentScale.Crop,
                                    modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(8.dp))
                                )
                                // Delete red cross button
                                Box(
                                    modifier = Modifier
                                        .align(Alignment.TopEnd)
                                        .padding(2.dp)
                                        .size(20.dp)
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(Color.Red)
                                        .clickable {
                                            if (referenceImageInternal != null && idx == 0) {
                                                onClearReference()
                                            } else {
                                                val galleryIdx = if (referenceImageInternal != null) idx - 1 else idx
                                                if (galleryIdx in refImageUris.indices) {
                                                    refImageUris = refImageUris.filterIndexed { i, _ -> i != galleryIdx }
                                                }
                                            }
                                        },
                                    contentAlignment = Alignment.Center
                                ) {
                                    Text("×", color = Color.White, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                } else {
                    Text("未选择参考图 [文生图模式]", color = Color.Gray)
                }
            }
        }

        // Image Count Selector (n)
        Row(
            modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("生成图片数量: ", fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                IconButton(onClick = { if (imageCount > 1) imageCount-- }) {
                    Text("➖", fontSize = 18.sp)
                }
                Text("$imageCount", fontSize = 18.sp, fontWeight = FontWeight.Bold)
                IconButton(onClick = { if (imageCount < 10) imageCount++ }) {
                    Text("➕", fontSize = 18.sp)
                }
            }
        }

        // Generate Button
        Button(
            onClick = {
                val isImageToImage = refImageUris.isNotEmpty() || referenceImageInternal != null
                var targetToken = if (isImageToImage) chatToken else imageToken
                if (targetToken.isBlank()) {
                    targetToken = if (isImageToImage) imageToken else chatToken
                }
                if (targetToken.isBlank() || prompt.isBlank()) {
                    Toast.makeText(context, "API Token或提示词不能为空", Toast.LENGTH_SHORT).show()
                    return@Button
                }
                isGenerating = true
                statusText = "状态: 正在发送请求..."
                
                scope.launch {
                    val base64Refs = mutableListOf<String>()
                    
                    // 1. Process local history reference image (if selected)
                    if (referenceImageInternal != null) {
                        try {
                            val bmp = BitmapFactory.decodeFile(referenceImageInternal)
                            if (bmp != null) {
                                val stream = ByteArrayOutputStream()
                                bmp.compress(Bitmap.CompressFormat.JPEG, 90, stream)
                                base64Refs.add(Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP))
                            }
                        } catch (e: Exception) {}
                    }
                    
                    // 2. Process gallery reference images (if selected)
                    refImageUris.forEach { uri ->
                        try {
                            val input = context.contentResolver.openInputStream(uri)
                            val bytes = input?.readBytes()
                            input?.close()
                            if (bytes != null) {
                                base64Refs.add(Base64.encodeToString(bytes, Base64.NO_WRAP))
                            }
                        } catch (e: Exception) {}
                    }

                    val targetApiUrl = if (base64Refs.isNotEmpty()) chatUrl else apiUrl

                    val result = NetworkManager.generateImage(
                        apiUrl = targetApiUrl, token = targetToken, model = model,
                        prompt = prompt, size = size, quality = quality, 
                        refImageBase64s = base64Refs, n = imageCount
                    )
                    
                    isGenerating = false
                    if (result.isSuccess) {
                        statusText = "状态: 完成"
                        val genResult = result.getOrNull()
                        val bitmapsList = mutableListOf<Bitmap>()

                        if (genResult != null) {
                            genResult.images.forEachIndexed { index, imgStr ->
                                statusText = "状态: 正在处理图片 ${index + 1}/${genResult.images.size}..."
                                var bmp: Bitmap? = null
                                if (imgStr.startsWith("url:")) {
                                    val url = imgStr.substring(4)
                                    val bmpRes = ImageUtils.downloadImageAsBitmap(url)
                                    if (bmpRes.isSuccess) {
                                        bmp = bmpRes.getOrNull()
                                    }
                                } else if (imgStr.startsWith("base64:")) {
                                    val b64 = imgStr.substring(7)
                                    val decoded = Base64.decode(b64, Base64.DEFAULT)
                                    bmp = BitmapFactory.decodeByteArray(decoded, 0, decoded.size)
                                }
                                if (bmp != null) {
                                    bitmapsList.add(bmp)
                                }
                            }
                        }

                        if (bitmapsList.isNotEmpty()) {
                            resultBitmaps = bitmapsList
                            selectedOutputIndex = 0
                            statusText = "状态: 完成"
                            // Save to Internal Gallery WITH Metadata
                            StorageManager.saveImageToInternalStorage(
                                context = context,
                                bitmaps = bitmapsList,
                                prompt = prompt,
                                model = model,
                                size = size,
                                quality = quality,
                                apiUrl = targetApiUrl,
                                duration = genResult?.duration ?: "",
                                promptTokens = genResult?.promptTokens ?: 0,
                                completionTokens = genResult?.completionTokens ?: 0,
                                totalTokens = genResult?.totalTokens ?: 0
                            )
                            Toast.makeText(context, "已保存到内部图库", Toast.LENGTH_SHORT).show()
                        } else {
                            statusText = "状态: 接口未能成功提取到图片"
                        }

                    } else {
                        statusText = "状态: 错误 - ${result.exceptionOrNull()?.message}"
                        Toast.makeText(context, "网络故障或接口报错", Toast.LENGTH_LONG).show()
                    }
                }
            },
            modifier = Modifier.fillMaxWidth().height(56.dp),
            enabled = !isGenerating
        ) {
            Text(if (isGenerating) "正在生成..." else "生成图像", fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
        
        Text(statusText, color = if (statusText.contains("错误") || statusText.contains("失败")) Color.Red else MaterialTheme.colorScheme.primary)

        // Result Image Area
        Card(
            modifier = Modifier.fillMaxWidth().height(420.dp).glassmorphism(),
            colors = CardDefaults.cardColors(containerColor = Color.Transparent)
        ) {
            Column(
                modifier = Modifier.fillMaxSize().padding(8.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Box(
                    modifier = Modifier.weight(1f).fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    if (resultBitmaps.isNotEmpty()) {
                        val bmp = resultBitmaps.getOrNull(selectedOutputIndex)
                        if (bmp != null) {
                            Image(
                                bitmap = bmp.asImageBitmap(),
                                contentDescription = "Generated Image",
                                contentScale = ContentScale.Fit,
                                modifier = Modifier.fillMaxSize()
                            )
                        }
                    } else {
                        Text("等待生成...", color = Color.Gray)
                    }
                }
                
                if (resultBitmaps.size > 1) {
                    LazyRow(
                        modifier = Modifier.fillMaxWidth().height(60.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        items(resultBitmaps.size) { idx ->
                            val bmp = resultBitmaps[idx]
                            val isSelected = idx == selectedOutputIndex
                            Box(
                                modifier = Modifier
                                    .size(50.dp)
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(if (isSelected) MaterialTheme.colorScheme.primary else Color.Transparent)
                                    .padding(if (isSelected) 2.dp else 0.dp)
                                    .clickable { selectedOutputIndex = idx }
                            ) {
                                Image(
                                    bitmap = bmp.asImageBitmap(),
                                    contentDescription = "Thumbnail",
                                    contentScale = ContentScale.Crop,
                                    modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(4.dp))
                                )
                            }
                        }
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
    }
}
