# autokorektur

We are developing a program for the automated replacement of cars in images. 
First, a mask of the vehicles is generated through instance segmentation using YOLOv8. 
Subsequently, we use the latent diffusion model Stable-Diffusion-2 to generate the relevant areas of the image through inpainting, thus replacing the cars with a realistic background.

The resulting automated inpainting method is capable of replacing cars in a wide range of different images. This method is designed for speed, and we propose making it accessible through a mobile app. Our proposed app has been developed for Android and is designed to send images to a server and receive processed images from there. The image processing program runs on the server.

The results show that the method mostly achieves good to very good results, especially with high-quality images. 
The model encounters difficulties in generating a realistic image when removing many cars in parking lots or highways or when there are people in the foreground.

## Some Results
The images form the left side, the originals, arefrom the ...

![Image 1](https://github.com/nighoge/autokorrektur/blob/main/images/1702998611.png)
<p>Image 1</p>

![Image 2](images/result1.png)
<p>Image 2</p>

