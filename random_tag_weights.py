import random
import re

class RandomTagWeights:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Default input text if no external input_text is provided."
                    }
                ),
                "min_weight": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "The lowest possible random weight assigned."
                    }
                ),
                "max_weight": (
                    "FLOAT",
                    {
                        "default": 1.3,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "The highest possible random weight assigned."
                    }
                ),
                "threshold": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "Tags with generated weight below this value are discarded."
                    }
                ),
                "max_tags": (
                    "INT",
                    {
                        "default": 30,
                        "min": 1,
                        "max": 10000,
                        "step": 1,
                        "tooltip": "Maximum number of tags allowed in the output."
                    }
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xffffffffffffffff,
                        "tooltip": "Random seed for consistent repeatable output."
                    }
                ),
                "shuffle_tags": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Randomize the order of output tags."
                    }
                ),
                "detect_by_commas": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "If ON: tags are split by commas. If OFF: tags are split by spaces."
                    }
                ),
                "group_parentheses": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "If ON: anything inside (...) is treated as one tag."
                    }
                ),
                "preserve_existing_weights": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "If ON: tags already containing weights (tag:1.0) will not be modified."
                    }
                ),
                "output_with_commas": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "tooltip": "Choose output format: commas or spaces between final tags."
                    }
                ),
                "add_random_commas": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "If ON: randomly insert commas between tags at the end."
                    }
                ),
                "num_random_commas": (
                    "INT",
                    {
                        "default": 1,
                        "min": 1,
                        "max": 100,
                        "step": 1,
                        "tooltip": "Number of commas to randomly insert between tags."
                    }
                ),
            },
            "optional": {
                "input_text": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "forceInput": True,
                        "tooltip": "External text input from another node."
                    }
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("modified_text",)
    FUNCTION = "randomize_weights"
    CATEGORY = "text"

    def randomize_weights(
        self,
        text,
        min_weight,
        max_weight,
        threshold,
        max_tags,
        seed,
        shuffle_tags,
        detect_by_commas,
        group_parentheses,
        preserve_existing_weights,
        output_with_commas,
        add_random_commas,
        num_random_commas,
        input_text=None
    ):
        if input_text and input_text.strip():
            source_text = input_text
        else:
            source_text = text

        if not isinstance(source_text, str):
            source_text = str(source_text)

        random.seed(seed)

        weighted_pattern = r"\(([^()]+?):([\d.]+)\)"
        parentheses_group_pattern = r"\([^()]*\)"

        final_tags = []

        # 1. Extract weighted tags
        def extract_weighted(match):
            tag = match.group(1).strip()
            weight = match.group(2).strip()

            if preserve_existing_weights:
                final_tags.append((tag, float(weight)))
            else:
                new_weight = round(random.uniform(min_weight, max_weight), 2)
                if new_weight >= threshold:
                    final_tags.append((tag, new_weight))

            return ""

        remainder = re.sub(weighted_pattern, extract_weighted, source_text)

        # 2. Extract grouped parentheses tags
        grouped_tags = set()

        if group_parentheses:
            for match in re.findall(parentheses_group_pattern, remainder):
                cleaned = match.strip("()").strip()
                grouped_tags.add(cleaned)
                remainder = remainder.replace(match, " ")

            for tag in grouped_tags:
                new_weight = round(random.uniform(min_weight, max_weight), 2)
                if new_weight >= threshold:
                    final_tags.append((tag, new_weight))

        # 3. Split remaining plain tags
        remainder = remainder.replace("\n", " ")

        if detect_by_commas:
            raw_tags = [t.strip() for t in remainder.split(",") if t.strip()]
        else:
            raw_tags = [t.strip() for t in remainder.split(" ") if t.strip()]

        for tag in raw_tags:
            if not tag:
                continue

            # FIX: remove commas when output_with_commas is OFF
            if not output_with_commas:
                tag = tag.replace(",", "").strip()

            if any(tag == existing for existing, _ in final_tags):
                continue

            if preserve_existing_weights and re.match(weighted_pattern, tag):
                continue

            new_weight = round(random.uniform(min_weight, max_weight), 2)
            if new_weight >= threshold:
                final_tags.append((tag, new_weight))

        # 4. Shuffle + limit count
        if shuffle_tags:
            random.shuffle(final_tags)

        final_tags = final_tags[:max_tags]

        # 5. Output format
        sep = ", " if output_with_commas else " "

        modified_text = sep.join(f"({tag}:{weight})" for tag, weight in final_tags)

        # 6. Add random commas if enabled
        if add_random_commas and len(final_tags) > 1:
            # Find positions after each tag (where we can insert commas)
            # We'll look for positions right after tag patterns like "(tag:weight)"
            tag_pattern = r"\([^)]+:[^)]+\)"
            matches = list(re.finditer(tag_pattern, modified_text))
            
            if matches:
                # Get positions right after each tag (except the last one)
                insertion_positions = [match.end() for match in matches[:-1]]
                
                # Limit number of commas to available positions
                num_commas_to_add = min(num_random_commas, len(insertion_positions))
                
                # Randomly select positions to insert commas
                selected_positions = random.sample(insertion_positions, num_commas_to_add)
                selected_positions.sort(reverse=True)  # Sort in reverse to maintain indices when inserting
                
                # Insert commas at selected positions
                for pos in selected_positions:
                    modified_text = modified_text[:pos] + "," + modified_text[pos:]

        return (modified_text,)


NODE_CLASS_MAPPINGS = {
    "RandomTagWeights": RandomTagWeights
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomTagWeights": "Random Tag Weights"
}

