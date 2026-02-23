import websocket # pip install websocket-client
import uuid
import json
import urllib.request
import urllib.parse

server_address = "localhost:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    try:
        req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        print(f"ComfyUI Error: {e.code} {e.reason}")
        print(e.read().decode('utf-8'))
        raise

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def generate_book_cover(book_title, book_description, workflow_json):
    # 1. Prepare the Prompt
    refined_prompt = f"Professional book cover art for '{book_title}'. {book_description}. High quality, historical epic style."

    # 2. Transform the workspace JSON to ComfyUI API Prompt format
    # ComfyUI API expects a map of node_id -> {inputs, class_type}
    prompt_api = {}

    # Map workspace nodes to API nodes
    for node in workflow_json.get("nodes", []):
        node_id = str(node["id"])
        class_type = node["type"]
        inputs = {}

        # 1. Add links from 'inputs' list in workspace JSON
        if "inputs" in node:
            for input_item in node["inputs"]:
                if "link" in input_item and input_item["link"] is not None:
                    # We need to find which node/output this link comes from
                    # In workspace JSON, links are in a separate 'links' list: [id, origin_id, origin_slot, target_id, target_slot, type]
                    link_id = input_item["link"]
                    for link in workflow_json.get("links", []):
                        if link[0] == link_id:
                            origin_node_id = str(link[1])
                            origin_slot = link[2]
                            inputs[input_item["name"]] = [origin_node_id, origin_slot]
                            break

        # 2. Add values from 'widgets_values'
        # This is tricky because we need to know the widget names.
        # For this specific workflow, we can handle the known nodes.
        if class_type == "MarkdownNote":
            continue

        if class_type == "CLIPTextEncode":
            inputs["text"] = refined_prompt if node["id"] == 45 else node.get("widgets_values", [""])[0]
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
            inputs["width"] = node["widgets_values"][0]
            inputs["height"] = node["widgets_values"][1]
            inputs["batch_size"] = node["widgets_values"][2]
        elif class_type == "KSampler":
            inputs["seed"] = node["widgets_values"][0]
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
            "class_type": class_type
        }

    # 3. Connect and Listen
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")

    print(f"Queueing generation for: {book_title}")
    prompt_response = queue_prompt(prompt_api)
    prompt_id = prompt_response['prompt_id']

    # 4. Wait for completion and track outputs
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break # Execution is done
            elif message['type'] == 'executed':
                # This message contains node output info
                if message['data']['prompt_id'] == prompt_id:
                    node_output = message['data']['output']
                    if 'images' in node_output:
                        node_id = message['data']['node']
                        output_images[node_id] = node_output['images']
        else:
            continue

    print("Generation complete.")

    # 5. Download and save images locally
    for node_id, images in output_images.items():
        for image_info in images:
            image_data = get_image(image_info['filename'], image_info['subfolder'], image_info['type'])
            local_filename = f"generated_{book_title.lower().replace(' ', '_')}_{image_info['filename']}"
            with open(local_filename, "wb") as f:
                f.write(image_data)
            print(f"Saved: {local_filename}")

    ws.close()

# --- RUNNING THE CODE ---
if __name__ == "__main__":
    # Load your JSON from the file
    with open("scripts/example_workflow.json", "r") as f:
        raw_workflow = json.load(f)

    book_name = "Echoes of Empire"
    book_desc = "A journey through India's pre-1800 history, ancient civilizations, and Mughal palaces."

    generate_book_cover(book_name, book_desc, raw_workflow)
