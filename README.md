# 🧩 ComfyUI - Random Tag Weights Node

A custom **ComfyUI** node that randomizes tag weights for text prompts.  
Useful for dynamic prompt generation or creative experimentation in AI image workflows.

---

## ✨ Features

- Randomly generates weights for each tag (e.g., `(dog:1.2)`)
- Filters tags based on a minimum threshold
- Optionally shuffles the order of tags
- Allows reproducible randomness via a seed
- Supports both inline text input and external input connections

---

## ⚙️ Parameters

| Name | Type | Description |
|------|------|-------------|
| `text` | string | Base tag list (comma-separated) |
| `min_weight` | float | Minimum random weight |
| `max_weight` | float | Maximum random weight |
| `threshold` | float | Minimum weight to include tag |
| `max_tags` | int | Maximum number of tags to output |
| `seed` | int | Random seed for reproducibility |
| `shuffle_tags` | bool | Shuffle the order of selected tags |
| `input_text` | optional string | Alternative input text |

---

## 🧠 How It Works

1. The node parses the provided text for tags.
2. Each tag is assigned a random weight between `min_weight` and `max_weight`.
3. Tags with weights **above `threshold`** are kept.
4. The selected tags are shuffled (if enabled) and limited to `max_tags`.
5. The result is returned as a formatted string like: (dog:1.2), (cat:1.3), (bird:1.0)


---

## 📦 Installation

1. Download or clone this repo into your `ComfyUI/custom_nodes` folder
 
2. Restart ComfyUI — your new node will appear under the Text category!