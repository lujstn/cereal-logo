package com.lujstn.cereal.logo

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.provider.Settings
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.role
import androidx.compose.ui.semantics.semantics
import com.airbnb.lottie.compose.LottieAnimation
import com.airbnb.lottie.compose.LottieCompositionSpec
import com.airbnb.lottie.compose.LottieConstants
import com.airbnb.lottie.compose.animateLottieCompositionAsState
import com.airbnb.lottie.compose.rememberLottieComposition
import org.json.JSONObject

enum class CerealLogoVariant(val rawRes: Int) {
    FLOW(R.raw.cereal_inflate_flow),
    SPLIT(R.raw.cereal_inflate_split),
    BLOOM(R.raw.cereal_inflate_bloom),
}

enum class CerealLogoMode { FLOW, SPLIT, BLOOM, RANDOM }

private fun CerealLogoMode.resolved(): CerealLogoVariant = when (this) {
    CerealLogoMode.FLOW -> CerealLogoVariant.FLOW
    CerealLogoMode.SPLIT -> CerealLogoVariant.SPLIT
    CerealLogoMode.BLOOM -> CerealLogoVariant.BLOOM
    CerealLogoMode.RANDOM -> CerealLogoVariant.entries.random()
}

@Composable
fun CerealLogo(
    modifier: Modifier = Modifier,
    mode: CerealLogoMode = CerealLogoMode.RANDOM,
    loop: Boolean = false,
    speed: Float = 1f,
    respectReducedMotion: Boolean = true,
    haptics: Boolean = false,
    contentDescription: String = "Cereal",
) {
    val variant = remember(mode) { mode.resolved() }
    val composition by rememberLottieComposition(LottieCompositionSpec.RawRes(variant.rawRes))

    val context = LocalContext.current
    val reduceMotion = remember(respectReducedMotion) {
        respectReducedMotion && Settings.Global.getFloat(
            context.contentResolver,
            Settings.Global.ANIMATOR_DURATION_SCALE,
            1f,
        ) == 0f
    }

    val animatedProgress by animateLottieCompositionAsState(
        composition = composition,
        iterations = if (loop) LottieConstants.IterateForever else 1,
        speed = speed,
        isPlaying = !reduceMotion,
    )

    LaunchedEffect(variant) {
        if (haptics && !reduceMotion) playCerealHaptics(context, variant, speed)
    }

    val label = contentDescription
    LottieAnimation(
        composition = composition,
        progress = { if (reduceMotion) 1f else animatedProgress },
        modifier = modifier.semantics {
            this.contentDescription = label
            role = Role.Image
        },
    )
}

private fun cerealVibrator(context: Context): Vibrator? =
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        (context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager)?.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
    }

private fun loadTapTimes(context: Context, variant: CerealLogoVariant, rate: Float): List<Pair<Int, Float>>? {
    return try {
        val text = context.resources.openRawResource(R.raw.cereal_haptics)
            .bufferedReader().use { it.readText() }
        val events = JSONObject(text).getJSONObject(variant.name.lowercase()).getJSONArray("events")
        (0 until events.length()).map { i ->
            val event = events.getJSONObject(i)
            val atMs = (event.getDouble("t") / rate * 1000.0).toInt()
            atMs to event.getDouble("intensity").toFloat().coerceIn(0f, 1f)
        }
    } catch (e: Exception) {
        null
    }
}

private fun playCerealHaptics(context: Context, variant: CerealLogoVariant, speed: Float) {
    val vibrator = cerealVibrator(context) ?: return
    if (!vibrator.hasVibrator()) return
    val rate = if (speed > 0f) speed else 1f
    val taps = loadTapTimes(context, variant, rate)?.takeIf { it.isNotEmpty() } ?: return

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R &&
        vibrator.areAllPrimitivesSupported(VibrationEffect.Composition.PRIMITIVE_CLICK)
    ) {
        val composition = VibrationEffect.startComposition()
        var previous = 0
        for ((atMs, intensity) in taps) {
            composition.addPrimitive(
                VibrationEffect.Composition.PRIMITIVE_CLICK,
                intensity,
                (atMs - previous).coerceAtLeast(0),
            )
            previous = atMs
        }
        vibrator.vibrate(composition.compose())
        return
    }

    val timings = ArrayList<Long>()
    val amplitudes = ArrayList<Int>()
    var previous = 0
    for ((atMs, intensity) in taps) {
        timings.add((atMs - previous).coerceAtLeast(0).toLong())
        amplitudes.add(0)
        timings.add(18L)
        amplitudes.add((intensity * 255).toInt().coerceIn(1, 255))
        previous = atMs + 18
    }
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        vibrator.vibrate(VibrationEffect.createWaveform(timings.toLongArray(), amplitudes.toIntArray(), -1))
    } else {
        @Suppress("DEPRECATION")
        vibrator.vibrate(timings.toLongArray(), -1)
    }
}
