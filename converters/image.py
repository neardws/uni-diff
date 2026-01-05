import os
from typing import List
from .base import BaseConverter, ConvertedDocument, TextBlock


class ImageConverter(BaseConverter):
    """Converter for image files using OCR or pixel comparison."""

    @property
    def supported_extensions(self) -> List[str]:
        return ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']

    def convert(self, file_path: str, use_ocr: bool = True) -> ConvertedDocument:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        blocks = []
        full_text = ""
        metadata = {}

        try:
            from PIL import Image
            img = Image.open(file_path)
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['mode'] = img.mode
            metadata['format'] = img.format

            if use_ocr:
                try:
                    import pytesseract
                    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

                    n_boxes = len(data['text'])
                    current_line = []
                    current_line_top = None
                    line_threshold = 10

                    for i in range(n_boxes):
                        text = data['text'][i].strip()
                        if text:
                            top = data['top'][i]

                            if current_line_top is None:
                                current_line_top = top

                            if abs(top - current_line_top) > line_threshold:
                                if current_line:
                                    line_text = ' '.join([w['text'] for w in current_line])
                                    full_text += line_text + "\n"
                                    min_x = min(w['x'] for w in current_line)
                                    min_y = min(w['y'] for w in current_line)
                                    max_x = max(w['x'] + w['width'] for w in current_line)
                                    max_y = max(w['y'] + w['height'] for w in current_line)
                                    blocks.append(TextBlock(
                                        text=line_text,
                                        page=0,
                                        x=min_x,
                                        y=min_y,
                                        width=max_x - min_x,
                                        height=max_y - min_y,
                                        metadata={'type': 'ocr_line'}
                                    ))
                                current_line = []
                                current_line_top = top

                            current_line.append({
                                'text': text,
                                'x': data['left'][i],
                                'y': data['top'][i],
                                'width': data['width'][i],
                                'height': data['height'][i]
                            })

                    if current_line:
                        line_text = ' '.join([w['text'] for w in current_line])
                        full_text += line_text + "\n"
                        min_x = min(w['x'] for w in current_line)
                        min_y = min(w['y'] for w in current_line)
                        max_x = max(w['x'] + w['width'] for w in current_line)
                        max_y = max(w['y'] + w['height'] for w in current_line)
                        blocks.append(TextBlock(
                            text=line_text,
                            page=0,
                            x=min_x,
                            y=min_y,
                            width=max_x - min_x,
                            height=max_y - min_y,
                            metadata={'type': 'ocr_line'}
                        ))

                except ImportError:
                    full_text = f"[Image: {img.width}x{img.height} {img.mode}]"
                    blocks.append(TextBlock(
                        text=full_text,
                        page=0,
                        x=0,
                        y=0,
                        width=img.width,
                        height=img.height,
                        metadata={'type': 'image_placeholder'}
                    ))
            else:
                full_text = f"[Image: {img.width}x{img.height} {img.mode}]"
                blocks.append(TextBlock(
                    text=full_text,
                    page=0,
                    x=0,
                    y=0,
                    width=img.width,
                    height=img.height,
                    metadata={'type': 'image_placeholder'}
                ))

            img.close()

        except ImportError:
            raise RuntimeError(
                "Pillow is not available. Install it: pip install Pillow"
            )

        return ConvertedDocument(
            blocks=blocks,
            full_text=full_text,
            page_count=1,
            metadata=metadata,
            source_path=file_path,
            source_type='image'
        )
