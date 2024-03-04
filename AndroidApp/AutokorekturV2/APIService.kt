package com.example.autokorekturv2

import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Streaming

interface APIService {
    @Multipart
    @POST("/upload")
    suspend fun uploadImage(@Part image: MultipartBody.Part): Response<UploadResponse>

    @GET("download/{filename}")
    @Streaming
    suspend fun downloadImage(@Path("filename") filename: String): Response<ResponseBody>
}