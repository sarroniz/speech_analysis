# This Python script allows the user to name/rename tiers in multiple .TextGrid files.
# You need to have the 'praatio' library installed. You can install it via pip: pip install praatio
# Change the base_directory and tier_index_mapping variables to suit your needs.
# The script will create a new folder structure with the updated .TextGrid files.
# Created by Santi Arroniz (January 2025)

import os
from praatio import textgrid

# Define the base directory containing speaker folders
base_directory = "your_base_directory" # change this
output_directory = "your_output_directory" # change this

# Create the output directory if it doesn't exist
os.makedirs(output_directory, exist_ok=True)

# Define the mapping of tier indices (0-based) to new names
# Change the values to the desired new names
tier_index_mapping = {
    0: "sentence",       # 1st tier (index 0)
    1: "words",         # 2nd tier (index 1)
    2: "syllables",    # 3rd tier (index 2)
    3: "phonemes",      # 4th tier (index 3)
    4: "interesting", # 5th tier (index 4)
}

# Walk through all subdirectories and process .TextGrid files
for root, dirs, files in os.walk(base_directory):
    for file_name in files:
        if file_name.endswith(".TextGrid"):
            # Get the relative path of the speaker folder
            relative_path = os.path.relpath(root, base_directory)
            
            # Create the corresponding output folder
            speaker_output_folder = os.path.join(output_directory, relative_path)
            os.makedirs(speaker_output_folder, exist_ok=True)
            
            # Load the TextGrid file with rename mode for duplicate (empty) names
            tg_path = os.path.join(root, file_name)
            original_tg = textgrid.openTextgrid(tg_path, includeEmptyIntervals=False, duplicateNamesMode="rename")
            
            # Create a new empty TextGrid
            new_tg = textgrid.Textgrid()
            
            # Copy each tier, renaming the specified ones
            for i, tier in enumerate(original_tg.tiers):
                # Determine the new name for the tier
                if i in tier_index_mapping:
                    new_name = tier_index_mapping[i]
                else:
                    new_name = tier.name if tier.name and not tier.name.isspace() else f"tier_{i+1}"
                
                # Check if it's an IntervalTier or PointTier and create accordingly
                if isinstance(tier, textgrid.IntervalTier):
                    entries = [(entry.start, entry.end, entry.label) for entry in tier.entries]
                    new_tier = textgrid.IntervalTier(
                        name=new_name,
                        entries=entries,
                        minT=tier.minTimestamp,
                        maxT=tier.maxTimestamp
                    )
                else:  # PointTier
                    entries = [(entry.time, entry.label) for entry in tier.entries]
                    new_tier = textgrid.PointTier(
                        name=new_name,
                        entries=entries,
                        minT=tier.minTimestamp,
                        maxT=tier.maxTimestamp
                    )
                
                new_tg.addTier(new_tier)
            
            # Save the updated TextGrid to the speaker's output folder
            output_path = os.path.join(speaker_output_folder, file_name)
            new_tg.save(output_path, format="long_textgrid", includeBlankSpaces=True)

print("Tier renaming completed. Updated files saved to:", output_directory)