from PIL import Image
import argparse

parser = argparse.ArgumentParser(description='Convert an RGB image to greyscale.')
parser.add_argument('filename', metavar='F', type=str, nargs='?',
                    help='filename')
args = parser.parse_args()
print args.filename


im = Image.open(args.filename)

iml = im.load()
width, height = im.size

print width,"x",height


im2 = Image.new("L",(width,height),color=0)
im2l = im2.load()

for x in xrange(1080):
	for y in xrange(1080):
		r = iml[x,y][0]*0.2125
		g = iml[x,y][1]*0.7154
		b = iml[x,y][2]*0.0721
		im2l[x,y] = int(r+g+b)

im2.save("image_greyscale.jpg")


