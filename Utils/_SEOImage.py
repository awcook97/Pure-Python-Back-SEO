__name__ = "_SEOImage"
from typing import Any
from PIL import Image, ImageDraw, ImageFont
import random, requests, os

def init_SEOImage(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix

def cleanFilename(s):
	if not s:
		return ''
	badchars = '\\/:*?\"\'<>|'
	for c in badchars:
		s = s.replace(c, '')
	return s
clList = '''dark_blue, grey, light_blue, blue, orange, purple, red, yellow, yellow_green, green'''
COLORS = {
    'dark_blue': {'c': (27, 53, 81), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
    'grey': {'c': (70, 86, 95), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(93,188,210)'},
    'light_blue': {'c': (93, 188, 210), 'p_font': 'rgb(27,53,81)', 's_font': 'rgb(255,255,255)'},
    'blue': {'c': (23, 114, 237), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 255, 255)'},
    'orange': {'c': (242, 174, 100), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'purple': {'c': (114, 88, 136), 'p_font': 'rgb(255,255,255)', 's_font': 'rgb(255, 212, 55)'},
    'red': {'c': (255, 0, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'yellow': {'c': (255, 255, 0), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(27,53,81)'},
    'yellow_green': {'c': (232, 240, 165), 'p_font': 'rgb(0,0,0)', 's_font': 'rgb(0,0,0)'},
    'green': {'c': (65, 162, 77), 'p_font': 'rgb(217, 210, 192)', 's_font': 'rgb(0, 0, 0)'}
}
def pullPixa(search_term, api_key):
    # Build the URL
    #api_key = None
    url = f'https://pixabay.com/api/?key={api_key}&q={search_term}&image_type=photo&per_page=200'

    # Make the request
    response = requests.get(url)

    # Convert the response to JSON
    data = response.json()

    # Get the image URLs
    image_urls = [image['largeImageURL'] for image in data['hits']]
    imgIDs = [image['id'] for image in data['hits']]
    # Download the images
    i = random.randint(0, len(image_urls)-1)
    url = image_urls[i]
    #filename = f"{search_term}_{imgIDs[i]}.{url.split('.')[-1]}".replace('/', '-')
    filePath = f"output/images/{cleanFilename(search_term)}.{url.split('.')[-1]}"
    #fullFilePath = f"{filePath}\\{filename}"
    download_image(url, filePath)
    return filePath


def seoImage(search_term: str, article_title: str, api_key: str):
    baseImg = pullPixa(search_term, api_key)
    #masked = mask_image(baseImg, randomImage)
    newImgName = f"{article_title.replace(' ', '_')}.png"
    titleWordCount = len(article_title.split(' '))
    halfwayTitle = int(titleWordCount/2)
    artTitle = ['','']
    split_artTitle = article_title.split(' ')
    for words in range(0,len(split_artTitle)):
        if words < halfwayTitle:
            artTitle[0] += split_artTitle[words] + ' '
        else:
            artTitle[1] += split_artTitle[words] + ' '
    SEOImage = WrittenImage(
        bgPath=baseImg,
        img_name=newImgName,
        text1=artTitle[0],
        text2=artTitle[1],
        color='rand',
        fontsize=22
    )
    SEOImage.save_image()
    #print(SEOImage.img_name)
    return f'{SEOImage.img_name}'

def download_image(url, saveas):
    response = requests.get(url)
    if response.status_code == 200:
        with open(saveas, 'wb') as f:
            f.write(response.content)


class WrittenImage():
    """A class that creates and saves an Image object with text and a mask over it."""

    def __init__(self, bgPath: str, img_name: str, text1: str, text2: str, fgPath: str = '', fontsize: int = 45, colors: dict[str, dict[str, Any]] = COLORS, font: str = 'Fonts/Roboto-Bold.ttf', color: str = 'blue', imgLayer: str = None):
        """
        __init__ initializes the WrittenImage class


        Args:
            bgPath (str): Image path used as the background
            img_name (str): Name of the output image
            text1 (str): Top text
            text2 (str): Bottom Text
            fgPath (str): Logo image path. Optional.
            fontsize (int, optional): Size of the text. Defaults to 45.
            colors (dict[str, dict[str, Any]]): Dictionary of colors written as: 'color_name':{'c':(int, int, int), 'p_font':'rgb(int, int, int)','s_font':'rgb(int, int, int)'},
            font (str, optional): Style of font, must download additional fonts. Defaults to 'Fonts/Roboto-Bold.ttf'.
            color (str): Color that you chose. Defaults to 'blue'
            imgLayer (str): Image path to be used as a layer. Optional.
        """
        self.bgPath = bgPath
        self.fgPath = fgPath
        self.img_name = img_name
        self.text1 = text1
        self.text2 = text2
        self.fontsize = fontsize
        self.colors = colors
        self.font = font
        self.color = color
        if self.color == 'rand': self.color = random.choice(clList.split(', '))
        self.background = Image.open(self.bgPath)
        if self.fgPath:
            self.foreground = Image.open(self.fgPath)
        self.imgLayer = imgLayer

    def add_color(self, image, c, transparency, imgLayer = None):
        color = Image.new('RGB', image.size, c)
        mask = Image.new('RGBA', image.size, (0, 0, 0, transparency))
        if imgLayer: 
            imgLayer = Image.open(imgLayer)
            imgLayer = imgLayer.resize(image.size)
            imgLayer.putalpha(int(255 * (0.01 * transparency)))
            mask = imgLayer
        return Image.composite(image, color, mask).convert('RGB')

    def center_text(self, img, font, text1, text2, fill1, fill2):
        draw = ImageDraw.Draw(img)
        w, h = img.size
        t1_width = draw.textlength(text1, font)
        t2_width = draw.textlength(text2, font)
        p1 = ((w-t1_width)/2, h // 3)
        p2 = ((w-t2_width)/2, h // 3 + h // 5)
        draw.text(p1, text1, fill=fill1, font=font)
        draw.text(p2, text2, fill=fill2, font=font)
        return img
    
    def calcfontsize(self, img, font='Fonts/Roboto-Bold.ttf', font_size=45, text1='', text2=''):
        w, h = img.size
        myFont = ImageFont.FreeTypeFont(font, size=font_size)
        ts1 = myFont.getlength(text1)
        ts2 = myFont.getlength(text2)
        while ts1 > w or ts2 > w:
            font_size -= 1
            myFont = ImageFont.truetype(font, size=font_size)
            ts1 = myFont.getlength(text1)
            ts2 = myFont.getlength(text2)
        return font_size -2
        

    def add_text(self, img, color, text1, text2, logo=False, font='Fonts/Roboto-Bold.ttf', font_size=45):
        draw = ImageDraw.Draw(img)

        p_font = self.colors[color]['p_font']
        s_font = self.colors[color]['s_font']

        # starting position of the message
        img_w, img_h = img.size
        height = img_h // 3
        font = ImageFont.truetype(font, size=self.calcfontsize(img, font, font_size, text1, text2))

        if logo == False:
            self.center_text(img, font, text1, text2, p_font, s_font)
        else:
            text1_offset = (img_w // 4, height)
            text2_offset = (img_w // 4, height + img_h // 5)
            draw.text(text1_offset, text1, fill=p_font, font=font)
            draw.text(text2_offset, text2, fill=s_font, font=font)
        return img

    def add_logo(self, background: Image, foreground: Image) -> Image:
        bg_w, bg_h = background.size
        img_w, img_h = foreground.size
        img_offset = (20, (bg_h - img_h) // 2)
        background.paste(foreground, img_offset, foreground)
        return background

    def write_image(self, background, color, text1, text2, foreground=''):
        background = self.add_color(background, self.colors[color]['c'], 80, self.imgLayer)
        if not foreground:
            self.add_text(background, color, text1, text2)
        else:
            self.add_text(background, color, text1, text2, logo=True)
            self.add_logo(background, foreground)
        return background

    def save_image(self):
        self.background = self.write_image(
            self.background, self.color, self.text1, self.text2, foreground=self.fgPath)
        self.background.save(f'output/images/{cleanFilename(self.img_name)}')
#seoImage('dog', "This Dog", "261")

def __init__():
    pass
def __main__(*args):
    seoImage("Dog", "Doggie", None)