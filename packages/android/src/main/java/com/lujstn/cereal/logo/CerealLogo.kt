package com.lujstn.cereal.logo

import android.provider.Settings
import androidx.compose.runtime.Composable
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
