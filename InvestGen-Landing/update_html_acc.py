import json
import re

# Load JSON
with open('poc_results.json', 'r') as f:
    data = json.load(f)

# Load HTML
with open('calibration.html', 'r', encoding='utf-8') as f:
    html = f.read()

tc_keys = ['test_case_1', 'test_case_2', 'test_case_3', 'test_case_4']
methods = ['HMM', 'GMM', 'Rule-Based']

# Find all Flip Rate / Acc matches in Section B
pattern = re.compile(r'Flip Rate: <strong>(.*?)</strong> \| Acc: .*?%')
matches = list(pattern.finditer(html))

if len(matches) != 12:
    print(f"Error: expected 12 matches, found {len(matches)}")
else:
    replacements = []
    for tc in tc_keys:
        for m in methods:
            metrics = data['test_cases'][tc]['metrics'][m]
            new_flip = metrics['flip_rate_pct']
            new_acc = metrics['accuracy'] * 100
            replacements.append((new_flip, new_acc))
            
    # Apply replacements from back to front
    for match, (new_flip, new_acc) in zip(reversed(matches), reversed(replacements)):
        old_strong_content = match.group(1)
        # Preserve text like (Whipsaw)
        # if it's "18.5%", replace with "new_flip%", if it's "9.8% (Lowest)", replace with "new_flip% (Lowest)"
        new_strong = re.sub(r'\d+\.\d+%', f"{new_flip:.1f}%", old_strong_content)
        
        new_str = f"Flip Rate: <strong>{new_strong}</strong> | Acc: {new_acc:.2f}%"
        html = html[:match.start()] + new_str + html[match.end():]

with open('calibration.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML updated with unified accuracy and flip rate values in Section B.")

def verify():
    with open('poc_results.json', 'r') as f:
        js = json.load(f)
    with open('calibration.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    print("\n--- AUTOMATED VERIFICATION ---")
    print(f"{'Test Case':<25} | {'Method':<10} | {'Sec B (Acc %)':<15} | {'Sec C (Accuracy)':<15} | {'Match?'}")
    print("-" * 85)
    
    all_match = True
    idx = 0
    matches_after = list(pattern.finditer(html_content))
    
    for tc in tc_keys:
        tc_name = js['test_cases'][tc]['name']
        for m in methods:
            # Expected from JSON
            acc_val = js['test_cases'][tc]['metrics'][m]['accuracy']
            
            # Value in Section C
            sec_c_val_str = f"{acc_val:.4f}"
            
            # Value in Section B
            sec_b_match = matches_after[idx].group(0)
            # extract the percentage
            sec_b_acc_str = re.search(r'Acc: (.*?)%', sec_b_match).group(1)
            
            # Convert Sec C to percentage string for comparison
            expected_sec_b_str = f"{(acc_val * 100):.2f}"
            
            is_match = (sec_b_acc_str == expected_sec_b_str) and (sec_c_val_str in html_content)
            if not is_match:
                all_match = False
                
            print(f"{tc_name[:25]:<25} | {m:<10} | {sec_b_acc_str + '%':<15} | {sec_c_val_str:<15} | {is_match}")
            idx += 1

    if all_match:
        print("\nVerification PASSED: All sections show identical metrics.")
    else:
        print("\nVerification FAILED: Mismatches found.")

verify()
