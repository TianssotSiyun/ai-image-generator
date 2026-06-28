package com.example.gptimagestudio.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.graphics.Color

private val DarkColorScheme = darkColorScheme(
    primary = AeroPurple,
    secondary = AeroPurpleLight,
    tertiary = AeroPurpleDark,
    background = BackgroundPurpleDark,
    surface = SurfacePurpleDark,
    onPrimary = Color.White,
    onSecondary = Color.White,
    onBackground = TextPrimaryPurpleDark,
    onSurface = TextPrimaryPurpleDark
)

private val LightColorScheme = lightColorScheme(
    primary = AeroCyanDark,
    secondary = AeroGreenDark,
    tertiary = AeroCyan,
    background = BackgroundCyanLight,
    surface = BackgroundCyanLight,
    onPrimary = TextPrimaryLight,
    onSecondary = TextPrimaryLight,
    onBackground = TextPrimaryLight,
    onSurface = TextPrimaryLight
)

@Composable
fun GPTImageStudioTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false, // Disable dynamic colors to keep Aero vibe
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(colorScheme = colorScheme, typography = Typography, content = content)
}
