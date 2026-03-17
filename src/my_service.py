from common_code.config import get_settings
from common_code.logger.logger import get_logger, Logger
from common_code.service.models import Service
from common_code.service.enums import ServiceStatus
from common_code.common.enums import FieldDescriptionType, ExecutionUnitTagName, ExecutionUnitTagAcronym
from common_code.common.models import FieldDescription, ExecutionUnitTag
from common_code.tasks.models import TaskData
# Imports required by the service's model
from draw_boxes.draw_boxes import draw_bounding_boxes
import io
import json

api_description = """This service draws boxes on an image. It is intended to work with the
text recognition OCR service. The bounding boxes are passed in a JSON file that corresponds to the output of
the text recognition service.
"""
api_summary = """This service draws boxes on an image. It is intended to work with the
text recognition OCR service.
"""

api_title = "Image Draw Bounding Boxes Service API."
version = "0.0.1"

settings = get_settings()


class MyService(Service):
    """
    bounding boxes drawing service
    """

    # Any additional fields must be excluded for Pydantic to work
    _model: object
    _logger: Logger

    def __init__(self):
        super().__init__(
            name="Image Draw Bounding Boxes",
            slug="image-draw-bounding-boxes",
            url=settings.service_url,
            summary=api_summary,
            description=api_description,
            status=ServiceStatus.AVAILABLE,
            data_in_fields=[
                FieldDescription(
                    name="image",
                    type=[
                        FieldDescriptionType.IMAGE_PNG,
                        FieldDescriptionType.IMAGE_JPEG,
                    ],
                ),
                FieldDescription(
                    name="data",
                    type=[FieldDescriptionType.APPLICATION_JSON]
                )
            ],
            data_out_fields=[
                FieldDescription(
                    name="image-with-boxes", type=[FieldDescriptionType.IMAGE_PNG, FieldDescriptionType.IMAGE_JPEG]
                ),
            ],
            tags=[
                ExecutionUnitTag(
                    name=ExecutionUnitTagName.IMAGE_PROCESSING,
                    acronym=ExecutionUnitTagAcronym.IMAGE_PROCESSING,
                ),
            ],
            has_ai=False,
            docs_url="https://docs.swiss-ai-center.ch/reference/services/image-draw-bounding-boxes/",
        )
        self._logger = get_logger(settings)

    def process(self, data):
        # NOTE that the data is a dictionary with the keys being the field names set in the data_in_fields
        # The objects in the data variable are always bytes. It is necessary to convert them to the desired type
        # before using them.
        # raw = data["image"].data
        # input_type = data["image"].type
        # ... do something with the raw data
        img = data['image'].data
        img_format = data['image'].type
        boxes_data = json.loads(data['data'].data)

        img_boxes = draw_bounding_boxes(image=img, boxes=boxes_data['boxes'])
        img_type = str(data['image'].type).split('_')[1]
        img_byte_arr = io.BytesIO()
        img_boxes.save(img_byte_arr, format=img_type)
        img_byte_arr = img_byte_arr.getvalue()

        # NOTE that the result must be a dictionary with the keys being the field names set in the data_out_fields
        return {
            "image-with-boxes": TaskData(data=img_byte_arr, type=img_format)
        }
