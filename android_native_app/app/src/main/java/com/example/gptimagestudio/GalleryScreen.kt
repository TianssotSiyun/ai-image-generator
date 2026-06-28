package com.example.gptimagestudio

import android.graphics.BitmapFactory
import android.widget.Toast
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.example.gptimagestudio.ui.components.glassmorphism
import kotlinx.coroutines.launch
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GalleryScreen(
    onImageSelected: (String) -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var historyItems by remember { mutableStateOf(emptyList<HistoryItem>()) }
    var selectedItem by remember { mutableStateOf<HistoryItem?>(null) }
    var dialogImageIndex by remember { mutableStateOf(0) }
    
    // Refresh images
    LaunchedEffect(Unit) {
        historyItems = StorageManager.getInternalHistory(context)
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(8.dp)
    ) {
        if (historyItems.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text("暂无生成的图片历史。", color = Color.Gray)
            }
        } else {
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                contentPadding = PaddingValues(8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(historyItems) { item ->
                    if (item.isImageDeleted) {
                        Box(
                            modifier = Modifier
                                .aspectRatio(1f)
                                .clip(RoundedCornerShape(8.dp))
                                .background(Color.DarkGray)
                                .clickable { selectedItem = item },
                            contentAlignment = Alignment.Center
                        ) {
                            Column(
                                modifier = Modifier.padding(8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Text("已删除", color = Color.LightGray, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    item.prompt,
                                    color = Color.Gray,
                                    fontSize = 10.sp,
                                    maxLines = 3,
                                    overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
                                )
                            }
                        }
                    } else {
                        val firstFile = item.imageFiles.firstOrNull { it.exists() }
                        val bitmap = remember(firstFile?.absolutePath) {
                            if (firstFile != null) BitmapFactory.decodeFile(firstFile.absolutePath) else null
                        }
                        if (bitmap != null) {
                            Image(
                                bitmap = bitmap.asImageBitmap(),
                                contentDescription = "Gallery Image",
                                contentScale = ContentScale.Crop,
                                modifier = Modifier
                                    .aspectRatio(1f)
                                    .clip(RoundedCornerShape(8.dp))
                                    .clickable { 
                                        selectedItem = item
                                        dialogImageIndex = 0
                                    }
                            )
                        } else {
                            Box(
                                modifier = Modifier
                                    .aspectRatio(1f)
                                    .clip(RoundedCornerShape(8.dp))
                                    .background(Color.DarkGray)
                                    .clickable { selectedItem = item },
                                contentAlignment = Alignment.Center
                            ) {
                                Text("图片损坏", color = Color.LightGray, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
        }
    }

    if (selectedItem != null) {
        val item = selectedItem!!
        val existingFiles = item.imageFiles.filter { it.exists() }
        
        Dialog(onDismissRequest = { selectedItem = null }) {
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
                    .glassmorphism(),
                color = Color.Transparent
            ) {
                Column(
                    modifier = Modifier.padding(16.dp).verticalScroll(androidx.compose.foundation.rememberScrollState()),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    if (item.isImageDeleted || existingFiles.isEmpty()) {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(200.dp)
                                .clip(RoundedCornerShape(8.dp))
                                .background(Color.DarkGray),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("图片文件已从磁盘删除", color = Color.LightGray)
                        }
                    } else {
                        val currentFile = existingFiles.getOrNull(dialogImageIndex) ?: existingFiles[0]
                        val bitmap = remember(currentFile.absolutePath) {
                            BitmapFactory.decodeFile(currentFile.absolutePath)
                        }
                        if (bitmap != null) {
                            Image(
                                bitmap = bitmap.asImageBitmap(),
                                contentDescription = "Full Image",
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clip(RoundedCornerShape(8.dp)),
                                contentScale = ContentScale.Fit
                            )
                        }
                        
                        if (existingFiles.size > 1) {
                            Spacer(modifier = Modifier.height(8.dp))
                            LazyRow(
                                modifier = Modifier.fillMaxWidth().height(50.dp),
                                horizontalArrangement = Arrangement.spacedBy(8.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                items(existingFiles.size) { idx ->
                                    val f = existingFiles[idx]
                                    val bmp = remember(f.absolutePath) { BitmapFactory.decodeFile(f.absolutePath) }
                                    if (bmp != null) {
                                        val isSelected = idx == dialogImageIndex
                                        Box(
                                            modifier = Modifier
                                                .size(40.dp)
                                                .clip(RoundedCornerShape(4.dp))
                                                .background(if (isSelected) MaterialTheme.colorScheme.primary else Color.Transparent)
                                                .padding(if (isSelected) 2.dp else 0.dp)
                                                .clickable { dialogImageIndex = idx }
                                        ) {
                                            Image(
                                                bitmap = bmp.asImageBitmap(),
                                                contentDescription = "Thumb",
                                                contentScale = ContentScale.Crop,
                                                modifier = Modifier.fillMaxSize().clip(RoundedCornerShape(4.dp))
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Column(modifier = Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("📜 提示词: ${item.prompt}", style = MaterialTheme.typography.bodySmall)
                        Text("🤖 模型: ${item.model}", style = MaterialTheme.typography.bodySmall)
                        Text("📐 尺寸: ${item.size} | 💎 质量: ${item.quality}", style = MaterialTheme.typography.bodySmall)
                        if (item.apiUrl.isNotEmpty()) {
                            Text("🌐 接口: ${item.apiUrl}", style = MaterialTheme.typography.bodySmall)
                        }
                        if (item.duration.isNotEmpty() || item.totalTokens > 0) {
                            Text("⚡ 耗时: ${item.duration} | 🪙 Token: 输入 ${item.promptTokens} / 输出 ${item.completionTokens} (总计 ${item.totalTokens})", style = MaterialTheme.typography.bodySmall)
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (existingFiles.isNotEmpty()) {
                        val currentFile = existingFiles.getOrNull(dialogImageIndex) ?: existingFiles[0]
                        Button(
                            onClick = {
                                scope.launch {
                                    val res = StorageManager.saveImageToMediaStore(context, currentFile)
                                    if (res.isSuccess) {
                                        Toast.makeText(context, "已保存到系统相册！", Toast.LENGTH_SHORT).show()
                                    } else {
                                        Toast.makeText(context, "保存失败", Toast.LENGTH_SHORT).show()
                                    }
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("保存到手机相册")
                        }
                        
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Button(
                            onClick = {
                                onImageSelected(currentFile.absolutePath)
                                selectedItem = null
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("设为图生图参考")
                        }
                        
                        Spacer(modifier = Modifier.height(8.dp))
                    }
                    
                    OutlinedButton(
                        onClick = {
                            item.imageFiles.forEach { StorageManager.deleteInternalImage(it) }
                            val metaFile = java.io.File(context.filesDir, "gpt_images/${item.id}.json")
                            StorageManager.deleteInternalImage(metaFile)
                            historyItems = StorageManager.getInternalHistory(context)
                            selectedItem = null
                            Toast.makeText(context, "已删除记录", Toast.LENGTH_SHORT).show()
                        },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Red)
                    ) {
                        Text("删除历史")
                    }

                    Spacer(modifier = Modifier.height(8.dp))

                    OutlinedButton(
                        onClick = { selectedItem = null },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("关闭")
                    }
                }
            }
        }
    }
}
