from PIL import ImageGrab, Image
ImageGrab.grab().save("foutput.png")
myImg=Image.open("output.png")
myImg.
myImg.show()
newImg = myImg.crop((0,0,100,100))
newImg.save("output.png")
newImg.show()