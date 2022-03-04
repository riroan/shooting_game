import os

ls = os.listdir("images")
for i in ls:
    os.system(f"convert -strip images/{i} images/{i}")