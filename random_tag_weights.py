import random
import re

class RandomTagWeights:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "big cat, dog, small bird, red fox, blue sky, green tree, tall building, fast car, loud noise, bright light"}),
                "min_weight": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "max_weight": ("FLOAT", {"default": 1.3, "min": 0.0, "max": 10.0, "step": 0.1}),
                "threshold": ("FLOAT", {"default": 1.2, "min": 0.0, "max": 10.0, "step": 0.1}),
                "max_tags": ("INT", {"default": 3, "min": 1, "max": 10000, "step": 1}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "shuffle_tags": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "input_text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("modified_text",)
    FUNCTION = "randomize_weights"
    CATEGORY = "text"

    def randomize_weights(self, text, min_weight, max_weight, threshold, max_tags, seed, shuffle_tags, input_text=None):
        if input_text and input_text.strip():
            source_text = input_text
        else:
            source_text = text

        if not isinstance(source_text, str):
            source_text = str(source_text)

        random.seed(seed)

        weighted_pattern = r"\(([^:]+):([\d.]+)\)"
        plain_tag_pattern = r"(^|,\s*)([^,]+?)(?=,|$|\s*$)"

        def get_random_weight():
            return round(random.uniform(min_weight, max_weight), 2)

        qualifying_tags = []

        def replace_weight(match):
            tag = match.group(1).strip()
            new_weight = get_random_weight()
            if new_weight >= threshold:
                qualifying_tags.append((tag, new_weight))
            return ""

        text_with_weighted = re.sub(weighted_pattern, replace_weight, source_text)

        def wrap_plain_tag(match):
            tag = match.group(2).strip()
            if not re.search(rf"\({re.escape(tag)}:[\d.]+\)", text_with_weighted):
                new_weight = get_random_weight()
                if new_weight >= threshold:
                    qualifying_tags.append((tag, new_weight))
            return ""

        text_with_weighted = re.sub(plain_tag_pattern, wrap_plain_tag, text_with_weighted)

        if shuffle_tags:
            random.shuffle(qualifying_tags)

        qualifying_tags = qualifying_tags[:max_tags]

        modified_text = ", ".join(f"({tag}:{weight})" for tag, weight in qualifying_tags).strip()

        return (modified_text,)

NODE_CLASS_MAPPINGS = {
    "RandomTagWeights": RandomTagWeights
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomTagWeights": "Random Tag Weights"
}

