| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-H2 | ESP32-P4 | ESP32-S2 | ESP32-S3 | Linux |
| ----------------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | -------- | -------- | -------- | ----- |

# Simple HTTPD Server Example

The Example consists of HTTPD server demo with demonstration of URI handling :
    1. URI \hello for GET command returns "Hello World!" message
    2. URI \echo for POST command echoes back the POSTed message
    3. URI \sse for GET command sends a message to client every second


Add cjson dep - 
```bash
idf.py add-dependency "espressif/cjson"
```

## Updated Structure

```txt
http_server_test/
├── CMakeLists.txt                    Root ESP-IDF project (MINIMAL_BUILD)
├── sdkconfig.defaults                Baseline device config
├── sdkconfig.ci{,.ipv6_only,.sse}    CI config variants
├── sdkconfig                         Local, gitignored
├── dependencies.lock                 idf_component.yml lock
├── requirements.txt                  Python deps (cffi, jinja2)
├── package.json / package-lock.json  Tailwind CLI orchestration
├── pytest_http_server_simple.py      Root-level HTTP smoke test
├── README.md
│
├── components/
│   └── cJSON/                        Vendored cJSON (upstream, 130+ files)
│       ├── cJSON.c/.h, cJSON_Utils.c/.h, CMakeLists.txt
│       ├── fuzzing/  library_config/  tests/ (unity)
│       └── README.md  LICENSE  Makefile  test.c
│
├── main/                             ── FIRMWARE (ESP-IDF component)
│   ├── CMakeLists.txt                Compiles main.c + wifi.c ONLY
│   ├── idf_component.yml
│   ├── Kconfig.projbuild
│   ├── main.c                        Entry point
│   ├── wifi.c / wifi.h
│   ├── state/
│   │   ├── state.c / state.h
│   │   ├── state_struct.h            ★ Authoritative POD structs (cffi source)
│   │   └── state_selftest.c
│   ├── events.c / events.h           ★ Not compiled yet
│   ├── web_api.c / web_api.h         ★ Not compiled yet
│   ├── web_assets.c (0 B)            ★ Empty — asset embedding target
│   ├── web_assets.h (0 B)            ★ Empty
│   └── web/                          ── BUILD-TIME PYTHON TOOLING
│       ├── schema.py                 cffi → dynamic dataclasses
│       ├── mock_data.py              Synthetic state + SSE payloads
│       ├── preview.py                Threaded preview server
│       ├── build_web.py              Stateless Jinja renderer
│       ├── ffi_build.py (0 B)        Deferred cffi API-mode build
│       └── __pycache__/              ★ Committed .pyc files (gitignored rule missed them)
│
├── templates/                        ── JINJA SOURCES (build time only)
│   ├── index.html
│   ├── pages/live_demo.html
│   └── components/
│       ├── layout/{top_navbar.html, footer.html (0 B)}
│       └── dashboard/
│           ├── title.html
│           ├── test_reading.html     Data-free placeholders
│           └── test_chart.html       uPlot + SSE
│
├── static/                           ── SERVED VERBATIM
│   ├── css/{build.css (13 KB), uplot.css}
│   ├── img/temp_logo.svg
│   └── js/
│       ├── app.js (2.3 KB)           ★ Shared /api/state + single SSE
│       ├── htmx.min.js (52 KB)      Loaded; SSE extension unused
│       ├── sse.min.js (2.9 KB)      Loaded; unused
│       └── uplot.js (36 KB)         uPlot 1.6.7
│
├── tailwind/
│   ├── input.css                     Theme/palette source
│   ├── package.json
│   └── readme.md
│
├── build/                            ESP-IDF output (gitignored)
├── node_modules/                     Tailwind install (gitignored)
└── .venv/                            Python env (gitignored)
```

## User Callback

The example includes a simple user callback that can be used to get the SSL context (connection information) when the server is being initialized. To enable the user callback, set `CONFIG_EXAMPLE_ENABLE_HTTPS_USER_CALLBACK` to `y` in the project configuration menu.

## Server-Sent Events (SSE)

The example also includes a simple SSE handler (having endpoint \sse), which sends a message to the client every second. To enable SSE, set `CONFIG_EXAMPLE_ENABLE_SSE_HANDLER` to `y` in the project configuration menu.

## How to use example

### Hardware Required

* A development board with ESP32/ESP32-S2/ESP32-C3 SoC (e.g., ESP32-DevKitC, ESP-WROVER-KIT, etc.)
* A USB cable for power supply and programming

### Configure the project

```
idf.py menuconfig
```
* Open the project configuration menu (`idf.py menuconfig`) to configure Wi-Fi or Ethernet. See "Establishing Wi-Fi or Ethernet Connection" section in [examples/protocols/README.md](../../README.md) for more details.

### Build and Flash

Build the project and flash it to the board, then run monitor tool to view serial output:

```
idf.py -p PORT flash monitor
```

(Replace PORT with the name of the serial port to use.)

(To exit the serial monitor, type ``Ctrl-]``.)

See the Getting Started Guide for full steps to configure and use ESP-IDF to build projects.

### Test the example :
        * run the test script : "python scripts/client.py \<IP\> \<port\> \<MSG\>"
            * the provided test script first does a GET \hello and displays the response
            * the script does a POST to \echo with the user input \<MSG\> and displays the response
        * or use curl (assuming IP is 192.168.43.130):
            1. "curl 192.168.43.130:80/hello"  - tests the GET "\hello" handler
            2. "curl -X POST --data-binary @anyfile 192.168.43.130:80/echo > tmpfile"
                * "anyfile" is the file being sent as request body and "tmpfile" is where the body of the response is saved
                * since the server echoes back the request body, the two files should be same, as can be confirmed using : "cmp anyfile tmpfile"
            3. "curl -X PUT -d "0" 192.168.43.130:80/ctrl" - disable /hello and /echo handlers
            4. "curl -X PUT -d "1" 192.168.43.130:80/ctrl" -  enable /hello and /echo handlers

## Example Output
```
I (9580) example_connect: - IPv4 address: 192.168.194.219
I (9580) example_connect: - IPv6 address: fe80:0000:0000:0000:266f:28ff:fe80:2c74, type: ESP_IP6_ADDR_IS_LINK_LOCAL
I (9590) example: Starting server on port: '80'
I (9600) example: Registering URI handlers
I (66450) example: Found header => Host: 192.168.194.219
I (66460) example: Request headers lost
```

## Troubleshooting
* If the server log shows "httpd_parse: parse_block: request URI/header too long", especially when handling POST requests, then you probably need to increase HTTPD_MAX_REQ_HDR_LEN, which you can find in the project configuration menu (`idf.py menuconfig`): Component config -> HTTP Server -> Max HTTP Request Header Length


