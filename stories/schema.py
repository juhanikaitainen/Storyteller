import json
import jsonschema

storySchema = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "title":{
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 50
                },
                "summary": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200
                },
                "price": {
                    "type": "number",
                    "minimum": 0,
                    "exclusiveMaximum": 1000000.00
                }
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "is_starting": {
                        "type": "boolean"
                    },
                    "is_ending": {
                        "type": "boolean"
                    },
                    "position": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 20
                    },
                    "text": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 3000
                    },
                    "links": {
                        "type": [ "array", "null" ],
                        "items": {
                            "type": "object",
                            "properties": {
                                "to": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 20
                                },
                                "button": {
                                    "type": "string",
                                    "minLength": 1,
                                    "maxLength": 50
                                }
                            }
                        }
                    }
                }
            }
        }       
    }
}


def storySchemaValidate(jsonData):
    try:
        jsonschema.validate(instance=jsonData, schema=storySchema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True