# x9 — Reflected XSS automation

Automation tool to generate URL payloads for **reflected XSS** testing and send HTTP requests (GET/POST/both).
Intended for security testing. 

**Do not** use against targets without authorization.

---

## Features

* Read lists of URLs and parameters from files.
* Generate URL variations using different strategies.
* Send requests with GET, POST or BOTH.
* Chunk parameters to control payload size.
* Support custom HTTP headers file.
* Optional proxy support, SSL forcing, delay between requests, and silent mode.

---

## Installation

Copy the script to your machine, make it executable and run with Python 3.8+:

```bash
# if distributed as x9.py
chmod +x x9.py
./x9.py -h
```

If it's packaged, install however your project specifies (pip, etc.). The examples below assume a CLI binary named `x9`.

---

## Quick usage

```
usage: x9 [-h] -u URLS -p PARAMS [-ch CHUNK_SIZE] -me {GET,POST,BOTH} [-f HEADERS] [-s]
          [-d DELAY] [-x PROXY] [--ssl] [-sg STRATEGY [STRATEGY ...]]
```

Minimum: provide a URLs file and a params file, and choose a method:

```bash
x9 -u urls.txt -p params.txt -me GET
```

---

## Files & formats

### `urls.txt`

One target URL per line. Use `{PARAM}` placeholder where you want the parameter inserted (optional). If no placeholder exists the tool will append query string parameters for GET.

Examples:

```
https://example.com/search?q={PARAM}
https://example.com/page
http://test.local/view?id={PARAM}
```

### `params.txt`

One parameter name per line (or `name=value` pairs if you want preset values). Typically list parameter names to be tested.

Examples (just names):

```
q
id
search
name
```

Or with values:

```
q=<script>alert(1)</script>
id=1'><img src=x onerror=alert(1)>
```

If you supply names only, the tool will inject payload templates for testing reflected XSS.

### `headers.txt`

Optional. One header per line in the form `Header-Name: value`.

Example:

```
User-Agent: Mozilla/5.0 (x9)
Referer: https://example.com/
Authorization: Bearer <token>
```

---

## Options explained

* `-u, --urls URLS` — Path to URLs file (required).
* `-p, --params PARAMS` — Path to parameters file (required).
* `-ch, --chunk-size CHUNK_SIZE` — How many parameters to group per generated request. Default `10`. Useful to avoid extremely long queries or to test parameters in manageable batches.
* `-me, --method {GET,POST,BOTH}` — HTTP method to use.

  * `GET`: sends payloads in query string.
  * `POST`: sends payloads as `application/x-www-form-urlencoded` POST body.
  * `BOTH`: will attempt both GET and POST for each target.
* `-f, --headers HEADERS` — Path to headers file (optional).
* `-s, --silent` — Suppress output messages; useful for piping or when running in background loggers.
* `-d, --delay DELAY` — Delay in seconds between requests. Default `0`.
* `-x, --proxy PROXY` — Proxy URL, e.g. `socks5://127.0.0.1:9050` or `http://127.0.0.1:8080`.
* `--ssl` — Force HTTPS. If a URL is `http://`, the tool will convert it to `https://` before sending.
* `-sg STRATEGY [STRATEGY ...]` — URL generation strategies. Possible values:

  * `ignore` — skip parameters that are not present in the URL (i.e., only test parameters where `{PARAM}` placeholder exists). Good when you want to only test specific injection points.
  * `normal` — standard generation: append or replace parameters on the URL using each parameter individually.
  * `combine` — combine multiple parameters in a single request according to `--chunk-size`. Useful to test interactions between parameters.

  You can pass one or multiple strategies (e.g. `-sg normal combine`); the tool will run them in order.

> The help text may show repeated strategy names; treat them as single tokens `ignore`, `normal`, `combine`.

---

## Examples

### Basic GET test

```bash
x9 -u urls.txt -p params.txt -me GET
```

### POST with custom headers and 1s delay

```bash
x9 -u urls.txt -p params.txt -me POST -f headers.txt -d 1
```

### Test both GET and POST, chunk params into groups of 5, use combine strategy

```bash
x9 -u urls.txt -p params.txt -me BOTH -ch 5 -sg combine normal
```

### Force HTTPS through an HTTP URL and route via SOCKS5 proxy (e.g., Tor)

```bash
x9 -u urls.txt -p params.txt -me GET --ssl -x socks5://127.0.0.1:9050
```

### Silent run (no stdout)

```bash
x9 -u urls.txt -p params.txt -me GET -s
```

---

## Behavior notes & tips

* **Chunk size**: when `combine` is used the tool will group up to `CHUNK_SIZE` parameters per generated request. If you set `-ch 1` it will behave like single-parameter tests.
* **Placeholder `{PARAM}`**: if present in a URL, the tool will replace it with `paramname=payload`. If absent the tool will append parameters in query string (GET) or in body (POST).
* **Payloads**: by default the script injects a set of XSS payload templates. You can modify the payload set in the script if you want custom payloads or different encodings (URL-encoding, HTML-encoding).
* **Headers**: if you set a `Content-Type` header in `headers.txt`, ensure it matches what the tool sends (`application/x-www-form-urlencoded` for POST by default).
* **Proxy**: proxy URL must include scheme (`http://`, `socks5://`) and host\:port.
* **SSL**: `--ssl` forcibly switches `http://` to `https://`; it does not validate or manage certificates beyond standard Python/requests behavior.
* **Concurrency**: this tool is sequential by default. If you need concurrency, extend the script carefully and respect target rate limits and legal constraints.

---

## Example files

`urls.txt`

```
https://vulnerable.app/search?q={PARAM}
https://vulnerable.app/view
```

`params.txt`

```
q
id
name
```

`headers.txt`

```
User-Agent: x9/1.0
Accept-Language: en-US
```

---

## Responsible disclosure & legal

You must have **explicit permission** to test any target with this tool. Unauthorized scanning or attacking is illegal in many jurisdictions. Use only on:

* your own assets, or
* targets for which you have written permission (scope defined), or
* authorized bug bounty programs that permit automated testing.

If you discover a vulnerability, follow the target's responsible disclosure policy or bug bounty rules.

---

## Troubleshooting

* If requests fail via proxy, verify proxy syntax and that it’s reachable.
* If headers are ignored, ensure there are no duplicate headers in the script overriding your file.
* If you see too many false positives, increase `-d` delay, or reduce `-ch` chunk size.

---

## Extending the tool

Ideas for improvements:

* Add output reporters (CSV/JSON) with request/response captures and reflection markers.
* Add rate-limiting and concurrency controls.
* Add payload encoders (URL-encode, double-encode, base64).
* Add response analyzers to auto-detect reflections and context (HTML attribute, JS context, tag context).

---

## License & Contributing

Use, modify, or redistribute under your chosen license. If contributing, open PRs with focused changes and tests for payload generation and headers handling.

---

## Minimal README footer (copy-paste)

```markdown
# x9 — Reflected XSS automation & HTTP request generator

> Automation for reflected XSS: generate URLs and send HTTP requests (GET/POST/BOTH).

## Usage
x9 -u urls.txt -p params.txt -me GET

## Options
- -u/--urls: path to URLs file
- -p/--params: path to params file
- -ch/--chunk-size: default 10
- -me/--method: GET, POST or BOTH
- -f/--headers: path to headers file
- -s/--silent: silent mode
- -d/--delay: seconds between requests (default 0)
- -x/--proxy: proxy URL (socks5://host:port)
- --ssl: force HTTPS
- -sg/--strategy: one or more of [ignore, normal, combine]

## Warning
Only test targets you own or are authorized to test.
```

---

If you want, I can also:

* produce a ready-to-run `README.md` file and example `urls.txt`, `params.txt`, `headers.txt` packaged together, or
* generate a sample JSON/CSV reporter template the tool could output. Which would you prefer?
