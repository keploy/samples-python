# main.py
import json
import random
import string

from flask import Flask, Response
import base64 

app = Flask(__name__)

# ---------- Deterministic helpers ----------

ALNUM = string.ascii_letters + string.digits
HEX = ''.join(sorted(set(string.hexdigits.lower()) - set('x')))
B64 = string.ascii_letters + string.digits + '+/'


def b64url_nopad(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

def fake_jwt(rng: random.Random) -> str:
    # Deterministic header/payload, random-looking signature from rng
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": stable_id("user", 3100, 8), "ts": FIXED_TIMESTAMP, "aud": "keploy-tests"}
    seg1 = b64url_nopad(json.dumps(header, sort_keys=True).encode())
    seg2 = b64url_nopad(json.dumps(payload, sort_keys=True).encode())
    sig  = b64url_nopad(bytes(rng.randrange(0, 256) for _ in range(32)))
    return f"{seg1}.{seg2}.{sig}"

def opaque_token(rng: random.Random, n: int = 40) -> str:
    # Matches your Bearer rule class: [A-Za-z0-9._~-]{20,}
    return rand(rng, string.ascii_letters + string.digits + "._~-", n)

def u_escape_qs(s: str) -> str:
    # JSON-style unicode escaping for '=' and '&'
    return s.replace("=", r"\u003d").replace("&", r"\u0026")

def pct_amp(s: str) -> str:
    # Percent-encode just ampersands after the token (your rule handles %26)
    return s.replace("&", "%26")


def rand(rng, charset, n):
    return ''.join(rng.choice(charset) for _ in range(n))

def aws_access_key_id(rng):
    return "AKIA" + ''.join(rng.choice(string.ascii_uppercase + string.digits) for _ in range(16))

def aws_secret_access_key(rng):
    return rand(rng, B64, 40)

def github_pat(rng):
    return "ghp_" + rand(rng, ALNUM, 36)

def slack_webhook(rng):
    return f"https://hooks.slack.com/services/{rand(rng, string.ascii_uppercase+string.digits,9)}/{rand(rng, string.ascii_uppercase+string.digits,9)}/{rand(rng, ALNUM,24)}"

def stripe_live_key(rng):
    return "sk_live_" + rand(rng, ALNUM, 28)

def google_api_key(rng):
    return "AIza" + rand(rng, ALNUM + "_-", 35)

def twilio_auth_token(rng):
    return rand(rng, HEX, 32)

def sendgrid_api_key(rng):
    return "SG." + rand(rng, B64, 22) + "." + rand(rng, B64, 43)

def datadog_api_key(rng):
    return rand(rng, HEX, 32)

def aws_s3_presigned_url(rng):
    bucket = f"bucket-{rand(rng, string.ascii_lowercase+string.digits,8)}"
    key = f"{rand(rng, string.ascii_lowercase,6)}/{rand(rng, ALNUM,16)}.bin"
    x_amz_cred = f"{rand(rng, string.digits,8)}/{rand(rng, string.digits,8)}/us-east-1/s3/aws4_request"
    return (
        f"https://{bucket}.s3.amazonaws.com/{key}"
        f"?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        f"&X-Amz-Credential={x_amz_cred}"
        f"&X-Amz-Date=20250101T000000Z"
        f"&X-Amz-Expires=900"
        f"&X-Amz-Signature={rand(rng, HEX, 64)}"
        f"&X-Amz-SignedHeaders=host"
    )

def azure_storage_conn_string(rng):
    return (
        "DefaultEndpointsProtocol=https;"
        f"AccountName={rand(rng, string.ascii_lowercase,12)};"
        f"AccountKey={rand(rng, B64, 88)};"
        "EndpointSuffix=core.windows.net"
    )

def mongo_uri(rng):
    return (
        f"mongodb+srv://{rand(rng, string.ascii_lowercase,6)}:"
        f"{rand(rng, ALNUM,16)}@cluster{rand(rng, string.ascii_lowercase+string.digits,5)}."
        f"{rand(rng, string.ascii_lowercase,6)}.mongodb.net/"
        f"{rand(rng, string.ascii_lowercase,6)}?retryWrites=true&w=majority&appName="
        f"{rand(rng, ALNUM,10)}"
    )

def postgres_url(rng):
    return (
        f"postgres://{rand(rng, string.ascii_lowercase,6)}:{rand(rng, ALNUM,14)}@"
        f"{rand(rng, string.ascii_lowercase,6)}.{rand(rng, string.ascii_lowercase,3)}.internal:5432/"
        f"{rand(rng, string.ascii_lowercase,6)}"
    )

def github_webhook_secret(rng):
    return rand(rng, ALNUM, 40)

def npm_token(rng):
    return "npm_" + rand(rng, ALNUM, 36)

def gcp_service_account_key_id(rng):
    return rand(rng, HEX, 8)

def gcp_service_account_email(rng):
    return f"{rand(rng, string.ascii_lowercase,10)}@{rand(rng, string.ascii_lowercase,8)}.iam.gserviceaccount.com"

def openai_api_key(rng):
    return "sk-" + rand(rng, ALNUM+"_", 48)

def cloudflare_api_token(rng):
    return rand(rng, HEX, 40)

def github_app_private_key_id(rng):
    return rand(rng, string.digits, 6)

# Catalog of secret generators
GENS = [
    ("aws_access_key_id", aws_access_key_id),
    ("aws_secret_access_key", aws_secret_access_key),
    ("aws_s3_presigned_url", aws_s3_presigned_url),
    ("github_pat", github_pat),
    ("github_webhook_secret", github_webhook_secret),
    ("slack_webhook_url", slack_webhook),
    ("stripe_live_key", stripe_live_key),
    ("google_api_key", google_api_key),
    ("twilio_auth_token", twilio_auth_token),
    ("sendgrid_api_key", sendgrid_api_key),
    ("datadog_api_key", datadog_api_key),
    ("azure_storage_connection_string", azure_storage_conn_string),
    ("mongodb_uri", mongo_uri),
    ("postgres_url", postgres_url),
    ("npm_token", npm_token),
    ("gcp_service_account_key_id", gcp_service_account_key_id),
    ("gcp_service_account_email", gcp_service_account_email),
    ("openai_api_key", openai_api_key),
    ("cloudflare_api_token", cloudflare_api_token),
    ("github_app_private_key_id", github_app_private_key_id),
]

# Fixed seeds and fixed timestamp string for full determinism
FIXED_TIMESTAMP = "2025-01-01T00:00:00Z"
COMMON_SEED = 20250909
UNIQUE_BASE_SEED = 777000

def generate_common_secrets():
    rng = random.Random(COMMON_SEED)
    commons = {}
    for name, gen in GENS:
        commons[name] = gen(rng)
    return commons

def generate_unique_secrets(endpoint_idx, count=40):
    rng = random.Random(UNIQUE_BASE_SEED + endpoint_idx * 111)
    out = {}
    i = 0
    while len(out) < count:
        name, gen = GENS[i % len(GENS)]
        key = f"{name}_{len(out)+1}"
        out[key] = gen(rng)
        i += 1
    return out

def stable_id(prefix, seed, n=24):
    rng = random.Random(seed)
    return prefix + '_' + rand(rng, ALNUM, n)

def deeply_nested_payload(endpoint_name, endpoint_idx):
    commons = generate_common_secrets()
    uniques = generate_unique_secrets(endpoint_idx)

    payload = {
        "status": 200,
        "reason": "OK",
        "meta": {
            "endpoint": endpoint_name,
            "timestamp": FIXED_TIMESTAMP,
            "version": "v1",
            "trace": {
                "session": {
                    "id": stable_id("sess", 1000 + endpoint_idx, 24),
                    "labels": ["sensitive", "test-fixture", "synthetic"],
                    "routing": {
                        "region": "us-east-1",
                        "fallback": False,
                        "partitions": [
                            {"name": "p0", "weight": 60},
                            {"name": "p1", "weight": 40},
                        ],
                    },
                }
            },
        },
        "data": {
            "page_info": {
                "id": stable_id("pg", 2000 + endpoint_idx, 8),
                "page_meta": {
                    "type": "LIST",
                    "floating_meta": {"stack": "HORIZONTAL", "arrangement": "SPACE_BETWEEN"},
                },
                "name": f"Deep Secret Dump {endpoint_name.upper()}",
                "layout_params": {
                    "background_color": "#0B1221",
                    "page_layout": [{"type": "widget", "id": "w-1"}, {"type": "widget", "id": "w-2"}],
                    "usePageLayout": True,
                },
                "seo_data": {"seo_desc": "Synthetic secrets for scanner testing", "tags": ["gitleaks", "testing"]},
            },
            "page_content": {
                "header_widgets": [
                    {
                        "id": 101,
                        "type": "BREADCRUMBS",
                        "data": {"breadcrumbs": [{"label": "Root"}, {"label": endpoint_name}]},
                    }
                ],
                "widgets": [
                    {
                        "id": "cfg-001",
                        "type": "CONFIG",
                        "data": {
                            "providers": {
                                "aws": {
                                    "iam": {
                                        "access_key_id": commons["aws_access_key_id"],
                                        "secret_access_key": commons["aws_secret_access_key"],
                                    },
                                    "s3": {"presigned_example": commons["aws_s3_presigned_url"]},
                                },
                                "github": {
                                    "pat": commons["github_pat"],
                                    "webhook_secret": commons["github_webhook_secret"],
                                },
                                "slack": {"webhook_url": commons["slack_webhook_url"]},
                                "stripe": {"live_key": commons["stripe_live_key"]},
                                "google": {"api_key": commons["google_api_key"]},
                            },
                            "databases": {
                                "mongo": {"uri": commons["mongodb_uri"]},
                                "postgres": {"url": commons["postgres_url"]},
                            },
                            "cloud": {
                                "azure": {"storage_connection_string": commons["azure_storage_connection_string"]},
                                "gcp": {
                                    "service_account": {
                                        "key_id": commons["gcp_service_account_key_id"],
                                        "email": commons["gcp_service_account_email"],
                                    }
                                },
                            },
                            "ml": {"openai": {"api_key": commons["openai_api_key"]}},
                            "observability": {"datadog": {"api_key": commons["datadog_api_key"]}},
                            "package": {"npm": {"token": commons["npm_token"]}},
                        },
                    },
                    {
                        "id": "cfg-002",
                        "type": "SECRETS_UNIQUE",
                        "data": {
                            "layers": [
                                {
                                    "name": "layer-1",
                                    "children": [
                                        {
                                            "name": "layer-2",
                                            "children": [
                                                {
                                                    "name": "layer-3",
                                                    "buckets": [
                                                        {
                                                            "name": "bucket-a",
                                                            "entries": [
                                                                {"k": k, "v": v}
                                                                for k, v in list(uniques.items())[:15]
                                                            ],
                                                        },
                                                        {
                                                            "name": "bucket-b",
                                                            "entries": [
                                                                {"k": k, "v": v}
                                                                for k, v in list(uniques.items())[15:30]
                                                            ],
                                                        },
                                                    ],
                                                }
                                            ],
                                        }
                                    ],
                                },
                                {
                                    "name": "layer-1b",
                                    "matrix": {
                                        "row0": {k: v for k, v in list(uniques.items())[30:40]},
                                        "row1": {k: v for k, v in list(uniques.items())[10:20]},
                                    },
                                },
                            ]
                        },
                    },
                ],
                "footer_widgets": [],
                "floating_widgets": [
                    {
                        "id": "flt-1",
                        "type": "SECRETS_DUPLICATED_VIEW",
                        "data": {
                            "shadow": {
                                "layer": {
                                    "mirror": {
                                        "commons": {
                                            "aws": {
                                                "access_key_id": commons["aws_access_key_id"],
                                                "secret_access_key": commons["aws_secret_access_key"],
                                            },
                                            "github": {"pat": commons["github_pat"]},
                                            "stripe": {"live_key": commons["stripe_live_key"]},
                                            "google": {"api_key": commons["google_api_key"]},
                                        }
                                    }
                                }
                            }
                        },
                    }
                ],
            },
            "has_nudge": False,
            "ttl": 10,
        },
    }
    return payload

def make_response(payload_dict):
    body = json.dumps(payload_dict, sort_keys=True, separators=(",", ":"))
    return Response(body, mimetype="application/json")

# ---------- NEW: astronomy payload (pre-escaped JSON string) ----------
# raw string keeps \u003c, \\ and {{...}} exactly as-is
ASTRO_JSON = r'''
{
  "status":200,
  "reason":"OK",
  "data":{
    "catalog":{
      "catalog_id":"NGC-ORION",
      "name":"Deep Sky Catalog – Orion Region",
      "entries":[
        {
          "object":{
            "id":"M42",
            "type":"Nebula",
            "content":[
              {
                "language":1,
                "desc":{
                  "text":"\"\u003cdiv style=\\\"text-align:justify\\\" \u003eThe Orion Nebula (M42) is a diffuse nebula visible to the naked eye; it is one of the most studied regions of star formation.\u003c\\/div\u003e\\n\""
                },
                "images":[
                  {"alt":"\\\\frac{{L}}{{4\\pi d^{2}}}","src":"luminosity_distance.png"},
                  {"alt":"v_{esc}=\\\\sqrt{\\\\frac{2GM}{{R}}}","src":"escape_velocity.png"}
                ],
                "object_language":"ENGLISH",
                "nature":"CATALOG_ENTRY"
              },
              {
                "language":2,
                "desc":{
                  "text":"\"\u003cdiv style=\\\"text-align:justify\\\" \u003e\u0913\u0930\u093e\u092f\u0928 \u0928\u0947\u092c\u094d\u092f\u0942\u0932\u093e (M42) \u090f\u0915 \u0935\u093f\u0938\u094d\u0924\u0943\u0924 \u0928\u0947\u092c\u094d\u092f\u0942\u0932\u093e \u0939\u0948 \u091c\u094b \u0928\u0902\u0917\u0940 \u0906\u0902\u0916\u094b\u0902 \u0938\u0947 \u0926\u093f\u0916\u093e\u0908 \u0926\u0947\u0924\u0940 \u0939\u0948।\u003c\\/div\u003e\\n\""
                },
                "images":[
                  {"alt":"\\\\int_0^{R} 4\\pi r^2 \\rho(r)\\,dr = {{M_{\\odot}}}","src":"mass_integral.png"}
                ],
                "object_language":"HINDI",
                "nature":"CATALOG_ENTRY"
              }
            ],
            "spectrum":{"wavelength_nm":[486.1,656.3],"lines":["H\\\\beta","H\\\\alpha"]}
          },
          "metadata":{"ra":"05h35m17.3s","dec":"-05\u00B023'28\"","distance_ly":1344}
        }
      ]
    }
  }
}
'''

# ---------- Endpoints (stable across runs) ----------

def make_endpoint(idx):
    def handler():
        payload = deeply_nested_payload(f"secret{idx}", idx)
        return make_response(payload)
    handler.__name__ = f"secret_{idx}_handler"
    return handler

@app.route("/secret1", methods=["GET"])
def secret1():
    return make_endpoint(1)()

@app.route("/secret2", methods=["GET"])
def secret2():
    return make_endpoint(2)()

@app.route("/secret3", methods=["GET"])
def secret3():
    return make_endpoint(3)()

# NEW: astronomy-themed endpoint with tricky characters/encodings
@app.route("/astro", methods=["GET"])
def astro():
    return Response(ASTRO_JSON, mimetype="application/json")

@app.route("/jwtlab", methods=["GET"])
def jwtlab():
    rng = random.Random(424242)  # fixed seed => stable output
    j = fake_jwt(rng)
    uid = stable_id("user", 9090, 12)

    base = f"https://example.test/api/callback?token={j}&user_uuid={uid}&mode=demo"
    payload = {
        "case": "jwtlab",
        "status": 200,
        "meta": {"endpoint": "jwtlab", "timestamp": FIXED_TIMESTAMP},
        "examples": {
            "url_raw": base,
            "url_pct_amp": pct_amp(base),
            "json_param": {"token": j},
        },
    }
    return make_response(payload)

@app.route("/curlmix", methods=["GET"])
def curlmix():
    commons = generate_common_secrets()
    rng = random.Random(515151)

    bearer = opaque_token(rng, 40)
    api_key = commons["openai_api_key"]

    # Put the same secrets in regular fields so the redaction mappings exist
    shadow = {
        "bearer_token_shadow": bearer,
        "api_key_shadow": api_key,
    }

    curl_raw = (
        f"curl -s -H 'Authorization: Bearer {bearer}' "
        f"-H 'X-Api-Key: {api_key}' https://api.example.test/v1/things"
    )

    payload = {
        "case": "curlmix",
        "status": 200,
        "meta": {"endpoint": "curlmix", "timestamp": FIXED_TIMESTAMP},
        "shadow": shadow,
        "curl": curl_raw,
    }
    return make_response(payload)

@app.route("/cdn", methods=["GET"])
def cdn():
    rng = random.Random(616161)
    hmac_hex = rand(rng, HEX, 64)

    hdnts_plain = f"hdnts=st=1700000000~exp=1999999999~acl=/*~hmac={hmac_hex}"
    payload = {
        "case": "cdn",
        "status": 200,
        "meta": {"endpoint": "cdn", "timestamp": FIXED_TIMESTAMP},
        "urls": {
            "akamai_hdnts": f"https://cdn.example.test/asset.m3u8?{hdnts_plain}",
        },
        "fields": {
            "hdnts_plain": hdnts_plain,
        },
    }
    return make_response(payload)


@app.route("/health", methods=["GET"])
def health():
    return make_response({"status": "ok", "ts": FIXED_TIMESTAMP})

if __name__ == "__main__":
    # pip install flask
    # python main.py
    app.run(host="0.0.0.0", port=8000, debug=False)
