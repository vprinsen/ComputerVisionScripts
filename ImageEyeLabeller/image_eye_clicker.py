import tkinter as Tk
from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image
import os

# Create empty list for coordinate arrays to be appended to
coords = []
eyes=[]

# Function to be called when mouse is clicked
def save_coords(event):
	global canvas
	click_loc = [event.x, event.y]
	print("you clicked on", click_loc)
	coords.append(click_loc)
	canvas.target = Tk.PhotoImage(file='target-center-red.gif')
	canvas.create_image(event.x, event.y, anchor=Tk.CENTER, image=canvas.target)
#	point = canvas.create_line(event.x-2, event.y-2, event.x+2, event.y+2, fill="red")
# save 2 eyes - on third click, erase 2 eyes and start over
# keep list (or other data structure) containing created images? look up how tkinter wants this
# how to erase previous eyes?
# must erase eyes when changing image, too --v

# Function to load the next image into the canvas
def next_img():
	global coords
	print(coords)
	coords=[]
	f = next(imgs)
	if(f.endswith(('.jpg','.gif','.png'))):
		img = Image.open(f)
		if img.size[1] > window_height:		
			resize_height = int(window_height*0.9)
			resize_width = int(img.size[0] * (resize_height/img.size[1]))
			img = img.resize((resize_width,resize_height), Image.ANTIALIAS)
		if img.size[0] > window_width:		
			resize_width = int(window_width*0.9)
			resize_height = int(img.size[1] * (resize_width/img.size[0]))
			img = img.resize((resize_width,resize_height), Image.ANTIALIAS)
		canvas.img = ImageTk.PhotoImage(img)  # PIL solution
		image = canvas.create_image(0, 0, anchor=Tk.NW, image=canvas.img)
	else:
		next_img()


root = Tk.Tk()

# choose directory
img_dir = askdirectory(parent=root, initialdir="/Users/username/Desktop/ImageDataset/", title='Choose folder')
os.chdir(img_dir)
imgs = iter(os.listdir(img_dir))

# setup canvas
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width*0.66)
window_height = int(screen_height*0.66)

canvas = Tk.Canvas(root)
canvas.pack(fill=Tk.BOTH, expand=1) # Stretch canvas to root window size.
root.wm_geometry("%dx%d" % (window_width, window_height))
root.title('Eye clicker v0.1')

canvas.bind("<Button-1>",save_coords)

btn = Tk.Button(root, text='Next image', command=lambda: next_img())
btn.pack()

next_img() # load first image

root.mainloop()

print(coords)