from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from tempfile import NamedTemporaryFile


def v_key() -> tuple:
    font_path = 'media/CENTAUR.TTF'
    cnt = 4
    size = (95, 32)
    height, width = size
    bgcolor = (255, 255, 255)
    fontcolor = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
    li_le_str = 'abcdefghjkmnopqrstuvwxyz'
    up_le_str = li_le_str.upper()
    nu_str = '0123456789'
    the_str = li_le_str + up_le_str + nu_str
    img = Image.new('RGBA', (height, width), bgcolor)
    font = ImageFont.truetype(font_path, 22)
    draw = ImageDraw.Draw(img)
    text = '%s' % ' '.join(random.sample(the_str, 4))
    # text = text.join(' ')
    font_h, font_w = font.getsize(text)
    # line(width, height, size, draw)
    draw.text(((width - font_w) / 3, (height - font_h) / 40), text, font=font, fill=fontcolor[random.randint(0, 2)])
    xyz = [1 - random.uniform(-0.1, 0.1), 0, 0, 0, 1 - random.uniform(-0.1, 0.1), random.uniform(-0.009, 0.008), 0.001,
           random.uniform(0, 0.007)]
    img = img.transform(size, Image.PERSPECTIVE, xyz)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    text = ''.join(text.split(' '))
    f = NamedTemporaryFile()
    img.save(f, format='png')
    f.seek(0)
    img = f.read()
    f.close()
    return (text, img)
