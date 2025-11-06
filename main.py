import argparse
import random
import sys
import os
import time
import logging
import concurrent.futures
import requests
import urllib.parse
import json

def _parse_size(value: str) -> tuple[int, int]:
    """Helper to parse WxH size format for argparse."""
    try:
        width, height = map(int, value.split('x'))
        return width, height
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid size format: '{value}'. Expected WxH (e.g., 512x512).")

def generate_image(prompt_text, output_file, args):
    """Generates a single image with retry logic."""
    # Use a random seed if one isn't provided
    # make seed number always different and large digits
    # min 5 digit max 8 digit
    if args.seed is not None:
        seed = args.seed
    else:
        seed = random.randint(10000, 99999999)
    
    width, height = args.size

    # Construct the URL and parameters for the requests call
    base_url = "https://image.pollinations.ai/prompt/"
    encoded_prompt = urllib.parse.quote_plus(prompt_text)
    
    params = {
        "model": args.model,
        "width": width,
        "height": height,
        "seed": seed,
        "nologo": str(args.nologo), # Convert boolean to string "True" or "False"
        "private": str(args.private), # Convert boolean to string
        "safe": str(args.safe), # Convert boolean to string
        "enhance": str(args.enhance), # Convert boolean to string
        "json": "False", # As per user's example
        "messages": "[]", # As per user's example
    }

    if args.referrer:
        params["referrer"] = args.referrer
    else:
        params["referrer"] = "pollinations-cli-requests" # Default referrer for this client

    if args.negative:
        params["negative"] = args.negative # Assuming negative is a query parameter for this endpoint

    full_url = f"{base_url}{encoded_prompt}"

    log_data = {
        "prompt": prompt_text,
        "output_file": output_file,
        "model": args.model,
        "width": width,
        "height": height,
        "seed": seed,
        "negative_prompt": args.negative,
        "nologo": args.nologo,
        "private": args.private,
        "safe": args.safe,
        "status": "pending",
        "enhance": args.enhance,
    }

    print(f"Generating image with prompt: '{prompt_text}' and seed: {seed}")

    for attempt in range(args.retries + 1):
        try:
            print(f"Attempt {attempt + 1} of {args.retries + 1}...")
            
            # Make the POST request to the Pollinations API
            response = requests.post(full_url, params=params, timeout=args.timeout)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            if args.save:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved to {output_file}")
            else:
                print("Image generated but not saved (due to --no-save).")

            if args.log_file:
                log_data["status"] = "success"
                logging.info(json.dumps(log_data))
            return True  # Indicate success
        except requests.exceptions.RequestException as e:
            print(f"Generation failed on attempt {attempt + 1}: {e}")
            if attempt < args.retries:
                print(f"Retrying in {args.retry_delay} seconds...")
                time.sleep(args.retry_delay)
        except Exception as e: # Catch other potential non-request-specific errors
            print(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            if attempt < args.retries:
                print(f"Retrying in {args.retry_delay} seconds...")
                time.sleep(args.retry_delay)
    
    if args.log_file:
        log_data["status"] = "failure"
        logging.info(json.dumps(log_data))
    
    print(f"All retry attempts failed for prompt: '{prompt_text}'")
    return False # Indicate failure

def main():
    # This part was added in a previous step but not in the provided context. Re-adding for completeness.
    parser = argparse.ArgumentParser(description="Generate images using Pollinations AI.")
    
    # Arguments for pollinations.Image
    parser.add_argument("prompt", type=str, help="The main prompt for the image generation.")
    parser.add_argument("-m", "--model", type=str, default="flux", help="The model to use for generation.")
    parser.add_argument("-S", "--size", type=_parse_size, default=(1024, 1024), help="The size of the generated image in WxH format (e.g., 512x512).")
    parser.add_argument("-s", "--seed", type=int, help="The seed for randomization. A random seed will be used if not provided.")
    parser.add_argument('--logo', action='store_false', dest='nologo', default=True, help="Add a logo to the image.")
    parser.add_argument('--private', action='store_true', help="Make the image private (default is public).")
    parser.add_argument('--safe', action='store_true', default=False, help="Enable safe mode.")
    parser.add_argument("--referrer", type=str, default=None, help="Set the referrer.")
    parser.add_argument("--enhance", action='store_true', default=True, help="Enable image enhancement.")

    # Arguments for model.Generate
    parser.add_argument("-n", "--negative", type=str, default="", help="The negative prompt.")
    parser.add_argument("-o", "--output", type=str, help="The output filename. If not provided, a random name will be generated.")
    parser.add_argument('--no-save', action='store_false', dest='save', help="Do not save the image to a file.")
    parser.set_defaults(save=True) # By default, save the image unless --no-save is used

    parser.add_argument("-c", "--count", type=int, default=1, help="Number of images to generate per prompt.")
    # Retry arguments
    parser.add_argument("-r", "--retries", type=int, default=3, help="Number of times to retry generation on failure.")
    parser.add_argument("--retry-delay", type=int, default=5, help="Delay in seconds between retries.")
    
    # New argument for threads
    parser.add_argument("-t", "--threads", type=int, default=1, help="Number of concurrent threads to use for batch generation.")

    # Logging argument
    parser.add_argument("--log-file", type=str, help="Path to a file for logging generation details.")
    
    # Add a timeout argument for requests
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for the API request in seconds.")

    args = parser.parse_args()

    if args.log_file:
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(args.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Basic logging config for file output
        # For console output, a separate handler would be needed if desired
        logging.basicConfig(
            level=logging.INFO, format='%(asctime)s - %(message)s',
            filename=args.log_file, filemode='a'
        )

    prompt_source = args.prompt
    prompts = []

    if prompt_source == '-':
        print("Reading prompt from standard input...")
        prompts = [sys.stdin.read().strip()]
    elif os.path.isfile(prompt_source):
        print(f"Reading prompt from file: {prompt_source}")
        with open(prompt_source, 'r') as f:
            prompts = [line for line in f.read().strip().split('\n') if line.strip()]
    else:
        prompts = [prompt_source]

    if not prompts:
        parser.error("The prompt is empty. Provide a prompt string, a file path, or '-' for stdin.")

    is_batch = len(prompts) > 1
    is_multi_generation = is_batch or args.count > 1

    if is_multi_generation:
        if is_batch:
            print(f"Batch mode activated: Found {len(prompts)} prompts.")
        if args.count > 1:
            print(f"Count mode activated: Will generate {args.count} images per prompt.")
        
        # For multiple images, output must be a directory or not specified.
        if args.output and not os.path.isdir(args.output) and '.' in os.path.basename(args.output):
            parser.error("For multiple image generation (batch or count > 1), --output must be a directory, not a file.")
        
        # If output is a directory, ensure it exists
        if args.output and os.path.isdir(args.output):
            os.makedirs(args.output, exist_ok=True)

    # Prepare all tasks to be executed
    all_tasks = []
    for i, prompt in enumerate(prompts):
        for j in range(args.count):
            current_output_file = args.output
            
            # Determine the specific output filename for this task
            if is_multi_generation:
                filename = f"prompt_{i}_count_{j}_{random.randint(0, 1000000)}.jpeg"
                if current_output_file: # It must be a directory
                    current_output_file = os.path.join(current_output_file, filename)
                else: # No output directory specified, save in current dir
                    current_output_file = filename
            elif not current_output_file: # Single generation, no output specified
                current_output_file = f'image_{random.randint(0, 1000000)}.jpeg'
            
            all_tasks.append((prompt, current_output_file, args))

    total_requested = len(all_tasks)
    results = []

    if args.threads > 1 and is_multi_generation:
        print(f"Using {args.threads} threads for concurrent generation.")
        # max threads is only 2 if more than that server will reject
        if args.threads > 2:
            print("Warning: Maximum recommended threads is 2. Setting threads to 2.")
            args.threads = 2
            
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Submit tasks and collect futures
            futures = [executor.submit(generate_image, prompt_text, output_file, args) 
                       for prompt_text, output_file, args in all_tasks]
            
            # Iterate over completed futures to update progress bar and collect results
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
    else: # Sequential processing
        for prompt_text, output_file, args in all_tasks:
            results.append(generate_image(prompt_text, output_file, args))

    total_success = sum(results) # Count True results

    if total_success < total_requested:
        print(f"Generation finished. {total_success}/{total_requested} images generated successfully.")
        sys.exit(1)
    else:
        print(f"Generation finished. All {total_success} images generated successfully.")

if __name__ == "__main__":
    main()
