package com.example.autokorekturv2

import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface APIService {
    @POST("/api/v1/images/upload?image_category=general&is_intermediate=true&crop_visible=false")
    suspend fun postImage(@Body requestBody: RequestBody): Response<ResponseBody>

    @GET("/get")// api/v1/images/?offset=0&limit=10
    suspend fun getNumberOfPicturesOnServer(): Response<ResponseBody>

}