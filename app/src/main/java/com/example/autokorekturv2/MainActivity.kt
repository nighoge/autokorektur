package com.example.autokorekturv2

import android.content.Context
import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
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
import com.google.gson.GsonBuilder
import com.google.gson.JsonParser
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.RequestBody
import retrofit2.Retrofit

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
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

    Column(modifier = modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        /*Image(painter = painterResource(R.drawable.imagecar),
            contentDescription = stringResource(R.string.imagedescription)
        )*/
        imageUri?.let {
            if (Build.VERSION.SDK_INT < 28) {
                bitmap.value = MediaStore.Images
                    .Media.getBitmap(context.contentResolver,it)

            } else {
                val source = ImageDecoder
                    .createSource(context.contentResolver,it)
                bitmap.value = ImageDecoder.decodeBitmap(source)
            }

            bitmap.value?.let {  btm ->
                Image(bitmap = btm.asImageBitmap(),
                    contentDescription =null,
                    modifier = Modifier.size(400.dp))
            }
        }

        Button(
            onClick = { launcher.launch("image/*") }
            //modifier.padding(5.dp)
        ) {
            Text(text = stringResource(R.string.gallery), fontSize = 24.sp)
        }
        val context = LocalContext.current
        Button(
            onClick = {
                numberOfPicturesOnServer()
                showMessage(context=context, message = R.string.toast)
            }
            //modifier.align(alignment = Alignment.End).padding(5.dp)
        ) {
            Text(text = stringResource(R.string.send), fontSize = 24.sp)
        }

    }
}

fun showMessage(context: Context, @StringRes message: Int){
    val message = context.getString(message)
    Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
}

fun send() {

}

fun numberOfPicturesOnServer() {

    // Create Retrofit
    val retrofit = Retrofit.Builder()
        .baseUrl("https://httpbin.org")// http://192.168.2.108:9090/
        .build()

    // Create Service
    val getRequest = retrofit.create(APIService::class.java)

    CoroutineScope(Dispatchers.IO).launch {

        val response = getRequest.getNumberOfPicturesOnServer()

        withContext(Dispatchers.Main) {
            /*if (response.isSuccessful) {

                // Convert raw JSON to pretty JSON using GSON library
                val gson = GsonBuilder().setPrettyPrinting().create()
                val json = gson.toJson(
                    JsonParser.parseString(
                        response.body()
                            ?.string() // About this thread blocking annotation : https://github.com/square/retrofit/issues/3255
                    )
                )
                val total = json.get(-1).toString()
                Log.d("Total Images: ", total)

            }
            Log.e("RETROFIT_ERROR", response.code().toString())*/

        }
    }
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    AutokorekturV2Theme {
        AutokorekturApp()
    }
}