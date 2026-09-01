import json
import re

# Load unified JSON
with open('poc_results.json', 'r') as f:
    data = json.load(f)

# Load existing HTML
with open('calibration.html', 'r', encoding='utf-8') as f:
    html = f.read()

tc_keys = ['test_case_1', 'test_case_2', 'test_case_3', 'test_case_4']
methods = ['HMM', 'GMM', 'Rule-Based']

# Update the legacy table (Section B) hardcoded values
# The Section B badges look like: ">Brier: 0.4927<"
brier_matches = list(re.finditer(r'>Brier: \d\.\d{4}<', html))
expected_count = 12 # 4 test cases * 3 methods
if len(brier_matches) == expected_count:
    flat_briers = []
    for tc in tc_keys:
        for m in methods:
            flat_briers.append(f">Brier: {data['test_cases'][tc]['metrics'][m]['brier_score']:.4f}<")
    
    # Replace from back to front to preserve indices
    for match, new_val in zip(reversed(brier_matches), reversed(flat_briers)):
        html = html[:match.start()] + new_val + html[match.end():]
else:
    print(f"ERROR: Expected 12 matches for >Brier:, found {len(brier_matches)}")

with open('calibration.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML successfully updated and aligned with unified poc_results.json.")

def verify():
    # Load JSON
    with open('poc_results.json', 'r') as f:
        js = json.load(f)
        
    with open('calibration.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    mismatches = 0
    print("\n--- AUTOMATED VERIFICATION ---")
    for tc in tc_keys:
        for m in methods:
            brier = f"{js['test_cases'][tc]['metrics'][m]['brier_score']:.4f}"
            acc = f"{js['test_cases'][tc]['metrics'][m]['accuracy']:.4f}"
            
            # Check Extended table (Section C)
            if acc not in html_content:
                print(f"Mismatch: Section C missing Accuracy {acc} for {m} in {tc}")
                mismatches += 1
            if brier not in html_content:
                print(f"Mismatch: Section C missing Brier {brier} for {m} in {tc}")
                mismatches += 1
                
            # Check Legacy table (Section B)
            if f">Brier: {brier}<" not in html_content:
                print(f"Mismatch: Section B missing '>Brier: {brier}<' for {m} in {tc}")
                mismatches += 1
                
    print(f"Total Mismatches Found: {mismatches}")
    if mismatches == 0:
        print("Verification PASSED: All sections show identical metrics.")

verify()
