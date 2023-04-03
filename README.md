# sd-webui-stopmotion
![ezgif com-crop](https://user-images.githubusercontent.com/2740936/229401064-f42c353b-9eae-47e6-97a5-036c5e40f418.gif)
Make a quick GIF animation using ControlNet to guide the frames in a stop motion pipeline

## Installation
Add this extension through the extensions tab, Install from URL and paste this repository URL: 

`https://github.com/gogodr/sd-webui-stopmotion` 

## Usage
- Select the script named Stop Motion CN and you will be able to configure the interface
- Select how many ControlNet Modules you want to use
- Select which ControlNet model you will use for each tab
- Add the corresponding frames for the animation **
- Click on generate and it will generate all the frames ***

** As a recomendation use numbered files (Ex: 1.png, 2.png, 3.png ...)

*** The individual frames will be saved as normal in the corresponding txt2img or img2img output folder, but only the gif will be shown then the processing is done. 

## TODO:
- Handle output FPS
- Handle batch img2img guide
- Handle ControlNet preprocessing
