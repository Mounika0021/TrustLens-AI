
"""
TrustLens AI
Inference Engine

Uses the fine-tuned Qwen2-VL + LoRA model
with the same inference logic as the
working TrustLens-AI Demo notebook.
"""

import torch
from PIL import Image

from transformers import (
    AutoProcessor,
    Qwen2VLForConditionalGeneration,
)

from peft import PeftModel


MODEL_NAME = "Qwen/Qwen2-VL-2B-Instruct"

LORA_PATH = (
    "/content/drive/MyDrive/TrustLens-AI/"
    "models/trustlens_qwen2vl_lora"
)


class TrustLensModel:

    def __init__(self):

        print("Loading processor...")

        self.processor = AutoProcessor.from_pretrained(
            MODEL_NAME
        )

        print("Loading base model...")

        base_model = (
            Qwen2VLForConditionalGeneration.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.float16,
                device_map="auto",
            )
        )

        print("Loading LoRA adapter...")

        self.model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH,
        )

        self.model.eval()

        print("✅ TrustLens fine-tuned model ready!")

    def predict(self, image_path):

        image = Image.open(
            image_path
        ).convert("RGB")

        # IMPORTANT:
        # This is the same prompt used by the
        # working TrustLens-AI-Demo notebook.

        prompt = (
            "Analyze this identity document and "
            "return the verification result in JSON format."
        )

        conversation = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image,
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            conversation,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=[text],
            images=[image],
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.model.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=128,
                do_sample=False,
            )

        generated_ids = generated_ids[
            :,
            inputs["input_ids"].shape[1]:
        ]

        response = self.processor.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0].strip()

        return response


# --------------------------------------------------
# Singleton model
# --------------------------------------------------

_model = None


def get_model():

    global _model

    if _model is None:
        _model = TrustLensModel()

    return _model


def predict(image_path):

    model = get_model()

    return model.predict(image_path)


if __name__ == "__main__":

    test_image = (
        "/content/drive/MyDrive/TrustLens-AI/"
        "datasets/MRZ/images/0.png"
    )

    print(predict(test_image))
