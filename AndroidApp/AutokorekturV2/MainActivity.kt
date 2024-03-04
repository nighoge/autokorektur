package com.example.autokorekturv2


import android.content.Context
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.media.MediaScannerConnection
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.Log
import android.view.WindowManager
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.StringRes
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.wrapContentSize
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.autokorekturv2.ui.theme.AutokorekturV2Theme
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN, WindowManager.LayoutParams.FLAG_FULLSCREEN)
        setContent {
            AutokorekturV2Theme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    AutokorekturApp()
                }
            }
        }
    }
}

@Composable
fun AutokorekturApp() {
    LoadLayout(modifier = Modifier
        .fillMaxSize()
        .wrapContentSize(Alignment.Center))
}

@Composable
fun LoadLayout(modifier: Modifier) {
    var imageUri by remember {
        mutableStateOf<Uri?>(null)
    }
    val context = LocalContext.current
    val bitmap =  remember {
        mutableStateOf<Bitmap?>(null)
    }

    val launcher = rememberLauncherForActivityResult(contract =
    ActivityResultContracts.GetContent()) { uri: Uri? ->
        imageUri = uri
    }


    val url = "http://192.168.40.118:5000"
    val gson: Gson = GsonBuilder().setLenient().create()
    val retrofit = Retrofit.Builder()
        .baseUrl(url)
        .addConverterFactory(GsonConverterFactory.create(gson))
        .build()
        .create(APIService::class.java)

    Column(modifier = modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        imageUri?.let {
            if (Build.VERSION.SDK_INT < 28) {
                bitmap.value = MediaStore.Images
                    .Media.getBitmap(context.contentResolver,it)

            } else {
                try {
                    val source = ImageDecoder
                        .createSource(context.contentResolver,it)
                    bitmap.value = ImageDecoder.decodeBitmap(source)
                } catch (e: Exception) {
                    Log.e("LoadLayout", "Error loading layout:", e)
                    showMessage(context, R.string.errorLoadImage)
                }
            }

            bitmap.value?.let {  btm ->
                Image(bitmap = btm.asImageBitmap(),
                    contentDescription =null,
                    modifier = Modifier.size(400.dp))
            }
        }

        Button(
            onClick = { launcher.launch("image/*") }
        ) {
            Text(text = stringResource(R.string.gallery), fontSize = 24.sp)
        }
        val context = LocalContext.current
        Button(
            onClick = {
                if (bitmap.value != null) {
                    showMessage(context=context, message = R.string.uploadToast)
                    uploadImage(retrofit=retrofit, bitmap=bitmap)

                    downloadResult(retrofit=retrofit, context=context, delay=true)
                } else {
                    showMessage(context = context, message = R.string.chooseImage)
                }
            }
            //modifier.align(alignment = Alignment.End).padding(5.dp)
        ) {
            Text(text = stringResource(R.string.send), fontSize = 24.sp)
        }

    }
}


fun showMessage(context: Context, @StringRes message: Int){
    val message = context.getString(message)
    val handler = Handler(Looper.getMainLooper())
    handler.post {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

}

fun uploadImage(retrofit: APIService, bitmap: MutableState<Bitmap?>) {
    CoroutineScope(Dispatchers.IO).launch {
        try {
            val bitmap: Bitmap? = bitmap.value
            if (bitmap != null) {
                val imageFile = convertBitmapToRequestBody(bitmap)
                val uploadResponse = retrofit.uploadImage(
                    MultipartBody.Part.createFormData("image", "image.jpg", imageFile)
                )
                if (uploadResponse.isSuccessful) {
                    Log.d("Upload","Upload of the image executed")
                }
            }

        } catch (e: Exception) {
            Log.d("Upload","Exception while uploading the image: ", e)
        }
    }
}


private const val FILE_NAME = "result"
private const val FILE_EXTENSION = ".jpg"
private const val MAX_RETRY_COUNT = 30
private const val RETRY_DELAY_MS = 5000L // 5 seconds

fun downloadResult(retrofit: APIService, context: Context, delay: Boolean) {

    CoroutineScope(Dispatchers.IO).launch {
        if (delay) {
            delay(35000)
        }
        var retryCount = 0
        var downloadSuccessful = false

        while (retryCount < MAX_RETRY_COUNT && !downloadSuccessful) {
            try {
                val downloadResponse = retrofit.downloadImage("$FILE_NAME$FILE_EXTENSION")

                if (downloadResponse.isSuccessful) {
                    showMessage(context=context, message = R.string.downloadToast)
                    val headers = downloadResponse.headers()
                    Log.d("Download", "Response Headers: $headers")

                    val body = downloadResponse.body()
                    if (body != null) {
                        saveImageToDownloadFolder(body, context, FILE_NAME)
                        downloadSuccessful = true

                        val filePath = context.getExternalFilesDir(null)?.absolutePath + File.separator + FILE_NAME + FILE_EXTENSION
                        MediaScannerConnection.scanFile(context, arrayOf(filePath), null) { _, _ ->
                            Log.d("MediaScanner", "Scanned $filePath")
                        }
                    } else {
                        Log.d("Download", "Body of the response is null")
                    }
                } else {
                    Log.d("Download", "Download not successful, retrying in ${RETRY_DELAY_MS / 1000} seconds.")
                    delay(RETRY_DELAY_MS)
                    retryCount++
                }
            } catch (e: Exception) {
                Log.e("Download", "Exception while downloading the result: ", e)
            }
        }
    }
}

private fun saveImageToDownloadFolder(responseBody: ResponseBody, context: Context, filename: String) {
    try {
        if (Environment.getExternalStorageState() == Environment.MEDIA_MOUNTED) {
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)

            val timestamp = System.currentTimeMillis()
            val formattedDate = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date(timestamp))
            val newFilename = "$filename$formattedDate$FILE_EXTENSION"

            val file = File(downloadsDir, newFilename)

            val bufferSize = 8192
            responseBody.byteStream().use { input ->
                FileOutputStream(file).use { output ->
                    input.copyTo(output, bufferSize)
                }
            }


            MediaScannerConnection.scanFile(context, arrayOf(file.absolutePath), null) { _, _ ->
                Log.d("MediaScanner", "Scanned ${file.absolutePath}")
            }

            Log.d("Download", "Download successful. Image saved to: ${file.absolutePath}")
        } else {
            Log.e("Download", "External storage not available")
        }
    } catch (e: IOException) {
        Log.e("Download", "Exception while saving the image to the Downloads folder: ", e)
    }
}



private fun convertBitmapToRequestBody(bitmap: Bitmap): RequestBody {
    val byteArrayOutputStream = ByteArrayOutputStream()
    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, byteArrayOutputStream)
    return RequestBody.create("image/jpeg".toMediaType(), byteArrayOutputStream.toByteArray())
}



@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    AutokorekturV2Theme {
        AutokorekturApp()
    }
}