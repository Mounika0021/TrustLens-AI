"""
TrustLens AI
Inference Engine
Loads the Qwen2-VL LoRA model only once.
"""

import torch
from PIL import Image

from transformers import (
    AutoProcessor,
    Qwen2VLForConditionalGeneration,
)

from peft import PeftModel


MODEL_NAME = "Qwen/Qwen2-VL-2B-Instruct"

LORA_PATH = "/content/drive/MyDrive/TrustLens-AI/models/trustlens_qwen2vl_lora"


class TrustLensModel:

    def __init__(self):

        print("Loading processor...")

        self.processor = AutoProcessor.from_pretrained(
            MODEL_NAME
        )

        print("Loading base model...")

        base_model = Qwen2VLForConditionalGeneration.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
        )

        print("Loading LoRA adapter...")

        self.model = PeftModel.from_pretrained(
            base_model,
            LORA_PATH
        )

        self.model.eval()

        print("✅ TrustLens model ready!")

    def predict(self, image_path):

        image = Image.open(image_path).convert("RGB")

        prompt = """
You are an identity document verification expert.

Look at this document.

Extract the MRZ.

Return ONLY valid JSON.

{
    "mrz_line_1":"",
    "mrz_line_2":""
}
"""

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.processor(
            text=[text],
            images=[image],
            return_tensors="pt",
        ).to(self.model.device)

        with torch.no_grad():

            output = self.model.generate(
                **inputs,
                max_new_tokens=128,
            )

        generated = output[:, inputs.input_ids.shape[1]:]

        response = self.processor.batch_decode(
            generated,
            skip_special_tokens=True,
        )[0]

        return response


# --------------------------------------------------
# Singleton model
# --------------------------------------------------

_model = None


def get_model():
    """
    Load the model only once.
    """

    global _model

    if _model is None:
        _model = TrustLensModel()

    return _model


def predict(image_path):
    """
    Convenience function for inference.
    """

    model = get_model()

    return model.predict(image_path)


if __name__ == "__main__":

    result = predict(
        "/content/drive/MyDrive/TrustLens-AI/datasets/MRZ/images/0.png"
    )

    print(result)