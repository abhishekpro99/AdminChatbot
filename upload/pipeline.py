import json
import jwt
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def decode_jwt(token, token_name="JWT"):
    """
    Decodes a JWT without verifying the signature (for dev use only).
    """
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.debug(f"Decoded {token_name}: {json.dumps(decoded, indent=2)}")
        return decoded
    except Exception as e:
        logger.error(f"Failed to decode {token_name}: {e}")
        return {}

def print_azure_token(backend, response, *args, **kwargs):
    """
    Prints Azure token details in a structured format (Spring-style).
    """
    id_token = response.get('id_token')
    access_token = response.get('access_token')

    if not id_token:
        logger.warning("No ID token found in Azure response.")
        return

    decoded_id_token = decode_jwt(id_token, "ID Token")
    decoded_access_token = decode_jwt(access_token, "Access Token") if access_token else {}

    # Build Spring-style log
    username = decoded_id_token.get('preferred_username') or decoded_id_token.get('email') or decoded_id_token.get('name', 'Unknown')
    user_id = decoded_id_token.get('sub', 'UnknownSub')
    roles = decoded_id_token.get('roles', [])
    authorities = [f"SCOPE_{scope}" for scope in settings.SOCIAL_AUTH_AZUREAD_OAUTH2_SCOPE] + ["OIDC_USER"]

    log_output = (
        f"{username} Name: [{user_id}],\n"
        f"Granted Authorities: [[{', '.join(authorities)}]],\n"
        f"User Attributes: {json.dumps(decoded_id_token, indent=2)}"
    )

    print("\n" + "=" * 100)
    print(log_output)
    print("=" * 100 + "\n")

    # Optional: Save token info to session
    request = kwargs.get('request')
    if request:
        request.session['azure_id_token'] = decoded_id_token
        request.session['azure_access_token'] = decoded_access_token
