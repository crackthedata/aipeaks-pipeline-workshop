from metaflow import step, FlowSpec, S3, kubernetes, catch, batch, schedule, retry
from donut import DonutModel
from PIL import Image

#@schedule(hourly=True)
class ExtractionFlow(FlowSpec):

    @step
    def start(self):
        with S3(s3root='s3://aipeaks-demo/') as s3:
            urls = [obj.url for obj in s3.list_paths(['test_images'])]
            #urls = [obj.url for obj in s3.list_paths(['lotsa_images'])]
            self.images = [img_url for img_url in urls if img_url.endswith('.jpg')]

        self.next(self.process, foreach='images')

    #@batch(queue='job-queue-aipeaks', cpu=8, memory=16000, image="docker.io/crackthedata/aipeaks-k8s:v1")
    #@kubernetes()
    @catch
    @retry(times=10, minutes_between_retries=3)
    @step
    def process(self):
        print("Processing:", self.input)
        try:
            self.image_path = self.input
            model = DonutModel.from_pretrained("naver-clova-ix/donut-base-finetuned-cord-v2")
            model.eval()
            with S3() as s3:
                self.image = Image.open(s3.get(self.image_path).path).convert("RGB")
            self.text = model.inference(image=self.image, prompt="<s_cord-v2>")
        except Exception as e:
            print(e)
            raise e
        self.next(self.join)

    @step
    def join(self, inputs):
        self.results = [input.text['predictions'] for input  in inputs]
        print(self.results)
        self.next(self.end)

    @step
    def end(self):
        pass

if __name__ == '__main__':
    ExtractionFlow()