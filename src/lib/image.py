import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler, AutoPipelineForText2Image
# pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio===0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
# pip3 install diffusers transformers

print("Torch version:",torch.__version__)
print("Is CUDA enabled?",torch.cuda.is_available())

# model_id = "runwayml/stable-diffusion-v1-5"
model_id = "stabilityai/stable-diffusion-2-1"

# Use the DPMSolverMultistepScheduler (DPM-Solver++) scheduler here instead
# https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/text2img
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe = pipe.to("cuda")

pipe.enable_attention_slicing()

prompt = "a horse running through a field"
# prompt = "초원을 달리는 말을 그려줘"
# image = pipe(prompt, height=704, width=704).images[0]
image = pipe(prompt).images[0]
    
image.save("result.png")

# pipe.save_pretrained("model_id", variant="fp16")
# 👍 this works
# stable_diffusion = DiffusionPipeline.from_pretrained(
#     "./stable-diffusion-v1-5", variant="fp16", torch_dtype=torch.float16, use_safetensors=True
# )

# pipeline = AutoPipelineForText2Image.from_pretrained(
#     "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_safetensors=True
# ).to("cuda")
# prompt = "peasant and dragon combat, wood cutting style, viking era, bevel with rune"

# image = pipeline(prompt, num_inference_steps=25).images[0]
# image.save("result1.png")
