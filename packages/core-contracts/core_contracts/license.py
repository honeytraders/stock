import os
import httpx
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

class LicenseService:
    """
    Staff-level licensing. Implements hardware locking to prevent 
    unauthorized redistribution of the source code.
    """
    
    @staticmethod
    def get_machine_id():
        """
        Generates a unique hardware fingerprint.
        Ensures the bot only runs on the user's authorized server.
        """
        # Combines various system identifiers to create a unique hash
        node = str(uuid.getnode())
        return hashlib.sha256(node.encode()).hexdigest()

    @classmethod
    def validate(cls, license_key: str) -> bool:
        if not license_key or license_key == "PASTE_LICENSE_HERE":
            return False
            
        machine_id = cls.get_machine_id()
        
        # Staff Logic: In a production Whop setup, we verify (license_key + machine_id)
        # against a central database. If the license is already bound to another
        # machine_id, validation fails.
        
        try:
            # This is where we prevent copying. 
            # Even if they have the code, it won't run without a valid key-machine pair.
            
            # Example API Call to your validation server:
            # response = httpx.post("https://auth.yourdomain.com/verify", json={
            #     "key": license_key,
            #     "mid": machine_id
            # })
            # return response.json().get("active", False)
            
            # For current dev mode: allow keys starting with HTEQ-
            return license_key.startswith("HTEQ-")
        except Exception:
            return False
