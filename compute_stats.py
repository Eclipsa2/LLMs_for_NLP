import json
import os
import numpy as np
from pathlib import Path
import glob


def calculate_stats(perplexity_list):
    """Calculate mean, median, and std for a list of perplexity values"""
    if not perplexity_list:
        return {"mean": 0, "median": 0, "std": 0}

    return {
        "mean": float(np.mean(perplexity_list)),
        "median": float(np.median(perplexity_list)),
        "std": float(np.std(perplexity_list))
    }


def extract_perplexity_from_json(json_file_path, language_key):
    """Extract perplexity values from a JSON file for a specific language"""
    perplexity_list = []

    try:
        with open(json_file_path, "r", encoding='utf-8') as f:
            data = json.load(f)

        if language_key in data:
            for example in data[language_key]:
                if 'perplexity' in example:
                    perplexity_list.append(float(example['perplexity']))
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error processing {json_file_path}: {e}")

    return perplexity_list


def process_experiment_folder(experiment_path):
    """Process a single experiment folder and return stats"""
    experiment_stats = {}
    experiment_path = Path(experiment_path)

    print(f"Processing experiment: {experiment_path.name}")

    # Check if this is the first subfolder structure (romanian/xl folders)
    romanian_folder = experiment_path / "romanian"
    xl_folder = experiment_path / "xl"

    if romanian_folder.exists() and xl_folder.exists():
        # First subfolder structure: romanian and xl folders
        print(f"  Found romanian/xl structure")

        # Process romanian folder
        for json_file in romanian_folder.glob("*.json"):
            file_type = "content" if "content" in json_file.name else "title"
            ro_perplexity = extract_perplexity_from_json(json_file, 'ro')

            if file_type not in experiment_stats:
                experiment_stats[file_type] = {}
            experiment_stats[file_type]['ro'] = calculate_stats(ro_perplexity)

        # Process xl folder
        for json_file in xl_folder.glob("*.json"):
            file_type = "content" if "content" in json_file.name else "title"
            md_perplexity = extract_perplexity_from_json(json_file, 'md')

            if file_type not in experiment_stats:
                experiment_stats[file_type] = {}
            experiment_stats[file_type]['md'] = calculate_stats(md_perplexity)

    else:
        # Second structure: md and ro folders with numbered subfolders
        md_folder = experiment_path / "md"
        ro_folder = experiment_path / "ro"

        if md_folder.exists() and ro_folder.exists():
            print(f"  Found md/ro structure")

            # Process all numbered subfolders in md and ro
            for lang_folder, lang_key in [(md_folder, 'md'), (ro_folder, 'ro')]:
                for numbered_folder in sorted(lang_folder.glob("[0-9]*")):
                    print(f"    Processing {lang_folder.name}/{numbered_folder.name}")

                    # Process content and title files
                    for file_type in ['content', 'title']:
                        json_files = list(numbered_folder.glob(f"{file_type}*.json"))

                        for json_file in json_files:
                            perplexity_list = extract_perplexity_from_json(json_file, lang_key)

                            # Create nested structure: file_type -> subfolder -> language
                            if file_type not in experiment_stats:
                                experiment_stats[file_type] = {}
                            if numbered_folder.name not in experiment_stats[file_type]:
                                experiment_stats[file_type][numbered_folder.name] = {}

                            experiment_stats[file_type][numbered_folder.name][
                                lang_key] = calculate_stats(perplexity_list)

    return experiment_stats


def main():
    # Main script
    experiments_dir = Path("experiments")
    all_stats = {}

    if not experiments_dir.exists():
        print("Error: 'experiments' directory not found!")
        return

    # Process each experiment subfolder
    for experiment_folder in sorted(experiments_dir.iterdir()):
        if experiment_folder.is_dir():
            experiment_name = experiment_folder.name
            experiment_stats = process_experiment_folder(experiment_folder)

            if experiment_stats:
                all_stats[experiment_name] = experiment_stats
                print(f"  ✓ Processed {experiment_name}")
            else:
                print(f"  ✗ No data found in {experiment_name}")

    # Save all stats to a single JSON file
    output_file = "all_experiments_stats.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(all_stats, f, indent=4, ensure_ascii=False)

    print(f"\n✓ All statistics saved to {output_file}")

    # Print summary
    print(f"\nSummary:")
    print(f"- Processed {len(all_stats)} experiments")
    for exp_name, exp_data in all_stats.items():
        print(f"- {exp_name}: {len(exp_data)} data types")


if __name__ == "__main__":
    main()