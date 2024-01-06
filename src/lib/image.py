import torch
import sys, os
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoPipelineForText2Image
from xformers.ops import MemoryEfficientAttentionFlashAttentionOp

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))   # go to mother directory
from common import *
# pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio===0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
# pip3 install diffusers transformers

# MODEL_ID = "runwayml/stable-diffusion-v1-5"
MODEL_ID = "stabilityai/stable-diffusion-2-1"

logger = Mylogger()


class makeImg:
    def __init__(self):
        self.model_id = MODEL_ID
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, torch_dtype=torch.float16)
        # Use the DPMSolverMultistepScheduler (DPM-Solver++) scheduler here instead
        # https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/text2img
        self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe = self.pipe.to("cuda")       # use gpu
        self.pipe.enable_xformers_memory_efficient_attention(attention_op=MemoryEfficientAttentionFlashAttentionOp)
        self.pipe.vae.enable_xformers_memory_efficient_attention(attention_op=None)
        # self.pipe.enable_attention_slicing()  # reduce virtual gpu ram

    def run(self, prompt, path):
        logger.debug("[+] makeImg run...")
        self.prompt = prompt

        # image = pipe(prompt, height=704, width=704).images[0]
        self.image = self.pipe(self.prompt, num_inference_steps=60, guidance_scale=7.5).images[0]
            
        self.image.save(f"{path}.png")
        logger.debug("[+] makeImg OK...")


    def test(self):
        # self.pipe.save_pretrained("model_id", variant="fp16")
        # # 👍 this works
        # stable_diffusion = DiffusionPipeline.from_pretrained(
        #     "./stable-diffusion-v1-5", variant="fp16", torch_dtype=torch.float16, use_safetensors=True
        # )

        # pipeline = AutoPipelineForText2Image.from_pretrained(
        #     "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_safetensors=True
        # ).to("cuda")
        # prompt = "peasant and dragon combat, wood cutting style, viking era, bevel with rune"

        # image = pipeline(prompt, num_inference_steps=25).images[0]
        # image.save("result1.png")
        pass


if __name__ == '__main__':
    prompt = "a horse running through a field"
    test_obj = makeImg()
    test_obj.run(prompt, "result")





