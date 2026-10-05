from pathlib import Path
from PIL import Image, ImageDraw

qa = Path(__file__).resolve().parents[1] / "tmp" / "final_qa"

def make(pattern, output, cols, thumb_w):
    paths = sorted(qa.glob(pattern))
    thumbs = []
    for path in paths:
        im = Image.open(path).convert("RGB")
        h = round(im.height * thumb_w / im.width)
        im = im.resize((thumb_w, h), Image.Resampling.LANCZOS)
        thumbs.append((path.name, im))
    label_h, gap = 24, 12
    cell_h = max(im.height for _, im in thumbs) + label_h
    rows = (len(thumbs) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), "white")
    draw = ImageDraw.Draw(canvas)
    for i, (name, im) in enumerate(thumbs):
        x = gap + (i % cols) * (thumb_w + gap)
        y = gap + (i // cols) * (cell_h + gap)
        draw.text((x, y), name, fill="black")
        canvas.paste(im, (x, y + label_h))
    canvas.save(qa / output, "JPEG", quality=55, optimize=True)

make("report-*.png", "report-contact.jpg", 2, 430)
make("resume-*.png", "resume-contact.jpg", 2, 520)
