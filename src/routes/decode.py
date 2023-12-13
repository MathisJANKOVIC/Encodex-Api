from pydantic import BaseModel
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from database.models import EncodingType
from database.connection import LocalSession

class BodyModel(BaseModel):
    encoded_str: str

router = APIRouter()

@router.post("/encodex/{encoding_type_name}/decode/")
def decode_string(encoding_type_name: str, body: BodyModel = Body(...)):

    session = LocalSession()
    encoding_type: EncodingType = session.query(EncodingType).filter(EncodingType.name == encoding_type_name).first()

    if(encoding_type is None):
        session.close()
        return JSONResponse(status_code=404, content={"succes": False, "message": "Encoding type not found"})

    decoded_str = ""

    if(encoding_type.encoded_chars_len is None):

        buffer = ""
        for encoded_char in body.encoded_str :
            if(encoded_char == encoding_type.encoded_words_sep):
                if buffer:
                    decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
                    buffer = ""
                decoded_str += " "
            elif(encoded_char == encoding_type.encoded_chars_sep):
                if buffer:
                    decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
                    buffer = ""
            else:
                decoded_char = next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), None)

                if(decoded_char is None):
                    buffer += encoded_char

                else:
                    decoded_str += decoded_char

        if(buffer):
            decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
        decoded_str += " "
    else:
        buffer = ""
        for encoded_char in body.encoded_str :
            if(encoded_char == encoding_type.encoded_words_sep):
                if buffer:
                    decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
                    buffer = ""
                decoded_str += " "
            elif(encoded_char == encoding_type.encoded_chars_sep):
                if buffer:
                    decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
                    buffer = ""
            else:
                buffer += encoded_char
                if(len(buffer) == encoding_type.encoded_chars_len):
                    decoded_str += next((encoding_char.char for encoding_char in encoding_type.encoding_chars if encoding_char.encoded_char == buffer), buffer)
                    buffer = ""

    session.close()
    return JSONResponse(status_code=200, content={"succes": True, "content": decoded_str})