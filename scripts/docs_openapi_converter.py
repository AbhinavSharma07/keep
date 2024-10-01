from argparse import ArgumentParser
import typing as t
import json
import logging

Json = dict[str, t.Any] | list[t.Any] | str | bool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_3_dot_1_to_3_dot_0(json_content: dict[str, Json]) -> dict[str, Json]:
    """
    Converts OpenAPI 3.1.0 spec to 3.0.2 by handling 'anyOf' and 'examples' fields.
    
    :param json_content: Dictionary containing OpenAPI spec in 3.1.0 format
    :return: Converted OpenAPI spec in 3.0.2 format
    """
    json_content["openapi"] = "3.0.2"

    def inner(yaml_dict: Json) -> None:
        """Recursively processes the dictionary to adjust fields for OpenAPI 3.0.2."""
        if isinstance(yaml_dict, dict):
            # Handle `anyOf` conversion
            if "anyOf" in yaml_dict and isinstance(yaml_dict["anyOf"], list):
                yaml_dict["anyOf"] = [item for item in yaml_dict["anyOf"] if not (isinstance(item, dict) and item.get("type") == "null")]
                if len(yaml_dict["anyOf"]) < len(json_content.get("anyOf", [])):
                    yaml_dict["nullable"] = True

            # Convert `examples` to `example`
            if "examples" in yaml_dict:
                examples = yaml_dict.pop("examples", [])
                if isinstance(examples, list) and examples:
                    yaml_dict["example"] = examples[0]

            # Recur for nested dictionaries
            for value in yaml_dict.values():
                inner(value)

        elif isinstance(yaml_dict, list):
            for item in yaml_dict:
                inner(item)

    inner(json_content)
    return json_content

def load_and_convert(source_path: str, dest_path: str) -> None:
    """
    Loads the OpenAPI 3.1.0 JSON, converts it to 3.0.2, and saves it to the destination path.
    
    :param source_path: Path to the OpenAPI 3.1.0 JSON file
    :param dest_path: Path to save the converted OpenAPI 3.0.2 JSON file
    """
    try:
        with open(source_path, "r") as src_file:
            content = json.load(src_file)
            logger.info(f"Loaded OpenAPI spec from {source_path}")

        converted_content = convert_3_dot_1_to_3_dot_0(content)
        
        with open(dest_path, "w") as dest_file:
            json.dump(converted_content, dest_file, indent=2)
            logger.info(f"Converted OpenAPI spec saved to {dest_path}")

    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error processing file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    parser = ArgumentParser(description="Convert OpenAPI 3.1.0 JSON spec to 3.0.2 format.")
    parser.add_argument("-s", "--source", help="Path to the OpenAPI 3.1.0 JSON file", required=True)
    parser.add_argument("-d", "--dest", help="Path to save the converted OpenAPI 3.0.2 JSON file", required=True)

    args = parser.parse_args()

    load_and_convert(args.source, args.dest)
