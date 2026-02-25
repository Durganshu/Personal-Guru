"""
Book Cover Generation Service using ComfyUI.

Connects to a ComfyUI server via websockets to generate
AI book cover images from a workflow JSON template.
"""
import json
import logging
import os
import random
import urllib.parse
import urllib.request
import uuid

logger = logging.getLogger(__name__)


class BookCoverService:
    """Generates book cover images via ComfyUI API."""

    def __init__(self, server_address, workflow_path):
        self.server_address = server_address
        self.workflow_path = workflow_path
        self.client_id = str(uuid.uuid4())

    def _queue_prompt(self, prompt):
        """Submit a prompt to the ComfyUI queue."""
        p = {"prompt": prompt, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt", data=data
        )
        return json.loads(urllib.request.urlopen(req, timeout=30).read())

    def _get_image(self, filename, subfolder, folder_type):
        """Download a generated image from ComfyUI."""
        params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(params)
        with urllib.request.urlopen(
            f"http://{self.server_address}/view?{url_values}", timeout=60
        ) as response:
            return response.read()

    def _load_workflow(self):
        """Load the ComfyUI workflow JSON from file."""
        with open(self.workflow_path) as f:
            return json.load(f)

    def _build_prompt_api(self, workflow_json, refined_prompt):
        """
        Transform the workspace JSON to ComfyUI API Prompt format.
        ComfyUI API expects a map of node_id -> {inputs, class_type}.
        """
        prompt_api = {}

        for node in workflow_json.get("nodes", []):
            node_id = str(node["id"])
            class_type = node["type"]
            inputs = {}

            # Add links from 'inputs' list in workspace JSON
            if "inputs" in node:
                for input_item in node["inputs"]:
                    if "link" in input_item and input_item["link"] is not None:
                        link_id = input_item["link"]
                        for link in workflow_json.get("links", []):
                            if link[0] == link_id:
                                origin_node_id = str(link[1])
                                origin_slot = link[2]
                                inputs[input_item["name"]] = [origin_node_id, origin_slot]
                                break

            # Skip non-functional nodes
            if class_type == "MarkdownNote":
                continue
            # WORKFLOW_DEPENDENCY: Node 45 is the positive prompt node in the
            # default workflow (scripts/example_workflow.json). If using a
            # different workflow, this may need adjustment.
            POSITIVE_PROMPT_NODE_ID = 45

            # Map widgets_values to inputs based on node type
            if class_type == "CLIPTextEncode":
                inputs["text"] = (
                    refined_prompt
                    if node["id"] == POSITIVE_PROMPT_NODE_ID
                    else node.get("widgets_values", [""])[0]
                )
            elif class_type == "CLIPLoader":
                inputs["clip_name"] = node["widgets_values"][0]
                inputs["type"] = node["widgets_values"][1]
                inputs["device"] = node["widgets_values"][2]
            elif class_type == "VAELoader":
                inputs["vae_name"] = node["widgets_values"][0]
            elif class_type == "UNETLoader":
                inputs["unet_name"] = node["widgets_values"][0]
                inputs["weight_dtype"] = node["widgets_values"][1]
            elif class_type == "ModelSamplingAuraFlow":
                inputs["shift"] = node["widgets_values"][0]
            elif class_type == "EmptySD3LatentImage":
                # User requested 278:398 aspect ratio.
                # Scaling up to 834x1194 for quality.
                inputs["width"] = 834
                inputs["height"] = 1194
                inputs["batch_size"] = node["widgets_values"][2]
            elif class_type == "KSampler":
                inputs["seed"] = random.randint(1, 2**53)
                inputs["control_after_generate"] = node["widgets_values"][1]
                inputs["steps"] = node["widgets_values"][2]
                inputs["cfg"] = node["widgets_values"][3]
                inputs["sampler_name"] = node["widgets_values"][4]
                inputs["scheduler"] = node["widgets_values"][5]
                inputs["denoise"] = node["widgets_values"][6]
            elif class_type == "SaveImage":
                inputs["filename_prefix"] = node["widgets_values"][0]

            prompt_api[node_id] = {
                "inputs": inputs,
                "class_type": class_type,
            }

        return prompt_api

    def generate_cover(self, book_title, book_description, output_path, refined_prompt=None):
        """
        Generate a book cover image and save it to output_path.

        Args:
            book_title: Title of the book.
            book_description: Short description for the image prompt.
            output_path: Absolute path to save the generated PNG.
            refined_prompt: Optional pre-refined LLM prompt. If None, it builds one.

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Check if ComfyUI is reachable
            try:
                urllib.request.urlopen(
                    f"http://{self.server_address}/system_stats", timeout=5
                )
            except Exception:
                return False, f"ComfyUI server not reachable at {self.server_address}"

            # Load workflow
            if not os.path.exists(self.workflow_path):
                return False, f"Workflow file not found: {self.workflow_path}"

            workflow_json = self._load_workflow()

            # Build or use prompt
            if not refined_prompt:
                refined_prompt = (
                    f"Professional book cover art for '{book_title}'. "
                    f"{book_description}. "
                    "High quality, cinematic, dramatic lighting, artistic style."
                )

            logger.info(f"Using refined prompt for {book_title}: {refined_prompt}")
            prompt_api = self._build_prompt_api(workflow_json, refined_prompt)

            # Connect via websocket and submit
            import websocket

            ws = websocket.WebSocket()
            ws.settimeout(120)  # 2 min timeout for generation
            ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

            logger.info(f"Queueing book cover generation for: {book_title}")
            prompt_response = self._queue_prompt(prompt_api)
            prompt_id = prompt_response["prompt_id"]

            # Wait for completion
            output_images = {}
            while True:
                out = ws.recv()
                if isinstance(out, str):
                    message = json.loads(out)
                    if message["type"] == "executing":
                        data = message["data"]
                        if data["node"] is None and data["prompt_id"] == prompt_id:
                            break  # Execution is done
                    elif message["type"] == "executed":
                        if message["data"]["prompt_id"] == prompt_id:
                            node_output = message["data"]["output"]
                            if "images" in node_output:
                                node_id = message["data"]["node"]
                                output_images[node_id] = node_output["images"]

            ws.close()
            logger.info(f"Book cover generation complete for: {book_title}")

            # Download and save the first image
            if not output_images:
                return False, "No images were generated"

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            for _node_id, images in output_images.items():
                for image_info in images:
                    image_data = self._get_image(
                        image_info["filename"],
                        image_info["subfolder"],
                        image_info["type"],
                    )
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    logger.info(f"Book cover saved: {output_path}")
                    return True, None  # Success on first image

            return False, "Failed to download generated image"

        except ImportError:
            return False, "websocket-client package not installed. Install with: pip install websocket-client"
        except Exception as e:
            logger.error(f"Book cover generation failed for '{book_title}': {e}", exc_info=True)
            return False, str(e)
