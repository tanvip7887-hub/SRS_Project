import subprocess
import sys

def run_script(script_name):
    print(f"\n🚀 Running {script_name}...\n")

    result = subprocess.run(
        [sys.executable, script_name],
        text=True
    )

    if result.returncode != 0:
        print(f"\n❌ Error in {script_name}. Stopping pipeline.")
        sys.exit(1)

    print(f"\n✅ Finished {script_name}")

# ---------------------------
# MAIN PIPELINE
# ---------------------------

if __name__ == "__main__":

    print("\n==============================")
    print(" SRS ANALYZER PIPELINE START ")
    print("==============================\n")

    run_script("main.py")                  # Extraction
    run_script("detect_duplicates.py")     # Duplicate Detection
    run_script("detect_ambiguity.py")      # Ambiguity Detection
    run_script("annotate_srs.py")   
    run_script("remove_duplicates.py")# Annotation

    print("\n==============================")
    print(" 🎉 PIPELINE COMPLETED ")
    print("==============================")
