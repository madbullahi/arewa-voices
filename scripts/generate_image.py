"""Generate campaign images with LongCat-Image.

Usage:
    python scripts/generate_image.py --campaign campaigns/out-of-school-children
"""
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, help="Path to a campaign folder")
    parser.add_argument("--steps", type=int, default=50)
    parser.add_argument("--high-vram", action="store_true", help="Keep the whole model on GPU (faster)")
    args = parser.parse_args()

    campaign = Path(args.campaign)
    script = json.loads((campaign / "script.json").read_text(encoding="utf-8"))
    out_dir = campaign / "output" / "images"
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch
    from diffusers import LongCatImagePipeline

    pipe = LongCatImagePipeline.from_pretrained(
        "meituan-longcat/LongCat-Image", torch_dtype=torch.bfloat16
    )
    if args.high_vram:
        pipe.to("cuda")
    else:
        pipe.enable_model_cpu_offload()  # ~17 GB VRAM

    for item in script["images"]:
        image = pipe(
            item["prompt"],
            height=item["height"],
            width=item["width"],
            guidance_scale=4.0,
            num_inference_steps=args.steps,
            generator=torch.Generator("cpu").manual_seed(item["seed"]),
            enable_cfg_renorm=True,
            enable_prompt_rewrite=True,
        ).images[0]
        path = out_dir / f"{item['name']}.png"
        image.save(path)
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
