package com.ttelectronics.scanner

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.Preview as CameraXPreview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.mlkit.vision.barcode.BarcodeScannerOptions
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.common.InputImage
import com.ttelectronics.scanner.ui.theme.ScannerTheme
import java.util.concurrent.atomic.AtomicBoolean

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            ScannerTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    val context = LocalContext.current
    var hasCameraPermission by remember { mutableStateOf(false) }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
    }

    LaunchedEffect(Unit) {
        val granted = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
        hasCameraPermission = granted
        if (!granted) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    var numericCode by rememberSaveable { mutableStateOf("") }
    var otherCode by rememberSaveable { mutableStateOf("") }
    var isScanning by rememberSaveable { mutableStateOf(false) }

    fun handleBarcode(value: String) {
        when {
            value.matches(Regex("^\\d{7}$")) -> {
                numericCode = value
            }
            else -> {
                otherCode = value
            }
        }
    }

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "Escáner de códigos de barra",
                style = MaterialTheme.typography.headlineSmall
            )

            if (hasCameraPermission) {
                CameraPreview(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(260.dp),
                    isScanning = isScanning,
                    onBarcodeDetected = { handleBarcode(it) }
                )
            } else {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(260.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text("Se requiere permiso de cámara.")
                        Button(onClick = {
                            permissionLauncher.launch(Manifest.permission.CAMERA)
                        }) {
                            Text("Conceder permiso")
                        }
                    }
                }
            }

            OutlinedTextField(
                value = numericCode,
                onValueChange = {},
                label = { Text("Código numérico (7 dígitos)") },
                readOnly = true,
                modifier = Modifier.fillMaxWidth()
            )

            OutlinedTextField(
                value = otherCode,
                onValueChange = {},
                label = { Text("Otro código") },
                readOnly = true,
                modifier = Modifier.fillMaxWidth()
            )

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(
                    onClick = {
                        numericCode = ""
                        otherCode = ""
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("Limpiar")
                }
                Button(
                    onClick = { isScanning = !isScanning },
                    modifier = Modifier.weight(1f)
                ) {
                    Text(if (isScanning) "Detener scanner" else "Activar scanner")
                }
            }
        }
    }
}

@Composable
fun CameraPreview(
    modifier: Modifier = Modifier,
    isScanning: Boolean,
    onBarcodeDetected: (String) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember { PreviewView(context) }
    val cameraProviderFuture = remember { ProcessCameraProvider.getInstance(context) }
    val imageAnalysis = remember {
        ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
    }
    val barcodeScanner = remember {
        val options = BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_CODE_128)
            .build()
        BarcodeScanning.getClient(options)
    }
    val executor = remember { ContextCompat.getMainExecutor(context) }
    val isProcessing = remember { AtomicBoolean(false) }

    DisposableEffect(lifecycleOwner, cameraProviderFuture) {
        val cameraProvider = cameraProviderFuture.get()
        val preview = CameraXPreview.Builder().build().apply {
            setSurfaceProvider(previewView.surfaceProvider)
        }
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
        cameraProvider.unbindAll()
        cameraProvider.bindToLifecycle(
            lifecycleOwner,
            cameraSelector,
            preview,
            imageAnalysis
        )

        onDispose {
            imageAnalysis.clearAnalyzer()
            barcodeScanner.close()
            cameraProvider.unbindAll()
        }
    }

    LaunchedEffect(isScanning) {
        if (isScanning) {
            imageAnalysis.setAnalyzer(executor) { imageProxy ->
                if (isProcessing.getAndSet(true)) {
                    imageProxy.close()
                    return@setAnalyzer
                }
                val mediaImage = imageProxy.image
                if (mediaImage != null) {
                    val inputImage = InputImage.fromMediaImage(
                        mediaImage,
                        imageProxy.imageInfo.rotationDegrees
                    )
                    barcodeScanner.process(inputImage)
                        .addOnSuccessListener { barcodes ->
                            barcodes
                                .asSequence()
                                .mapNotNull { it.rawValue }
                                .filter { it.isNotBlank() }
                                .take(2)
                                .forEach { onBarcodeDetected(it) }
                        }
                        .addOnFailureListener {
                            isProcessing.set(false)
                        }
                        .addOnCompleteListener {
                            isProcessing.set(false)
                            imageProxy.close()
                        }
                } else {
                    isProcessing.set(false)
                    imageProxy.close()
                }
            }
        } else {
            imageAnalysis.clearAnalyzer()
        }
    }

    AndroidView(
        factory = { previewView },
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    ScannerTheme {
        MainScreen()
    }
}
