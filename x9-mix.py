#!/usr/bin/env python3

import argparse
import os
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, unquote
import requests
from concurrent.futures import ThreadPoolExecutor
import time
import subprocess


def load_file(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist")
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]


def load_headers(file_path):
    headers = {}
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip()] = value.strip()
    return headers


def chunk_data_generator(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def create_urls_with_combine_strategy(base_urls, params, chunk_size, ssl, headers):
    all_generated_urls = []
    values = [
        'joojooham"',
        'joojooham\\"',
        "joojooham'",
        "joojooham\\'",
        'joojooham`',
        'joojooham\\`',
        'joojooham<'
    ]

    for base_url in base_urls:

        url_parts = list(urlparse(base_url))
        query_params = parse_qs(url_parts[4])

        for key in query_params:
            query_params[key] = query_params[key][0]

        for key in query_params:
            original_value = query_params[key]
            for value in values:
                modified_params = query_params.copy()
                modified_params[key] = original_value + value
                url_parts[4] = "&".join(f"{k}={str(v)}" for k, v in modified_params.items())
                scheme = "https" if ssl else (
                    "https" if ":443" in url_parts[0] or url_parts[0].startswith("https") else "http"
                )
                url_parts[0] = f"{scheme}"
                all_generated_urls.append(urlunparse(url_parts))

        for value in values:
            for key in query_params:
                modified_params = query_params.copy()
                modified_params[key] = value
                url_parts[4] = "&".join(f"{k}={str(v)}" for k, v in modified_params.items())
                all_generated_urls.append(urlunparse(url_parts))
    return all_generated_urls

def create_urls_with_ignore_strategy(base_urls, params, chunk_size, ssl, headers):
    all_generated_urls = []
    value_variations = [
        'joojooham"',
        'joojooham\\"',
        "joojooham'",
        "joojooham\\'",
        'joojooham`',
        'joojooham\\`',
        'joojooham<'
    ]
    fparams = []
    for base_url in base_urls:
        # "fallparams" command used for mine parameter
        cmdHeaders = []
        for key, value in headers.items():
            cmdHeaders += ['-H']
            cmdHeaders += [f'{key}: {value}']
        cmd = ["fallparams", "-o", "x9-temp-parameters.txt", "-u", base_url]
        cmd += cmdHeaders
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            fparams += load_file("x9-temp-parameters.txt")
        except FileNotFoundError:
            pass
        finally:
            pass

    params = fparams + params
    uniqueparams = list(dict.fromkeys(params))
    uniqueparams.sort()
    for base_url in base_urls:
        url_parts = list(urlparse(base_url))
        for chunk in chunk_data_generator(uniqueparams, chunk_size):

            for value in value_variations:
                # Prepare new parameters for the chunk
                new_params = [(param, value) for param in chunk]

                # Build the full query string and update the URL

                url_parts[4]= "&".join(f"{key}={str(value)}" for key, value in new_params)
                scheme = "https" if ssl else (
                    "https" if ":443" in url_parts[0] or url_parts[0].startswith("https") else "http"
                )
                url_parts[0] = f"{scheme}"
                generated_url = urlunparse(url_parts)
                all_generated_urls.append(generated_url)

    return all_generated_urls
def create_urls_with_normal_strategy(base_urls, params, chunk_size, ssl, headers):
    all_generated_urls = []
    value_variations = [
        'joojooham"',
        'joojooham\\"',
        "joojooham'",
        "joojooham\\'",
        'joojooham`',
        'joojooham\\`',
        'joojooham<'
    ]
    fparams = []
    for base_url in base_urls:
        # "fallparams" command used for mine parameter
        cmdHeaders = []
        for key, value in headers.items():
            cmdHeaders += ['-H']
            cmdHeaders += [f'{key}: {value}']
        cmd = ["fallparams", "-o", "x9-temp-parameters.txt", "-u", base_url]
        cmd += cmdHeaders
        result = subprocess.run(cmd, capture_output=True, text=True)

        try:
            fparams += load_file("x9-temp-parameters.txt")
        except FileNotFoundError:
            pass
        finally:
            pass

    params = fparams + params
    uniqueparams = list(dict.fromkeys(params))
    uniqueparams.sort()
    for base_url in base_urls:
        url_parts = list(urlparse(base_url))
        existing_params = parse_qs(url_parts[4])  # Parse existing query params
        # todo  params  - existing_params
        if len(existing_params) != 0:
            for chunk in chunk_data_generator(uniqueparams, chunk_size):

                for value in value_variations:
                    # Prepare new parameters for the chunk
                    new_params = [(param, value) for param in chunk]

                    # Merge with existing parameters (if any)
                    merged_params = []
                    if existing_params:
                        for key, values in existing_params.items():
                            merged_params.extend((key, val) for val in values)

                    merged_params.extend(new_params)

                    # Build the full query string and update the URL
                    url_parts[4] = "&".join(f"{key}={str(value)}" for key, value in merged_params)
                    scheme = "https" if ssl else (
                        "https" if ":443" in url_parts[0] or url_parts[0].startswith("https") else "http"
                    )
                    url_parts[0] = f"{scheme}"
                    generated_url = urlunparse(url_parts)
                    all_generated_urls.append(generated_url)

    return all_generated_urls


def send_http_request(url, method, headers, delay, proxy, silent):
    time.sleep(delay)  # تأخیر بین هر درخواست
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, proxies=proxy)
        elif method == "POST":
            # POST method body create and remove GET method body :
            url_parts = list(urlparse(url))
            data = parse_qs(url_parts[4])
            url_parts[4] = ""
            url = urlunparse(url_parts)
            response = requests.post(url, headers=headers, proxies=proxy, data=data)
        else:
            raise ValueError("Invalid HTTP method")

        if response.status_code != 200:
            if not silent:
                print(f"\033[91m {response.status_code}\033[0m")
        return response.text
    except requests.RequestException as e:
        print(f"Error making {method} request to {url}: {e}")
        return ""

def check_response_for_keywords(response_text, keywords):
    # if is_encoded(ressponse_text):
    #     return False

    for keyword in keywords:
        if keyword in response_text:
            return True

    return False


def process_urls_in_batches(base_urls, params, chunk_size, method, headers, silent, delay, proxy, ssl, strategy):
    keywords = [
        'joojooham""', "joojooham''",
        'joojooham\\""', "joojooham\\''",
        "joojooham``", "joojooham\\``", 'joojooham<'
    ]

    for i in range(0, len(base_urls), 5):
        batch_urls = base_urls[i:i + 5]
        total_in_batch = len(batch_urls)

        if not silent:
            print(f"Processing batch {i // 5 + 1}...")

        # Generate URLs for the batch
        generated_urls = strategy(batch_urls, params, chunk_size, ssl, headers)

        # Save generated URLs to file
        with open('generated_urls_mix.txt', 'a') as file:
            for url in generated_urls:
                file.write(url + '\n')

            # Send HTTP requests and check responses
            for batch_index, batch in enumerate(chunk_data_generator(generated_urls, 20)):
                futures = []

                with ThreadPoolExecutor(max_workers=10) as executor:
                    for url in batch:
                        futures.append(executor.submit(send_http_request, url, method, headers, delay, proxy, silent))

                    for index, future in enumerate(futures):
                        response_text = future.result()

                        if check_response_for_keywords(response_text, keywords):
                            with open('res_mix.txt', 'a') as res_file:
                                res_file.write(" Method : \033[94m" + method + "\033[0m          " + batch[index] +  '\n')
                                print("\033[94m	added some result\033[0m")

                        # Update this line to reflect the correct counting per batch
                        print(f"URL {batch_index * 20 + index + 1}/{len(generated_urls)} in batch {i // 5 + 1} completed.")

                if not silent:
                    print(f"Batch {i // 5 + 1} completed.")

                if not silent:
                    print(f"Waiting for {delay} seconds before the next request...")
                time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description='Generate URLs with normal strategy and send HTTP requests.')
    parser.add_argument('-u', '--urls', required=True, help='Path to the file containing URLs.')
    parser.add_argument('-p', '--params', required=True, help='Path to the file containing parameters.')
    parser.add_argument('-ch', '--chunk-size', type=int, default=10,
                        help='Size of each chunk of parameters. Default is 10.')
    parser.add_argument('-me', '--method', required=True, choices=['GET', 'POST', 'BOTH'],
                        help='HTTP method to use (GET or POST or BOTH).')
    parser.add_argument('-f', '--headers', help='Path to the file containing HTTP headers.')
    parser.add_argument('-s', '--silent', action='store_true', help='Run in silent mode (no output messages).')
    parser.add_argument('-d', '--delay', type=float, default=0, help='Delay in seconds between requests. Default is 0.')
    parser.add_argument("-x", dest="proxy", help="Proxy URL (e.g. socks5://0.0.0.0:9050)", default=None)
    parser.add_argument("--ssl", dest="ssl", help="Force usage of SSL/HTTPS", action="store_true")
    parser.add_argument('-sg', nargs='+', dest="strategy", help="url generation strategy (ignoreignoreignoreignore , normalnormalnormalnormal , combinecombinecombinecombine)")
    args = parser.parse_args()
    proxy = {
        "http": args.proxy,
        "https": args.proxy,
    } if args.proxy else None
    base_urls = load_file(args.urls)
    params = load_file(args.params)
    headers = load_headers(args.headers) if args.headers else {}

    strategyMapper = {
        "normal"  : create_urls_with_normal_strategy,
        "ignore"  : create_urls_with_ignore_strategy,
        "combine" : create_urls_with_combine_strategy
    }
    strategies = []
    for arg in args.strategy:
        strategies.append(strategyMapper[arg])
    for strategy in strategies:
        print(f"\033[93m	{strategy} \033[0m")
        if args.method == "BOTH":
            for method in ["GET", "POST"]:
                process_urls_in_batches(base_urls, params, args.chunk_size, method, headers, args.silent, args.delay, proxy,
                                    args.ssl, strategy)
        else:
            process_urls_in_batches(base_urls, params, args.chunk_size, args.method, headers, args.silent, args.delay,
                                    proxy, args.ssl, strategy)
        print("Filtered URLs with matching keywords saved to res_normal.txt.")


if __name__ == '__main__':
    main()
