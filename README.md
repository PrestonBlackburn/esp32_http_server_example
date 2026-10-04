| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C5 | ESP32-C6 | ESP32-C61 | ESP32-H2 | ESP32-P4 | ESP32-S2 | ESP32-S3 | Linux |
| ----------------- | ----- | -------- | -------- | -------- | -------- | --------- | -------- | -------- | -------- | -------- | ----- |

# Simple HTTPD Server Example




## Updated Structure

```txt
http_server_test/
├── CMakeLists.txt                    Root ESP-IDF project
│                                     ├─ SDKCONFIG_DEFAULTS "sdkconfig.defaults" (+ .secrets if present)
│                                     ├─ EXTRA_COMPONENT_DIRS → main/web_assets   ★ NEW
│                                     └─ MINIMAL_BUILD ON
├── sdkconfig.defaults                ★ 0 B — baseline config now empty
├── sdkconfig.ci                      CI config variant
├── sdkconfig.ci.ipv6_only            CI config variant
├── sdkconfig.ci.sse                  CI config variant
├── sdkconfig / .old / .secrets       Local only, gitignored
├── dependencies.lock                 Committed lock → espressif/cjson
├── requirements.txt                  jinja2, cffi
├── package.json                      Tailwind v4 CLI (@tailwindcss/cli ^4.3.3)
├── package-lock.json                 gitignored
├── pytest_http_server_simple.py      Stock ESP-IDF pytest harness (see gaps below)
├── README.md                         Contains "## Updated Structure" — STALE
│
├── main/                             ── FIRMWARE (ESP-IDF component "main")
│   ├── CMakeLists.txt                SRCS: main.c, wifi.c
│   │                                 REQUIRES: esp-tls nvs_flash esp_netif
│   │                                           esp_http_server web_assets
│   ├── idf_component.yml             ★ espressif/cjson: '*' + esp_stubs (linux only)
│   ├── Kconfig.projbuild
│   ├── main.c              (12 KB)   static_get_handler on "/*" → web_assets_find()
│   │                                        + Content-Encoding: gzip   [main.c:116-125]
│   ├── wifi.c / wifi.h
│   ├── state/
│   │   ├── state_struct.h   (427 B)  ★ Authoritative POD — cffi + C source of truth
│   │   │                             state_t, db_measure_t (include-free)
│   │   ├── state.h          (136 B)  Include shim
│   │   ├── state.c          (0 B)    ★ Empty placeholder
│   │   └── state_selftest.c (0 B)    ★ Empty placeholder
│   ├── events.c / events.h (0 B)     ★ Empty placeholders
│   ├── web_api.c / web_api.h (0 B)   ★ Empty placeholders
│   └── web_assets/                   ★ NEW standalone ESP-IDF component
│       ├── CMakeLists.txt (1.2 KB)   add_custom_command → build_web.py; EMBED_FILES *.gz
│       │                             DEPENDS on templates/, static/, tools/web/*.py,
│       │                             and main/state/state_struct.h
│       ├── web_assets.c    (1.9 KB)  DECLARE_ASSET table + web_assets_find()
│       └── web_assets.h    (233 B)   web_asset_t { data, len, mime }
│
├── tools/                            ★ NEW — build-time Python, moved OUT of firmware
│   └── web/
│       ├── schema.py      (4.3 KB)   cffi → dynamic dataclasses from state_struct.h
│       ├── mock_data.py   (7.7 KB)   Synthetic state + 300-pt window + SSE payloads
│       ├── preview.py     (4.3 KB)   Threaded preview server (/, /api/state, /events)
│       └── build_web.py   (2.0 KB)   Render pages/*.html, gzip static, flatten by basename
│
├── managed_components/               ★ REPLACES vendored components/cJSON/
│   └── espressif__cjson/
│       ├── CMakeLists.txt  idf_component.yml  Kconfig
│       ├── CHECKSUMS.json  sbom_cJSON.yml  LICENSE  README.md
│       └── cJSON/                      Upstream: cJSON.c/.h, cJSON_Utils.c/.h,
│                                       tests/ (unity), fuzzing/
│
├── templates/                        ── JINJA SOURCES (build time only)
│   ├── _base.html        (1.1 KB)    ★ RENAMED from index.html — {% block content %}
│   ├── pages/
│   │   └── live_demo.html (353 B)    {% extends '_base.html' %} — the only rendered page
│   └── components/
│       ├── layout/
│       │   ├── top_navbar.html (364 B)
│       │   └── footer.html      (0 B) ★ Still empty but included by _base.html:31
│       └── dashboard/
│           ├── title.html        (371 B)
│           ├── test_reading.html (4.2 KB)  Data-free `--` placeholders
│           └── test_chart.html   (3.6 KB)  uPlot + SSE consumer
│
├── static/                           ── SERVED VERBATIM (gzipped at build)
│   ├── css/
│   │   ├── build.css   (13.2 KB)     Tailwind v4 output — still @imports Google Fonts
│   │   └── uplot.css   (1.8 KB)
│   ├── img/temp_logo.svg (283 B)
│   └── js/
│       ├── app.js       (2.3 KB)    ★ Shared /api/state bootstrap + single EventSource
│       ├── htmx.min.js  (52.2 KB)
│       ├── sse.min.js   (2.9 KB)    Loaded by _base.html; native EventSource actually used
│       └── uplot.js     (36.3 KB)   uPlot 1.6.7
│
├── tailwind/
│   ├── input.css        (3.2 KB)    Theme/palette source
│   ├── package.json / package-lock.json
│   └── readme.md
│
├── build/                            ESP-IDF output (gitignored)
│   └── main/web_assets/web_out/*.gz  Rendered + gzipped assets (mtime=0, deterministic)
├── node_modules/                     Tailwind install (gitignored)
└── .venv/                            Python env (gitignored)
```

## Setup

Add cjson dep - 
```bash
idf.py add-dependency "espressif/cjson"
```

running
```bash
idf.py build
idf.py flash
idf.py monitor
```
Check output at the IP provided in the logs

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


