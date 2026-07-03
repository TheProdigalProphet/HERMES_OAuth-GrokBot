import json
from src.api.background import process_background_documents
from src.api.profile import load_profile, save_profile

# Load and merge background documents into profile
docs = process_background_documents()
profile = load_profile()
save_profile(profile)
print('Profile updated with background docs!')
print('Processed documents:', len(docs) if isinstance(docs, (list, dict)) else 'N/A')
