#!/usr/bin/env python3
"""base64img - Encode images to data URIs and decode them back.

One file. Zero deps. Embeds images.

Usage:
  base64img.py encode photo.png              → data URI to stdout
  base64img.py encode photo.png --raw        → raw base64 (no prefix)
  base64img.py encode photo.png --css        → CSS background-image
  base64img.py encode photo.png --html       → <img> tag
  base64img.py encode photo.png --md         → Markdown image
  base64img.py decode data_uri.txt -o out.png
  base64img.py info photo.png                → size + dimensions estimate
"""

import argparse
import base64
import mimetypes
import os
import sys


MIME_MAP = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
    '.webp': 'image/webp',
    '.svg': 'image/svg+xml',
    '.ico': 'image/x-icon',
    '.bmp': 'image/bmp',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
    '.avif': 'image/avif',
}


def get_mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return MIME_MAP.get(ext, mimetypes.guess_type(path)[0] or 'application/octet-stream')


def cmd_encode(args):
    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    with open(args.file, 'rb') as f:
        data = f.read()

    b64 = base64.b64encode(data).decode('ascii')
    mime = get_mime(args.file)
    data_uri = f"data:{mime};base64,{b64}"

    file_size = len(data)
    b64_size = len(b64)
    print(f"# {os.path.basename(args.file)}: {file_size} bytes → {b64_size} chars ({mime})", file=sys.stderr)

    if args.raw:
        print(b64)
    elif args.css:
        print(f"background-image: url({data_uri});")
    elif args.html:
        alt = os.path.splitext(os.path.basename(args.file))[0]
        print(f'<img src="{data_uri}" alt="{alt}" />')
    elif args.md:
        alt = os.path.splitext(os.path.basename(args.file))[0]
        print(f"![{alt}]({data_uri})")
    elif args.clipboard:
        print(data_uri, end='')
    else:
        print(data_uri)

    return 0


def cmd_decode(args):
    if args.input:
        with open(args.input) as f:
            data_str = f.read().strip()
    else:
        if sys.stdin.isatty():
            print("Error: pipe data URI or use -i file", file=sys.stderr)
            return 1
        data_str = sys.stdin.read().strip()

    # Strip data URI prefix if present
    if data_str.startswith('data:'):
        # data:image/png;base64,xxxx
        _, encoded = data_str.split(',', 1)
    else:
        encoded = data_str

    try:
        raw = base64.b64decode(encoded)
    except Exception as e:
        print(f"Error decoding: {e}", file=sys.stderr)
        return 1

    if args.output:
        with open(args.output, 'wb') as f:
            f.write(raw)
        print(f"Wrote {len(raw)} bytes to {args.output}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(raw)

    return 0


def cmd_info(args):
    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    size = os.path.getsize(args.file)
    mime = get_mime(args.file)
    b64_size = ((size + 2) // 3) * 4  # base64 expansion
    data_uri_size = b64_size + len(f"data:{mime};base64,")

    print(f"  File:      {args.file}")
    print(f"  Size:      {size:,} bytes ({size/1024:.1f} KB)")
    print(f"  MIME:      {mime}")
    print(f"  Base64:    {b64_size:,} chars ({b64_size/1024:.1f} KB)")
    print(f"  Data URI:  {data_uri_size:,} chars ({data_uri_size/1024:.1f} KB)")
    print(f"  Expansion: {b64_size/size:.1f}x" if size else "")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Base64 image encoder/decoder")
    sub = parser.add_subparsers(dest="command")

    e = sub.add_parser("encode", help="Encode image to base64/data URI")
    e.add_argument("file", help="Image file to encode")
    e.add_argument("--raw", action="store_true", help="Raw base64 (no data URI prefix)")
    e.add_argument("--css", action="store_true", help="CSS background-image format")
    e.add_argument("--html", action="store_true", help="HTML <img> tag")
    e.add_argument("--md", action="store_true", help="Markdown image")
    e.add_argument("--clipboard", action="store_true", help="No trailing newline")

    d = sub.add_parser("decode", help="Decode base64/data URI to image")
    d.add_argument("-i", "--input", help="File containing data URI")
    d.add_argument("-o", "--output", help="Output file path")

    i = sub.add_parser("info", help="Show encoding size info")
    i.add_argument("file", help="Image file to analyze")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1

    return {"encode": cmd_encode, "decode": cmd_decode, "info": cmd_info}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
