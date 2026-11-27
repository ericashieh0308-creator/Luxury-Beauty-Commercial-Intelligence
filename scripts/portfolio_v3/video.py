"""Assemble a captioned 72-second walkthrough from verified Chromium captures."""
from pathlib import Path
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

from .evidence import ROOT

OUT = ROOT / "portfolio/v3"
SEGMENTS = [
    ("01-executive", "01 / Executive dashboard", "Read catalog coverage first. The public demo uses fictional records and simulated financial results."),
    ("02-commercial", "02 / Assortment decision", "Use brand and category representatives to prioritize an assortment review. Coverage does not measure sales."),
    ("03-base", "03 / Base financial plan", "Base shows USD 700,824 annual net revenue and USD 155,493 operating profit, rounded."),
    ("04-bull", "04 / Switch the planning case", "Selecting Bull updates annual operating profit to USD 204,022 under the modeled assumptions."),
    ("05-offer", "05 / Trial a 15% discount", "At 20% assumed unit uplift, the simulated offer loses USD 455 of contribution after campaign cost."),
    ("06-uplift", "06 / Raise the response assumption", "At 30% assumed uplift, contribution rises by USD 2,067. Verify response before funding the offer."),
]


def main():
    with tempfile.TemporaryDirectory() as workspace:
        work = Path(workspace)
        lines = []
        for index, (file, heading, caption) in enumerate(SEGMENTS):
            with Image.open(OUT / "evidence" / f"{file}.png") as raw:
                raw.thumbnail((1440, 890), Image.Resampling.LANCZOS)
                frame = Image.new("RGB", (1600, 1000), "#FBF8F1")
                frame.paste(raw, ((1600-raw.width)//2, 6))
            draw = ImageDraw.Draw(frame)
            draw.rectangle((0, 892, 1600, 1000), fill="#634F43")
            draw.text((44, 902), heading, fill="#E2CDA8", font=ImageFont.load_default(size=26))
            draw.text((44, 943), caption, fill="#FFFDF8", font=ImageFont.load_default(size=23))
            name = f"frame-{index}.png"
            frame.save(work / name)
            lines.extend([f"file '{name}'", "duration 12"])
        lines.append(f"file 'frame-{len(SEGMENTS)-1}.png'")
        (work / "sequence.txt").write_text("\n".join(lines)+"\n", encoding="utf-8")
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-safe","0","-f","concat",
                        "-i", str(work/"sequence.txt"),"-t","72","-r","24","-c:v","libx264","-pix_fmt","yuv420p",
                        "-movflags","+faststart",str(OUT/"Streamlit_Demo.mp4")], check=True)


if __name__ == "__main__":
    main()
