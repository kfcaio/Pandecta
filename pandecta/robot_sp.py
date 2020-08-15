from typing import Iterator, List
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator

from common.generic_robot import GenericRobot, setup


class RobotSP(GenericRobot):

    _text_extraction_args = {
            "pdftotext_arg": "raw"
    }

    BLOCK_PATTERN = (
        r'\d{2}\.\d{3}.\d{3}\/\d{4}-13'
    )

    def search(self, publications: List[dict]) -> Iterator[dict]:
        for publication in publications:
            fp = open(publication, 'rb')
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = PDFPage.get_pages(fp)

            for page in pages:
                interpreter.process_page(page)
                layout = device.get_result()

                for lobj in layout:
                    if isinstance(lobj, LTTextBox):
                        yield parse_box(lobj), page

def parse_box(box: LTTextBox) -> dict:
    x_coord = box.bbox[0]
    y_coord = box.bbox[3]
    text = box.get_text()

    box_title = ''
    hierarchy = []

    for line in box:
        for char in line:
            if 'Bold' in getattr(char, 'fontname', ''):
                box_title += char.get_text()
        if box_title:        
            hierarchy.append(box_title)
        box_title = ''
    
    return {
        'text': text,
        'x': x_coord,
        'y': y_coord,
        'hierarchy': hierarchy
    }




if __name__ == '__main__':
    setup(RobotSP)