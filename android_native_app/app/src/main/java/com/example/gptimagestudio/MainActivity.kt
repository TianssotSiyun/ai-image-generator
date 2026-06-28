package com.example.gptimagestudio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.example.gptimagestudio.theme.GPTImageStudioTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            GPTImageStudioTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    MainAppScaffold()
                }
            }
        }
    }
}

@Composable
fun MainAppScaffold() {
    val context = LocalContext.current
    val prefs = remember { PreferencesManager(context) }
    var currentTab by remember { mutableStateOf(0) }
    
    var referenceImageInternal by remember { mutableStateOf<String?>(null) }
    var templatePrompt by remember { mutableStateOf<String?>(null) }

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = MaterialTheme.colorScheme.surface.copy(alpha = 0.8f)
            ) {
                NavigationBarItem(
                    selected = currentTab == 0,
                    onClick = { currentTab = 0 },
                    icon = { Text("🛠", style = MaterialTheme.typography.titleMedium) },
                    label = { Text("生成图像") }
                )
                NavigationBarItem(
                    selected = currentTab == 1,
                    onClick = { currentTab = 1 },
                    icon = { Text("🖼", style = MaterialTheme.typography.titleMedium) },
                    label = { Text("内部图库") }
                )
                NavigationBarItem(
                    selected = currentTab == 2,
                    onClick = { currentTab = 2 },
                    icon = { Text("📝", style = MaterialTheme.typography.titleMedium) },
                    label = { Text("模板") }
                )
            }
        }
    ) { innerPadding ->
        Modifier.padding(innerPadding)
        
        when (currentTab) {
            0 -> GenerateScreen(
                    prefs = prefs,
                    referenceImageInternal = referenceImageInternal,
                    templatePrompt = templatePrompt,
                    onClearReference = { referenceImageInternal = null },
                    onClearTemplate = { templatePrompt = null }
                )
            1 -> GalleryScreen(
                    onImageSelected = { path ->
                        referenceImageInternal = path
                        currentTab = 0 // Switch back to generate screen
                    }
                )
            2 -> TemplatesScreen(
                    prefs = prefs,
                    onUseTemplate = { prompt ->
                        templatePrompt = prompt
                        currentTab = 0
                    }
                )
        }
    }
}
