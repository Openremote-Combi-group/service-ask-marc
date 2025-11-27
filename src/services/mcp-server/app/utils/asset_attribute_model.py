from typing import Optional

from openremote_client.schemas import AttributeDescriptorObjectSchema
from pydantic import create_model, Field

TYPE_MAP = {
    "text": str,
    "positiveInteger": int,
    "boolean": bool,
    "email": str,
    "text[]": list[str],
    "colourRGB": str,
    "GEO_JSONPoint": str,
    "hostOrIPAddress": str,
    "TCP_IPPortNumber": str,
    "usernameAndPassword": str,
    "connectionStatus": str,
    "oAuthGrant": str,
    "assetType": str,
    "positiveNumber": float,
    "number": float,
    "executionStatus": str,
    "positiveInteger[][]": list[list[int]],
    "connectorType": str,
    "multivaluedTextMap": str,
    "HTTP_URL": str,
    "integer": int,
    "SNMPVersion": str,
    "MQTTQos": str,
    "kNXMessageSourceAddress": str,
    "panelOrientation": str,
    "UUID": str,
    "WS_URL": str,
    "websocketSubscription": str,
    "websocketSubscription[]": list[str],
    "energyType": str,
    "operationMode": str,
    "consoleProviders": str,
    "direction": str,
    "vegetableType": str
}



def asset_attribute_model_factory(name: str, attributes: list[AttributeDescriptorObjectSchema]):
    model_fields = {}

    for attribute in attributes:
        field_name = attribute["name"]
        field_type = attribute.get("type")
        optional = attribute.get("optional", False)
        constraints = attribute.get("constraints", [])

        py_type = TYPE_MAP[field_type]

        # Build Field() constraints
        field_args = {}

        # If optional, wrap with Optional[]
        if optional:
            py_type = Optional[py_type]
            field_args["default"] = None


        for c in constraints:
            if c["type"] == "min":
                field_args["ge"] = c["min"]
            elif c["type"] == "max":
                field_args["le"] = c["max"]

        model_fields[field_name] = (py_type, Field(**field_args))

    return create_model(name, **model_fields)
