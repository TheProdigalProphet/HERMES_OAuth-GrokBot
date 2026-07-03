#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from api.background import load_all_documents, update_profile_from_document
from api.profile import load_profile, save_profile

print("🔄 Processing background documents for reunification profile...")

docs = load_all_documents()
print(f"Loaded {len(docs)} background documents from data/background/")

profile = load_profile()
print(f"Loaded profile for: {profile.name or 'Will Power (Leo David Power reunification)'}")

for doc in docs:
    update_profile_from_document(profile, doc)
    print(f"  ✓ Incorporated: {doc.title} ({doc.category})")

save_profile(profile)
print("\n✅ Profile successfully updated with all background documents!")
print("Profile saved to data/user_profile.json")
print("\nKey updates include experiences, career goals, and summary statements for the Care and Protection Order case.")
