from donut import DonutModel
from PIL import Image

# let's test our solution

model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")

model.eval() 
image = Image.open("./receipt_test.jpg").convert("RGB")
output = model.inference(image=image, prompt="<s_cord-v2>")

print(output)