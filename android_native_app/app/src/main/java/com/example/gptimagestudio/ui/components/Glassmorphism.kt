package com.example.gptimagestudio.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.gptimagestudio.theme.GlassDark
import com.example.gptimagestudio.theme.GlassWhite
import com.example.gptimagestudio.theme.GlassBorderDark
import com.example.gptimagestudio.theme.GlassBorderLight

fun Modifier.glassmorphism(): Modifier = composed {
    val isDark = isSystemInDarkTheme()
    val glassColor = if (isDark) GlassDark else GlassWhite
    val borderColor = if (isDark) GlassBorderDark else GlassBorderLight

    this
        .clip(RoundedCornerShape(16.dp))
        .background(
            Brush.linearGradient(
                colors = listOf(glassColor, glassColor.copy(alpha = glassColor.alpha * 0.5f))
            )
        )
        .border(
            width = 1.dp,
            brush = Brush.linearGradient(
                colors = listOf(borderColor, borderColor.copy(alpha = 0f))
            ),
            shape = RoundedCornerShape(16.dp)
        )
}
