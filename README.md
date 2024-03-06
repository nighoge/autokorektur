# autokorektur (engl. car correction)

We are developing a program for the automated replacement of cars in images. 
First, a mask of the vehicles is generated through instance segmentation using YOLOv8. 
Subsequently, we use the latent diffusion model Stable-Diffusion-2 to generate the relevant areas of the image through inpainting, thus replacing the cars with a realistic background.

The resulting automated inpainting method is capable of replacing cars in a wide range of different images. This method is designed for speed, and we propose making it accessible through a mobile app. Our proposed app has been developed for Android and is designed to send images to a server and receive processed images from there. The image processing program runs on the server.

The results show that the method mostly achieves good to very good results, especially with high-quality images. 
The model encounters difficulties in generating a realistic image when removing many cars in parking lots or highways or when there are people in the foreground.

## Some Results
The images on the left side, the originals, are from <a href="https://www.pexels.com/public-domain-images">Pexels</a>. The right side shows the results of the developed method.
More results can be found in my <a href="https://drive.google.com/file/d/1QIU3FOuuQslF-sZeNLv26Pq_P9fbZWIM/view">bachelore thesis</a>. 

<div style="display:flex;">
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/pexels-faruk-tokluoğlu-7385403.jpg" alt="Original 1" width="400" />
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/result1.jpg" alt="Image 1" width="400" />
</div>

<div style="display:flex;">
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/pexels-harrison-haines-9957865.jpg" alt="Original 2" width="400" />
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/result2.jpg" alt="Image 2" width="400" />
</div>

<div style="display:flex;">
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/pexels-spencer-davis-4388221.jpg" alt="Original 3" width="400" />
    <img src="https://github.com/nighoge/autokorrektur/blob/main/images/downSized/result3.jpg" alt="Image 3" width="400" />
</div>


