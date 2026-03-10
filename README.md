# base64img

Encode images to data URIs and decode them back.

One file. Zero deps. Embeds images.

## Usage

```bash
# Encode to data URI
python3 base64img.py encode photo.png

# Output formats
python3 base64img.py encode photo.png --html    # <img> tag
python3 base64img.py encode photo.png --css     # background-image
python3 base64img.py encode photo.png --md      # Markdown
python3 base64img.py encode photo.png --raw     # raw base64

# Decode back to file
python3 base64img.py decode -i encoded.txt -o output.png

# Size info
python3 base64img.py info photo.png
```

## Requirements

Python 3.8+. No dependencies.

## License

MIT
