package com.example.gptimagestudio

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.gptimagestudio.ui.components.glassmorphism
import org.json.JSONArray
import org.json.JSONObject

data class TemplateItem(val name: String, val prompt: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TemplatesScreen(
    prefs: PreferencesManager,
    onUseTemplate: (String) -> Unit
) {
    var templates by remember { mutableStateOf(emptyList<TemplateItem>()) }
    var showDialog by remember { mutableStateOf(false) }
    var newTemplateName by remember { mutableStateOf("") }
    var newTemplatePrompt by remember { mutableStateOf("") }

    // Load
    LaunchedEffect(prefs.templatesJson) {
        val list = mutableListOf<TemplateItem>()
        try {
            val arr = JSONArray(prefs.templatesJson)
            for (i in 0 until arr.length()) {
                val obj = arr.getJSONObject(i)
                list.add(TemplateItem(obj.getString("name"), obj.getString("prompt")))
            }
        } catch (e: Exception) {}
        templates = list
    }

    val saveTemplates = { list: List<TemplateItem> ->
        val arr = JSONArray()
        list.forEach { 
            val obj = JSONObject()
            obj.put("name", it.name)
            obj.put("prompt", it.prompt)
            arr.put(obj)
        }
        prefs.templatesJson = arr.toString()
        templates = list
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("提示词模板", fontSize = 24.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
            Button(onClick = { showDialog = true }) {
                Text("新增模板")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))

        if (templates.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("暂无模板，请点击右上角新增", color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f))
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                items(templates) { t ->
                    Card(
                        modifier = Modifier.fillMaxWidth().glassmorphism(),
                        colors = CardDefaults.cardColors(containerColor = androidx.compose.ui.graphics.Color.Transparent)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(t.name, fontWeight = FontWeight.Bold, fontSize = 18.sp)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(t.prompt, style = MaterialTheme.typography.bodyMedium)
                            Spacer(modifier = Modifier.height(8.dp))
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Button(onClick = { onUseTemplate(t.prompt) }) {
                                    Text("使用模板")
                                }
                                OutlinedButton(onClick = {
                                    val newList = templates.toMutableList()
                                    newList.remove(t)
                                    saveTemplates(newList)
                                }) {
                                    Text("删除")
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            title = { Text("新建模板") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(
                        value = newTemplateName,
                        onValueChange = { newTemplateName = it },
                        label = { Text("模板名称") },
                        singleLine = true
                    )
                    OutlinedTextField(
                        value = newTemplatePrompt,
                        onValueChange = { newTemplatePrompt = it },
                        label = { Text("提示词") },
                        maxLines = 4,
                        modifier = Modifier.height(120.dp)
                    )
                }
            },
            confirmButton = {
                Button(onClick = {
                    if (newTemplateName.isNotBlank() && newTemplatePrompt.isNotBlank()) {
                        val newList = templates.toMutableList()
                        newList.add(TemplateItem(newTemplateName, newTemplatePrompt))
                        saveTemplates(newList)
                        showDialog = false
                        newTemplateName = ""
                        newTemplatePrompt = ""
                    }
                }) {
                    Text("保存")
                }
            },
            dismissButton = {
                OutlinedButton(onClick = { showDialog = false }) {
                    Text("取消")
                }
            }
        )
    }
}
